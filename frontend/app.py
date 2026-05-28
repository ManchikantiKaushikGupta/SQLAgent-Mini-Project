import streamlit as st
import requests
import pandas as pd
from typing import Any, Dict

API_URL = "http://localhost:8000/api/v1/ask"

# 1. Page Configuration
st.set_page_config(page_title="DataSense AI - Telemetry Portal", page_icon="📊", layout="wide")

# 2. Custom Sleek CSS for Modern AI Look (Glows, glassmorphism, no headers)
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
            background-color: #1a1c24;
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            border: 1px solid #2d313f;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 1.1rem;
            font-weight: 600;
            color: #8f95b2;
        }
        .stTabs [data-baseweb="tab"]:hover {
            color: #ffffff;
        }
        .stTabs [aria-selected="true"] {
            color: #4f46e5 !important;
            border-bottom-color: #4f46e5 !important;
        }
        .kpi-card {
            background-color: #161821;
            border: 1px solid #252836;
            padding: 1.2rem;
            border-radius: 0.5rem;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# 3. Sidebar
with st.sidebar:
    st.title("💡 DataSense AI")
    st.markdown("Navigate and query your enterprise database using natural language.")
    st.divider()
    
    st.markdown("### 💬 Example Queries")
    st.info("Show the top 3 users by total order amount, ordered descending")
    st.info("Get all reviews for Laptop Model B2")
    st.info("Which category department has the highest number of products?")
    
    st.divider()
    st.markdown("### 📊 Observability Specs")
    st.caption("- **Orchestration**: LangGraph")
    st.caption("- **Retrieval**: FAISS (`IndexFlatIP`)")
    st.caption("- **LLM Engine**: Gemini 3.5 Flash")
    st.caption("- **Telemetry**: In-Memory + Disk Cache")

# 4. Main App Layout - Setup Tabs
st.title("DataSense AI Telemetry Portal")
st.markdown("Ask natural language questions to analyze database schemas and monitor step diagnostics in real-time.")

tab_chat, tab_obs = st.tabs(["💬 Chat Workspace", "📊 Observability Dashboard"])

# Setup session state metrics
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your AI SQL Agent. Ask me any analytical question, and I'll generate the query plan, prune the schema via FAISS, write the SQL, and display live metrics diagnostics!"}
    ]

if "last_metrics" not in st.session_state:
    st.session_state.last_metrics = None

# ---------------------------------------------------------------------------
# TAB 1: Chat Workspace
# ---------------------------------------------------------------------------
with tab_chat:
    # Render Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="✨" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])
            
            # If assistant returned structured data, render SQL and table
            if msg["role"] == "assistant" and "data" in msg:
                data = msg["data"]
                sql = data.get("sql_query")
                results = data.get("results")
                error_msg = data.get("error")
                
                with st.expander("🛠️ View SQL Statement"):
                    st.code(sql if sql else "-- No SQL query returned", language="sql")
                    if error_msg:
                        st.error(error_msg)
                        
                if results:
                    st.dataframe(pd.DataFrame(results), use_container_width=True)

    # Chat Input
    if prompt := st.chat_input("Ask a question (e.g., Get top 3 spending users)..."):
        # Append User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # Generate Assistant Response
        with st.chat_message("assistant", avatar="✨"):
            with st.spinner("Analyzing schema and generating optimized SQL..."):
                try:
                    response = requests.post(API_URL, json={"query": prompt})
                    response.raise_for_status()
                    data = response.json()
                    
                    error_msg = data.get("error")
                    sql = data.get("sql_query")
                    results = data.get("results")

                    # Log telemetries globally to session state for Dashboard tab
                    st.session_state.last_metrics = data

                    if error_msg:
                        answer_text = "I encountered an error trying to process that query. Please see the details below."
                    elif results is not None:
                        answer_text = f"Here is the data you requested! Found {len(results)} records."
                    else:
                        answer_text = "I processed your query, but no records were returned from the database."

                    st.markdown(answer_text)

                    # Show SQL expander
                    with st.expander("🛠️ View SQL Statement"):
                        st.code(sql if sql else "-- No SQL generated", language="sql")
                        if error_msg:
                            st.error(error_msg)

                    # Show table
                    if results:
                        st.dataframe(pd.DataFrame(results), use_container_width=True)

                    # Save message
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer_text,
                        "data": data
                    })

                except requests.exceptions.RequestException as e:
                    error_text = f"An API connection error occurred: {e}"
                    st.error(error_text)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_text
                    })


