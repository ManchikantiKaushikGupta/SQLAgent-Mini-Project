"""
Streamlit UI

A simple frontend connected to our FastAPI backend for interacting with the AI NL2SQL agent.
"""

import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000/api/v1/ask"

st.set_page_config(page_title="AI SQL Agent", page_icon="??", layout="wide")

st.title("?? NL2SQL AI Agent")
st.markdown("Ask a question in plain English, and the multi-agent system will convert it, validate it, and execute it against your PostgreSQL database.")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # If it's an assistant message, we might have rich SQL or data to show
        if msg["role"] == "assistant" and "data" in msg:
            with st.expander("Show execution details"):
                st.write("**Refined Query:**", msg["data"].get("refined_query", "N/A"))
                st.code(msg["data"].get("sql_query", "-- No SQL returned"), language="sql")
                if msg["data"].get("error"):
                    st.error(f"Error: {msg['data']['error']}")

            # Show results if available
            results = msg["data"].get("results")
            if results:
                df = pd.DataFrame(results)
                st.dataframe(df, use_container_width=True)

# Chat input
if prompt := st.chat_input("What would you like to know from the database?"):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process assistant response
    with st.chat_message("assistant"):
        with st.spinner("Agents are thinking, validating, and querying..."):
            try:
                response = requests.post(API_URL, json={"query": prompt})
                response.raise_for_status()
                data = response.json()
                
                error_msg = data.get("error")
                sql = data.get("sql_query")
                results = data.get("results")

                if error_msg:
                    answer_text = f"? **I ran into an issue:**\n\n{error_msg}"
                elif results is not None:
                    count = len(results)
                    answer_text = f"? **Query executed successfully!** Returned {count} rows."
                else:
                    answer_text = "?? **Query parsed, but no results were returned.**"

                st.markdown(answer_text)

                with st.expander("Show execution details"):
                    st.write("**Refined Query:**", data.get("refined_query", "N/A"))
                    st.code(sql if sql else "-- No SQL generated", language="sql")
                    if error_msg:
                        st.error(error_msg)

                if results:
                    st.dataframe(pd.DataFrame(results), use_container_width=True)

                # Append to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer_text,
                    "data": data
                })

            except requests.exceptions.RequestException as e:
                error_text = f"Failed to connect to the backend API: {e}"
                st.error(error_text)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_text
                })

