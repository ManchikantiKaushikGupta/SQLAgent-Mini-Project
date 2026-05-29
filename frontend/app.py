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

tab_chat, tab_obs, tab_bench = st.tabs(["💬 Chat Workspace", "📊 Observability Dashboard", "📈 Benchmark Analytics"])

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


# ---------------------------------------------------------------------------
# TAB 3: Benchmark Analytics
# ---------------------------------------------------------------------------
with tab_bench:
    import os
    import json

    st.subheader("📈 Multi-Dataset NL2SQL Benchmark Analytics")
    st.markdown("Monitor historical execution metrics, failure taxonomy diagnostic breakdowns, latency distributions, and token API cost metrics.")

    # 1. Dataset Selection
    dataset_options = {
        "Baseline E-Commerce": "run_history.json",
        "Spider": "run_history_spider.json",
        "Spider Realistic": "run_history_spider_realistic.json",
        "Spider SYN": "run_history_spider_syn.json"
    }

    selected_dataset = st.selectbox("🎯 Select Evaluation Target Benchmark:", list(dataset_options.keys()))
    file_name = dataset_options[selected_dataset]

    eval_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "evaluation"))
    file_path = os.path.join(eval_dir, file_name)

    if not os.path.exists(file_path):
        st.info(f"💡 **No Benchmark Run Log Found**: Run the evaluations via `python evaluation/expanded_runner.py --dataset {selected_dataset.lower().replace(' ', '_')}` (or `python evaluation/benchmark_runner.py` for Baseline) to generate metrics telemetry.")
    else:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                history_data = json.load(f)

            if not history_data:
                st.warning("The run history file exists but has no records.")
            else:
                # Get the most recent run
                latest_run = history_data[0]
                summary = latest_run.get("summary", {})
                results = latest_run.get("results", [])

                # Render run metadata
                st.markdown(f"#### 🏷️ Latest Run ID: `{summary.get('run_id', 'N/A')}` | Timestamp: `{summary.get('timestamp', 'N/A')}`")

                # --- KPI Metrics Panel ---
                acc = summary.get("execution_accuracy_pct", 0.0)
                passed = summary.get("passed_cases", 0)
                total = summary.get("total_cases", 0)
                avg_lat = summary.get("average_latency_seconds", 0.0)
                avg_tok = summary.get("avg_tokens_per_query", 0.0)
                tot_tok = summary.get("total_tokens", 0)

                # Cost estimation for Gemini 3.5 Flash:
                # Input tokens: $0.075 per 1,000,000 tokens ($0.000000075 per token)
                # Output tokens: $0.30 per 1,000,000 tokens ($0.00000030 per token)
                total_cost = 0.0
                for r in results:
                    p_tok = r.get("prompt_tokens", 0)
                    c_tok = r.get("completion_tokens", 0)
                    total_cost += (p_tok * 0.000000075) + (c_tok * 0.00000030)

                kpi_cols = st.columns(5)

                with kpi_cols[0]:
                    accuracy_str = f"{acc:.1f}%"
                    st.markdown(f"<div class='kpi-card'><p style='color:#8f95b2;margin:0;'>Execution Accuracy</p><h2 style='margin:0.2rem 0;color:#10b981;'>{accuracy_str}</h2><p style='color:#8f95b2;margin:0;'>{passed} / {total} cases</p></div>", unsafe_allow_html=True)
                with kpi_cols[1]:
                    st.markdown(f"<div class='kpi-card'><p style='color:#8f95b2;margin:0;'>Avg Latency</p><h2 style='margin:0.2rem 0;'>{avg_lat:.2f} s</h2><p style='color:#8f95b2;margin:0;'>per NL Query</p></div>", unsafe_allow_html=True)
                with kpi_cols[2]:
                    st.markdown(f"<div class='kpi-card'><p style='color:#8f95b2;margin:0;'>Avg Token Size</p><h2 style='margin:0.2rem 0;'>{avg_tok:,.0f}</h2><p style='color:#8f95b2;margin:0;'>tokens / query</p></div>", unsafe_allow_html=True)
                with kpi_cols[3]:
                    st.markdown(f"<div class='kpi-card'><p style='color:#8f95b2;margin:0;'>Run API Cost</p><h2 style='margin:0.2rem 0;color:#3b82f6;'>${total_cost:.5f}</h2><p style='color:#8f95b2;margin:0;'>for {total} queries</p></div>", unsafe_allow_html=True)
                with kpi_cols[4]:
                    corr_success = summary.get("correction_success_rate_pct", 0.0)
                    corr_passed = summary.get("queries_corrected_successfully", 0)
                    corr_total = summary.get("queries_needing_correction", 0)
                    st.markdown(f"<div class='kpi-card'><p style='color:#8f95b2;margin:0;'>Correction Rate</p><h2 style='margin:0.2rem 0;'>{corr_success:.1f}%</h2><p style='color:#8f95b2;margin:0;'>{corr_passed} / {corr_total} repaired</p></div>", unsafe_allow_html=True)

                st.divider()

                # --- Views Section ---
                col_left, col_right = st.columns(2)

                with col_left:
                    # View 1: Execution Accuracy & Difficulty Breakdown
                    st.markdown("#### 🏆 Execution Accuracy by Difficulty")
                    diff_stats = summary.get("difficulty_breakdown", {})
                    if diff_stats:
                        df_diff = pd.DataFrame([
                            {
                                "Difficulty Tier": d.capitalize(),
                                "Total Cases": stats.get("total", 0),
                                "Passed Cases": stats.get("passed", 0),
                                "Accuracy (%)": stats.get("accuracy_pct", 0.0)
                            }
                            for d, stats in diff_stats.items()
                        ])
                        st.dataframe(df_diff, hide_index=True, use_container_width=True)
                        st.bar_chart(df_diff, x="Difficulty Tier", y="Accuracy (%)", use_container_width=True)
                    else:
                        st.info("No difficulty breakdown stats available.")

                with col_right:
                    # View 2: Failure Taxonomy Analysis & Categories
                    st.markdown("#### 🔍 Failure Diagnostics & Taxonomy Breakdown")
                    failed_results = [r for r in results if not r.get("success", False)]

                    if not failed_results:
                        st.success("🎉 **Perfect Run!** Zero failed queries encountered. The safety validation and semantic validation passed flawlessly.")
                    else:
                        # Define failure categories
                        error_patterns = {
                            "SchemaError": ["column", "table", "relation", "alias", "schema"],
                            "JoinError": ["join", "on clause", "ambiguous"],
                            "AggregationError": ["group by", "aggregate", "non-aggregated"],
                            "FilterError": ["where", "filter", "operator", "syntax for type", "invalid input syntax"],
                            "LimitError": ["limit", "offset"],
                            "SemanticError": ["row count mismatch", "data cells do not match", "semantic validation error", "semantic validation exception"]
                        }

                        classification_counts = {k: 0 for k in error_patterns.keys()}
                        classification_counts["UnknownError"] = 0

                        for r in failed_results:
                            matched = False
                            err_msg = (r.get("error_message") or "").lower()

                            for cat, keywords in error_patterns.items():
                                if any(kw in err_msg for kw in keywords):
                                    classification_counts[cat] += 1
                                    matched = True
                                    break
                            if not matched:
                                classification_counts["UnknownError"] += 1

                        df_errors = pd.DataFrame([
                            {"Error Category": k, "Failures count": v}
                            for k, v in classification_counts.items() if v > 0
                        ])

                        if not df_errors.empty:
                            st.dataframe(df_errors, hide_index=True, use_container_width=True)
                            st.bar_chart(df_errors, x="Error Category", y="Failures count", horizontal=True, use_container_width=True)
                        else:
                            st.info("Failed queries found but could not be categorized.")

                st.divider()

                # --- Latency & Token side-by-side ---
                col_lat, col_tok = st.columns(2)

                with col_lat:
                    # View 3: Latency distributions
                    st.markdown("#### ⏱️ Query Latency Distributions")
                    df_res = pd.DataFrame([
                        {
                            "Case ID": r.get("case_id"),
                            "Latency (s)": r.get("latency_seconds", 0.0),
                            "Status": "PASS" if r.get("success", False) else "FAIL"
                        }
                        for r in results
                    ])
                    st.bar_chart(df_res, x="Case ID", y="Latency (s)", use_container_width=True)

                    # Latency stats
                    latencies_list = [r.get("latency_seconds", 0.0) for r in results]
                    if latencies_list:
                        min_lat = min(latencies_list)
                        max_lat = max(latencies_list)
                        st.caption(f"⏱️ **Min Latency**: `{min_lat:.2f} s` | **Max Latency**: `{max_lat:.2f} s` | **Avg Latency**: `{avg_lat:.2f} s`")

                with col_tok:
                    # View 4: Token usage & Cost Projections
                    st.markdown("#### 💸 Token Usage & Projections")
                    df_tokens = pd.DataFrame([
                        {
                            "Case ID": r.get("case_id"),
                            "Tokens Used": r.get("total_tokens", 0),
                            "Cost ($)": (r.get("prompt_tokens", 0) * 0.000000075) + (r.get("completion_tokens", 0) * 0.00000030)
                        }
                        for r in results
                    ])
                    st.bar_chart(df_tokens, x="Case ID", y="Tokens Used", use_container_width=True)

                    # Cost projections
                    cost_100 = total_cost * (100 / total) if total > 0 else 0.0
                    cost_1000 = total_cost * (1000 / total) if total > 0 else 0.0
                    st.caption(f"💰 **Total Cost**: `${total_cost:.5f}` | **Projected Cost/100 queries**: `${cost_100:.4f}` | **Projected Cost/1,000 queries**: `${cost_1000:.3f}`")

                st.divider()

                # --- Failed Queries Explanatory Table ---
                st.markdown("#### ❌ Failed Query Diagnostic List")
                if failed_results:
                    df_failed_render = pd.DataFrame([
                        {
                            "Case ID": r.get("case_id"),
                            "NL Query": r.get("query"),
                            "Error Details": r.get("error_message"),
                            "Retries": r.get("retry_count", 0),
                            "Tokens": r.get("total_tokens", 0)
                        }
                        for r in failed_results
                    ])
                    st.dataframe(df_failed_render, hide_index=True, use_container_width=True)
                else:
                    st.success("Passed all benchmark test cases successfully!")

        except Exception as file_err:
            st.error(f"Error loading or parsing benchmark run logs: {file_err}")

