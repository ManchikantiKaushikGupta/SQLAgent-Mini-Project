"""
Production Governance and Security Module

Implements Role-Based Access Control (RBAC) at table/column levels,
PII detection/redaction on inputs, SQL query result masking,
SQL AST-based validation, LIMIT clamping via SQLGlot, and JSON audit logging.
"""

import re
import os
import json
import time
import logging
from typing import Dict, List, Set, Any, Optional
from pydantic import BaseModel, Field, field_validator
import sqlglot
import sqlglot.expressions as exp

logger = logging.getLogger("SQLAgent.Security")
logger.setLevel(logging.INFO)

class SecurityException(Exception):
    """Exception raised when a security policy or validation check is violated."""
    pass

class RolePermissions(BaseModel):
    """
    Pydantic model representing access permissions for a specific role.
    """
    role: str = Field(..., description="The unique name of the role (e.g. admin, analyst)")
    allowed_tables: Set[str] = Field(default_factory=set, description="Set of tables this role is allowed to access. Use {'*'} for all tables.")
    allowed_columns: Dict[str, Set[str]] = Field(default_factory=dict, description="Mapping of table -> allowed columns. Empty or '*' values mean all columns of allowed tables.")
    denied_columns: Dict[str, Set[str]] = Field(default_factory=dict, description="Mapping of table -> explicitly denied columns.")
    can_view_pii: bool = Field(False, description="Whether this role is allowed to view PII columns unredacted.")
    max_limit: int = Field(100, description="The maximum allowed SELECT query LIMIT value.")

    @field_validator("role")
    @classmethod
    def normalize_role_name(cls, v: str) -> str:
        return v.lower().strip()


class SecurityConfig(BaseModel):
    """
    Pydantic model representing the global enterprise security policy configuration.
    """
    roles: Dict[str, RolePermissions] = Field(default_factory=dict, description="Configuration for all system roles.")
    pii_columns: Dict[str, List[str]] = Field(default_factory=dict, description="Mapping of table -> columns containing PII.")
    default_role: str = Field("restricted_user", description="Default role enforced if none is specified.")

    @classmethod
    def get_default_config(cls) -> "SecurityConfig":
        """
        Generates the standard out-of-the-box enterprise security policy.
        """
        admin_perms = RolePermissions(
            role="admin",
            allowed_tables={"*"},
            allowed_columns={},
            denied_columns={},
            can_view_pii=True,
            max_limit=1000
        )
        
        manager_perms = RolePermissions(
            role="manager",
            allowed_tables={"*"},
            allowed_columns={},
            denied_columns={},
            can_view_pii=False,
            max_limit=500
        )
        
        analyst_perms = RolePermissions(
            role="analyst",
            allowed_tables={"*"},
            allowed_columns={},
            denied_columns={
                "users": {"email", "first_name", "last_name"}
            },
            can_view_pii=False,
            max_limit=200
        )
        
        restricted_perms = RolePermissions(
            role="restricted_user",
            allowed_tables={"products", "categories", "reviews"},
            allowed_columns={},
            denied_columns={},
            can_view_pii=False,
            max_limit=50
        )

        pii_mapping = {
            "users": ["email", "first_name", "last_name"]
        }

        return cls(
            roles={
                "admin": admin_perms,
                "manager": manager_perms,
                "analyst": analyst_perms,
                "restricted_user": restricted_perms
            },
            pii_columns=pii_mapping,
            default_role="restricted_user"
        )