# ---------------------------------------------------------------------------
# TAB 2: Observability Dashboard
# ---------------------------------------------------------------------------
with tab_obs:
    st.subheader("🛠️ Run Diagnostics & Execution Telemetries")
    
    if st.session_state.last_metrics is None:
        st.info("💡 **No Active Telemetry**: Please execute a query inside the **Chat Workspace** to view live performance telemetries.")
        
        st.divider()
        st.markdown("### 🚀 Telemetry Metrics Tracked in Real-Time")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### ⏱️ Stage-wise Latency Timeline")
            st.caption("Logs step duration in seconds for Intent Clarification, FAISS Schema Retrieval, Query Planning, SQL Generation, and DB execution.")
            st.markdown("#### 🗺️ Structural Query Plan")
            st.caption("Exposes which tables, joins, filters, aggregations, groupings, orderings, and limits were mapped by the Query Planner.")
        with c2:
            st.markdown("#### 🛡️ Validation & Corrective Trails")
            st.caption("Exposes safety parsing audits (via SQLGlot AST constraints) and semantic validation, alongside chronological SQL repair loops.")
            st.markdown("#### 💸 LLM Token Consumption")
            st.caption("Tracks input and output token counts thread-safely across all generative agents during the workflow execution.")
    else:
        payload = st.session_state.last_metrics
        metrics = payload.get("metrics", {})
        
        # 1. KPI Panel
        latencies = metrics.get("latency", {})
        total_latency = sum(latencies.values()) if latencies else 0.0
        
        tokens = metrics.get("tokens", {})
        total_tokens = tokens.get("total_tokens", 0)
        prompt_tokens = tokens.get("prompt_tokens", 0)
        comp_tokens = tokens.get("completion_tokens", 0)
        
        history = metrics.get("correction_history", [])
        repair_attempts = len(history)

        st.markdown("### 📈 Key Performance Indicators (KPIs)")
        kpi_cols = st.columns(5)
        
        with kpi_cols[0]:
            st.markdown(f"<div class='kpi-card'><p style='color:#8f95b2;margin:0;'>Total Latency</p><h2 style='margin:0.2rem 0;'>{total_latency:.2f} s</h2></div>", unsafe_allow_html=True)
        with kpi_cols[1]:
            st.markdown(f"<div class='kpi-card'><p style='color:#8f95b2;margin:0;'>Total Tokens</p><h2 style='margin:0.2rem 0;'>{total_tokens:,}</h2></div>", unsafe_allow_html=True)
        with kpi_cols[2]:
            st.markdown(f"<div class='kpi-card'><p style='color:#8f95b2;margin:0;'>Prompt Tokens</p><h2 style='margin:0.2rem 0;'>{prompt_tokens:,}</h2></div>", unsafe_allow_html=True)
        with kpi_cols[3]:
            st.markdown(f"<div class='kpi-card'><p style='color:#8f95b2;margin:0;'>Completion Tokens</p><h2 style='margin:0.2rem 0;'>{comp_tokens:,}</h2></div>", unsafe_allow_html=True)
        with kpi_cols[4]:
            st.markdown(f"<div class='kpi-card'><p style='color:#8f95b2;margin:0;'>Repair Attempts</p><h2 style='margin:0.2rem 0;'>{repair_attempts}</h2></div>", unsafe_allow_html=True)

        st.divider()

        # 2. Stage Latency Chart & Token Consumption side-by-side
        g1, g2 = st.columns([3, 2])
        with g1:
            st.markdown("#### ⏱️ Stage-wise Latency Timeline")
            if latencies:
                df_lat = pd.DataFrame([
                    {"Stage": k.replace("_", " ").title(), "Duration (s)": v}
                    for k, v in latencies.items()
                ])
                st.bar_chart(df_lat, x="Stage", y="Duration (s)", horizontal=True, use_container_width=True)
            else:
                st.warning("No stage-wise latency tracked.")
                
        with g2:
            st.markdown("#### 💸 Token Usage Breakdown")
            if total_tokens > 0:
                df_tok = pd.DataFrame({
                    "Token Type": ["Prompt Input Tokens", "Completion Output Tokens"],
                    "Count": [prompt_tokens, comp_tokens]
                })
                st.dataframe(df_tok, hide_index=True, use_container_width=True)
            else:
                st.caption("Bypassed LLM calling (all responses generated from in-memory cache).")

        st.divider()

        # 3. Query Planner & FAISS Diagnostics
        d1, d2 = st.columns(2)
        with d1:
            st.markdown("#### 🗺️ Structural Query Plan (Planner Output)")
            plan_data = metrics.get("query_plan")
            if plan_data:
                st.caption(f"**Thought Process:** {plan_data.get('thought_process', 'N/A')}")
                
                # Tables
                tables = plan_data.get("tables", [])
                st.markdown("**Required Tables:**")
                if tables:
                    for t in tables:
                        st.markdown(f"- `{t.get('table_name')}`: *{t.get('purpose')}*")
                else:
                    st.caption("- None required")
                    
                # Joins
                joins = plan_data.get("joins", [])
                st.markdown("**JOIN Requirements:**")
                if joins:
                    for j in joins:
                        st.markdown(f"- `{j.get('left_table')}` ↔ `{j.get('right_table')}` ({j.get('join_type', 'INNER')}) on `{j.get('on_condition')}`")
                else:
                    st.caption("- None required")
                    
                # Filters
                filters = plan_data.get("filters", [])
                st.markdown("**Filters (WHERE constraints):**")
                if filters:
                    for f in filters:
                        st.markdown(f"- `{f.get('column')}` `{f.get('operator')}` `'{f.get('value')}'`")
                else:
                    st.caption("- None required")
            else:
                st.info("No query planning data present in metrics context.")
                
        with d2:
            st.markdown("#### 🛡️ Dynamic Schema Retrieval Audits")
            if latencies.get("schema_retrieval") is not None:
                st.success("✅ **FAISS Pruning Active**")
                st.markdown(f"**FAISS Latency:** `{latencies.get('schema_retrieval'):.3f} s`")
                st.markdown("**Search Algorithm:** Unit Cosine Similarity (`faiss.IndexFlatIP`)")
                st.markdown("**Embedding Model:** `models/gemini-embedding-2` (3,072 dims)")
                st.markdown("**PK/FK Safety Guard:** Enabled (Primary and Foreign Keys strictly preserved)")
                
                # Render pruned schema character count comparison
                full_len = 891 # default reflected E-Commerce schema chars size
                pruned_len = len(payload.get("db_schema", ""))
                reduction = ((full_len - pruned_len) / full_len) * 100
                st.markdown(f"**Schema Length Reduction:** `{reduction:.1f}%` (from {full_len} down to {pruned_len} characters)")
            else:
                st.caption("FAISS indices search skipped.")

        st.divider()

        # 4. SQL Statement & Validation Audits
        st.markdown("#### 💻 Generated SQL Query & Validations")
        st.code(payload.get("sql_query", "-- No SQL generated"), language="sql")
        
        exec_meta = metrics.get("execution", {})
        val_syntax = metrics.get("validation", {}).get("syntax", {})
        val_sem = metrics.get("validation", {}).get("semantic", {})
        
        col_v1, col_v2, col_v3 = st.columns(3)
        with col_v1:
            st.markdown("**Database Execution:**")
            if exec_meta.get("success") is True:
                st.success(f"✅ Successful ({exec_meta.get('row_count', 0)} rows returned)")
            elif exec_meta.get("success") is False:
                st.error(f"❌ Failed: {exec_meta.get('error')}")
            else:
                st.caption("Bypassed or did not execute.")
                
        with col_v2:
            st.markdown("**AST Safety & Syntax Audit:**")
            if val_syntax:
                if val_syntax.get("is_valid") is True:
                    st.success("✅ Passed Verification")
                else:
                    st.error(f"❌ Safety Violation: {val_syntax.get('reason')}")
            else:
                st.caption("Bypassed.")
                
        with col_v3:
            st.markdown("**Semantic Correctness Audit:**")
            if val_sem:
                if val_sem.get("is_valid") is True:
                    st.success("✅ Passed Intent-Match")
                else:
                    st.error(f"❌ Semantic Mismatch: {val_sem.get('reason')}")
            else:
                st.caption("Bypassed.")

        # 5. Correction loops
        if history:
            st.divider()
            st.markdown("#### 🔧 AST SQL Correction & Repair Trails")
            for item in history:
                with st.expander(f"🛠️ Attempt {item.get('attempt')} - logged at: {item.get('timestamp')}"):
                    st.markdown("**Failed SQL Query:**")
                    st.code(item.get("failed_sql"), language="sql")
                    st.markdown("**Validation / Database Compiler Error:**")
                    st.error(item.get("error_message"))
                    
                    thought = item.get("thought_process")
                    if thought:
                        st.info(f"💡 **Repair Reasoning:** {thought}")
                        
                    st.markdown("**Surgically Corrected Query (AST Patch):**")
                    st.code(item.get("corrected_sql"), language="sql")