class PIIRedactor:
    """
    Handles regex-based scanning and redaction of PII from user inputs,
    along with value-level masking on execution results.
    """
    def __init__(self, pii_columns: Dict[str, List[str]]):
        self.pii_columns = pii_columns
        # Common PII Regexes
        self.email_regex = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
        self.phone_regex = re.compile(r"\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}")

    def redact_text(self, text: str) -> str:
        """
        Redacts highly sensitive patterns like emails and phone numbers from user questions.
        """
        if not text:
            return text
        redacted = self.email_regex.sub("<EMAIL>", text)
        redacted = self.phone_regex.sub("<PHONE_NUMBER>", redacted)
        if redacted != text:
            logger.info("PII detected and redacted from user input query.")
        return redacted

    def mask_value(self, column_name: str, value: Any) -> Any:
        """
        Masks/redacts a specific PII data cell value according to its column type.
        """
        if value is None:
            return None
        
        val_str = str(value).strip()
        if not val_str:
            return value

        col_lower = column_name.lower()
        if "email" in col_lower:
            parts = val_str.split("@")
            if len(parts) == 2:
                local, domain = parts
                masked_local = local[0] + "****" if len(local) > 1 else "****"
                return f"{masked_local}@{domain}"
            return "******@example.com"
        elif "first_name" in col_lower or "last_name" in col_lower or "name" in col_lower:
            return val_str[0] + "***" if len(val_str) > 1 else "***"
        
        return "[REDACTED]"

    def redact_results(self, results: List[Dict[str, Any]], role_perms: RolePermissions) -> List[Dict[str, Any]]:
        """
        Scans execution rows and masks values in columns that are registered as PII 
        if the executing role is not authorized to view raw PII.
        """
        if role_perms.can_view_pii or not results:
            return results

        redacted_results = []
        for row in results:
            new_row = {}
            for col_name, col_val in row.items():
                is_pii = False
                # Check if this column is marked as PII in any table
                for table_name, pii_cols in self.pii_columns.items():
                    if col_name.lower() in [c.lower() for c in pii_cols]:
                        is_pii = True
                        break
                
                if is_pii:
                    new_row[col_name] = self.mask_value(col_name, col_val)
                else:
                    new_row[col_name] = col_val
            redacted_results.append(new_row)
            
        return redacted_results


class AuditLogger:
    """
    Appends structured JSON logs representing security actions, 
    verifications, and governance events to the enterprise log file.
    """
    def __init__(self, log_file: str = "observability/audit_log.json"):
        self.log_file = os.path.abspath(log_file)
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

    def log_event(self, action: str, role: str, username: Optional[str], details: Dict[str, Any]) -> None:
        """
        Writes a structured JSON audit record to the persistent log.
        """
        payload = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S+05:30"),
            "action": action,
            "role": role,
            "username": username or "anonymous",
            "details": details
        }
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(payload) + "\n")
        except Exception as e:
            logger.error(f"Failed to write to audit log: {e}")


class SecurityManager:
    """
    Global coordinator for database governance, RBAC enforcement, PII scrubbing, 
    and policy compliance.
    """
    _instance: Optional["SecurityManager"] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> "SecurityManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_manager()
        return cls._instance

    def _init_manager(self) -> None:
        self.config = SecurityConfig.get_default_config()
        self.redactor = PIIRedactor(self.config.pii_columns)
        self.audit_logger = AuditLogger()

    def get_role_permissions(self, role_name: Optional[str]) -> RolePermissions:
        """
        Fetches the permissions mapping for a given role, falling back securely.
        """
        if not role_name:
            role_name = self.config.default_role
        
        normalized = role_name.lower().strip()
        if normalized not in self.config.roles:
            logger.warning(f"Unknown role '{role_name}' requested. Falling back to default secure role: '{self.config.default_role}'")
            return self.config.roles[self.config.default_role]
            
        return self.config.roles[normalized]

    def prune_schema_for_role(self, schema_text: str, role_name: Optional[str]) -> str:
        """
        Removes unauthorized tables and columns from the database schema context.
        This shields the LLM planning agent from discovering unauthorized objects.
        """
        perms = self.get_role_permissions(role_name)
        if not schema_text or schema_text == "No tables found in the database.":
            return schema_text

        # If admin, return complete schema
        if "*" in perms.allowed_tables and not perms.denied_columns:
            return schema_text

        pruned_blocks = []
        # Table blocks are separated by empty lines, beginning with 'Table: name'
        table_blocks = schema_text.strip().split("\n\n")
        
        for block in table_blocks:
            lines = block.strip().split("\n")
            if not lines:
                continue
            
            header = lines[0]
            if not header.startswith("Table: "):
                # Fallback if text format is slightly different
                pruned_blocks.append(block)
                continue
                
            table_name = header.replace("Table: ", "").strip()
            
            # Check Table permission
            if "*" not in perms.allowed_tables and table_name not in perms.allowed_tables:
                continue # Role not allowed to see this table at all
                
            # Check Column permissions
            table_denied_cols = perms.denied_columns.get(table_name, set())
            table_allowed_cols = perms.allowed_columns.get(table_name, set())
            
            pruned_lines = [header]
            for col_line in lines[1:]:
                # Extract column name from line like "  - name (type) [flags]"
                match = re.match(r"\s*-\s*([a-zA-Z0-9_]+)", col_line)
                if not match:
                    pruned_lines.append(col_line)
                    continue
                    
                col_name = match.group(1)
                
                # Check if column is explicitly denied
                if col_name in table_denied_cols:
                    continue
                    
                # Check if column is not in allowed list (if allowed list is specified and not empty)
                if table_allowed_cols and col_name not in table_allowed_cols:
                    continue
                    
                pruned_lines.append(col_line)
                
            if len(pruned_lines) > 1: # Only include table if columns remain
                pruned_blocks.append("\n".join(pruned_lines))
                
        if not pruned_blocks:
            return "No tables available in the database schema under the current role permissions."
            
        return "\n\n".join(pruned_blocks)

    def validate_sql_security(self, sql: str, role_name: Optional[str], username: Optional[str] = None) -> str:
        """
        Parses generated SQL, performs static AST verification for RBAC,
        prevents system tables access, and surgically injects/clamps LIMIT clauses.
        
        Raises:
            SecurityException: If any governance policy or restriction is violated.
        Returns:
            The safe, potentially modified/clamped SQL query string.
        """
        perms = self.get_role_permissions(role_name)
        
        if not sql or not sql.strip():
            raise SecurityException("Empty SQL query provided.")

        try:
            parsed_statements = sqlglot.parse(sql, read="postgres")
        except Exception as e:
            # Re-parse with generic dialect if postgres fails to parse perfectly
            try:
                parsed_statements = sqlglot.parse(sql)
            except Exception as parse_err:
                self.audit_logger.log_event(
                    action="security_violation",
                    role=perms.role,
                    username=username,
                    details={"sql": sql, "error": f"Failed to parse SQL: {parse_err}"}
                )
                raise SecurityException(f"SQL Syntax Error: Could not parse query. Detail: {parse_err}")

        if not parsed_statements:
            raise SecurityException("Empty SQL query provided.")

        if len(parsed_statements) > 1:
            self.audit_logger.log_event(
                action="security_violation",
                role=perms.role,
                username=username,
                details={"sql": sql, "error": "Multiple statements detected"}
            )
            raise SecurityException("Security Violation: Multiple SQL statements are strictly unauthorized.")

        stmt = parsed_statements[0]
        if stmt is None:
            raise SecurityException("Empty SQL query provided.")

        # 1. Enforce SELECT statements only
        if not isinstance(stmt, exp.Select):
            self.audit_logger.log_event(
                action="security_violation",
                role=perms.role,
                username=username,
                details={"sql": sql, "error": f"Statement type {type(stmt).__name__} not allowed"}
            )
            raise SecurityException(
                f"Security Violation: Unsafe or unauthorized SQL statement detected: {type(stmt).__name__}. "
                "Only SELECT statements are allowed."
            )

        # 2. Extract and inspect tables
        tables_accessed = []
        for table_node in stmt.find_all(exp.Table):
            table_name = table_node.name.lower().strip()
            tables_accessed.append(table_name)
            
            # Prevent accessing metadata/system tables
            if table_name.startswith("sqlite_") or table_name.startswith("pg_") or "information_schema" in table_name:
                self.audit_logger.log_event(
                    action="security_violation",
                    role=perms.role,
                    username=username,
                    details={"sql": sql, "error": f"Metadata table access: '{table_name}'"}
                )
                raise SecurityException(f"Security Violation: Database metadata table access is forbidden: '{table_name}'.")

            # Check table authorization
            if "*" not in perms.allowed_tables and table_name not in perms.allowed_tables:
                self.audit_logger.log_event(
                    action="security_violation",
                    role=perms.role,
                    username=username,
                    details={"sql": sql, "error": f"Unauthorized table access: '{table_name}'"}
                )
                raise SecurityException(f"Security Violation: Unauthorized table access. Role '{perms.role}' is not allowed to query '{table_name}'.")

        # 3. Extract and inspect columns
        for col_node in stmt.find_all(exp.Column):
            col_name = col_node.name.lower().strip()
            
            # Check table prefix if available
            col_table = col_node.text("table").lower().strip()
            
            if col_table:
                # If table prefix matches a restricted column
                table_denied = perms.denied_columns.get(col_table, set())
                if col_name in [c.lower() for c in table_denied]:
                    self.audit_logger.log_event(
                        action="security_violation",
                        role=perms.role,
                        username=username,
                        details={"sql": sql, "error": f"Unauthorized column access: '{col_table}.{col_name}'"}
                    )
                    raise SecurityException(f"Security Violation: Unauthorized column access. Role '{perms.role}' is not allowed to query column '{col_table}.{col_name}'.")
            else:
                # No table prefix. Check if the column is restricted in ANY of the accessed tables.
                # If it's a restricted column in any table, reject to prevent evasion.
                for t in tables_accessed:
                    table_denied = perms.denied_columns.get(t, set())
                    if col_name in [c.lower() for c in table_denied]:
                        self.audit_logger.log_event(
                            action="security_violation",
                            role=perms.role,
                            username=username,
                            details={"sql": sql, "error": f"Implicit unauthorized column access: '{col_name}' in table '{t}'"}
                        )
                        raise SecurityException(f"Security Violation: Unauthorized column access. Role '{perms.role}' is not allowed to query column '{col_name}'.")

        # 3.1 Inspect for exp.Star queries to prevent exposure of restricted columns
        for star_node in stmt.find_all(exp.Star):
            for table_name in tables_accessed:
                if perms.denied_columns.get(table_name):
                    self.audit_logger.log_event(
                        action="security_violation",
                        role=perms.role,
                        username=username,
                        details={"sql": sql, "error": f"Star query matches denied columns in table '{table_name}'"}
                    )
                    raise SecurityException(
                        f"Security Violation: SELECT * is not allowed on table '{table_name}' "
                        f"because some columns are restricted for role '{perms.role}'. Please specify columns explicitly."
                    )

        # 4. Enforce LIMIT constraints
        limit_node = stmt.find(exp.Limit)
        if limit_node:
            try:
                # Parse current limit value
                current_limit = int(limit_node.expression.this)
                if current_limit > perms.max_limit:
                    logger.warning(f"Enforcing LIMIT clamp: {current_limit} -> {perms.max_limit} for role '{perms.role}'")
                    # Rewrite the limit expression in the AST
                    limit_node.set("expression", exp.Literal.number(perms.max_limit))
            except Exception as e:
                logger.warning(f"Failed to parse SQL LIMIT expression: {e}. Enforcing default limit.")
                limit_node.set("expression", exp.Literal.number(perms.max_limit))
        else:
            # Inject LIMIT clause
            logger.info(f"No LIMIT clause found. Injecting default LIMIT {perms.max_limit} for role '{perms.role}'")
            stmt = stmt.limit(perms.max_limit)

        safe_sql = stmt.sql(dialect="postgres")
        
        # Log successful security check
        self.audit_logger.log_event(
            action="sql_validation_passed",
            role=perms.role,
            username=username,
            details={"original_sql": sql, "safe_sql": safe_sql}
        )
        
        return safe_sql


def get_security_manager() -> SecurityManager:
    """Returns the global SecurityManager singleton instance."""
    return SecurityManager()
