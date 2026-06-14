import streamlit as st
import requests
import pandas as pd
import os
import json
from typing import Any, Dict

API_URL = "http://127.0.0.1:8001/api/v1/ask"

# 1. Page Configuration
st.set_page_config(
    page_title="DataSense AI - Telemetry Portal",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I am your AI SQL Agent. Ask me any analytical question, and I'll generate the query plan, prune the schema via FAISS, write the SQL, and display live metrics diagnostics!"
        }
    ]

if "last_metrics" not in st.session_state:
    st.session_state.last_metrics = None

if "active_page" not in st.session_state:
    st.session_state.active_page = "chats"

if "user_role" not in st.session_state:
    st.session_state.user_role = "restricted_user"

if "username" not in st.session_state:
    st.session_state.username = "anonymous"

if "selected_provider" not in st.session_state:
    st.session_state.selected_provider = "Default"

if "selected_model" not in st.session_state:
    st.session_state.selected_model = None

if "prefilled_query" not in st.session_state:
    st.session_state.prefilled_query = None


# 3. Dynamic Styles and DOM Tagging Scripts
# Inject Google Font and VOXA dark theme colors
active_page = st.session_state.active_page

st.markdown(f"""
    <style>
        /* Hide default Streamlit elements */
        footer {{visibility: hidden !important;}}
        #MainMenu {{visibility: hidden !important;}}
        
        /* Load Space Grotesk Google Font */
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
        
        /* Global Font & Layout Overrides */
        html, body, [class*="css"], .stText, .stMarkdown, p, h1, h2, h3, h4, h5, h6, span, button, input, label, select, textarea, div.stSelectbox, div.stTextInput {{
            font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }}
        
        .block-container {{
            padding-top: 1.5rem !important;
            padding-bottom: 2rem !important;
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        /* Premium Background Gradient (Radial Glow) */
        [data-testid="stAppViewContainer"] {{
            background: radial-gradient(circle at 85% 15%, #0d1e30 0%, #040404 70%) !important;
            color: #ffffff !important;
        }}
        
        [data-testid="stSidebar"] {{
            background-color: #040404 !important;
            border-right: 1px solid #171717 !important;
            padding-top: 1rem !important;
        }}
        
        [data-testid="stHeader"] {{
            background-color: transparent !important;
            backdrop-filter: blur(8px) !important;
            border-bottom: none !important;
        }}
        
        [data-testid="stSidebarCollapseButton"] {{
            color: #ffffff !important;
        }}
        
        /* Sidebar VOXA Custom Layout & Typography */
        .logo-container {{
            padding: 0.5rem 0.5rem;
            margin-bottom: 0.8rem;
            display: flex;
            align-items: center;
            gap: 0.6rem;
        }}
        .logo-text {{
            font-size: 1.8rem;
            font-weight: 700;
            letter-spacing: -1.5px;
            color: #ffffff;
            font-family: 'Space Grotesk', sans-serif;
        }}
        .logo-sub {{
            font-size: 0.7rem;
            background: linear-gradient(90deg, #6ec0ff 0%, #2d8cff 100%);
            color: #040404;
            padding: 0.15rem 0.4rem;
            border-radius: 4px;
            font-weight: 700;
            letter-spacing: 0px;
        }}
        
        .search-box {{
            background-color: #171717;
            border: 1px solid #2d2d2d;
            border-radius: 12px;
            padding: 0.5rem 0.8rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 1.2rem;
            margin-left: 0.5rem;
            margin-right: 0.5rem;
        }}
        .search-icon {{
            color: #8f95b2;
            font-size: 0.9rem;
        }}
        .search-input {{
            background: transparent !important;
            border: none !important;
            color: #ffffff !important;
            font-size: 0.85rem !important;
            width: 100% !important;
            padding: 0 !important;
            outline: none !important;
        }}
        
        .sidebar-heading {{
            color: #8f95b2;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin: 1.2rem 0.8rem 0.4rem 0.8rem;
        }}
        
        .sidebar-divider {{
            border-top: 1px solid #171717;
            margin: 1.2rem 0.5rem;
        }}
        
        /* Sidebar Nav Buttons Styling - Prevent white rectangles */
        div[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"],
        div[data-testid="stSidebar"] button[kind="secondary"],
        div[data-testid="stSidebar"] button {{
            background-color: transparent !important;
            background: transparent !important;
            color: #8f95b2 !important;
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
            text-align: left !important;
            justify-content: flex-start !important;
            display: flex !important;
            width: calc(100% - 1rem) !important;
            padding: 0.6rem 1rem !important;
            margin: 0.15rem 0.5rem !important;
            border-radius: 10px !important;
            font-size: 0.95rem !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }}
        div[data-testid="stSidebar"] button:hover {{
            background-color: #171717 !important;
            background: #171717 !important;
            color: #ffffff !important;
        }}
        
        /* Force button text elements to inherit the color (vital for Streamlit light mode fallback) */
        div[data-testid="stSidebar"] button p,
        div[data-testid="stSidebar"] button span,
        div[data-testid="stSidebar"] button div,
        div[data-testid="stSidebar"] button * {{
            color: inherit !important;
        }}
        
        /* Active nav item override */
        div[data-testid="stSidebar"] button[data-nav="{active_page}"],
        div[data-testid="stSidebar"] [data-nav="{active_page}"] button,
        div[data-testid="stSidebar"] button[data-nav="{active_page}"]:hover,
        div[data-testid="stSidebar"] button[data-nav="{active_page}"]:active,
        div[data-testid="stSidebar"] button[data-nav="{active_page}"]:focus {{
            background-color: #171717 !important;
            background: #171717 !important;
            color: #ffffff !important;
            border-left: 4px solid #2d8cff !important;
            padding-left: calc(1rem - 4px) !important;
            border-radius: 0 10px 10px 0 !important;
        }}
        
        /* Sidebar Bottom Sparkle Card */
        .sidebar-footer-card {{
            background: linear-gradient(135deg, #171717 0%, #121212 100%);
            border: 1px solid #2d2d2d;
            border-radius: 16px;
            padding: 0.8rem 1rem;
            display: flex;
            align-items: center;
            gap: 0.8rem;
            margin: 1rem 0.5rem;
        }}
        .footer-card-icon {{
            width: 36px;
            height: 36px;
            background: radial-gradient(circle, #2d8cff 0%, #0d1e30 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1rem;
            box-shadow: 0 0 10px rgba(45, 140, 255, 0.4);
        }}
        .footer-card-title {{
            font-weight: 600;
            color: #ffffff;
            font-size: 0.9rem;
        }}
        .footer-card-desc {{
            color: #8f95b2;
            font-size: 0.75rem;
        }}
        
        /* Chat Workspace Elements */
        .chat-header-container {{
            display: flex !important;
            justify-content: space-between !important;
            align-items: center !important;
            border-bottom: 1px solid #171717 !important;
            padding-bottom: 1rem !important;
            margin-bottom: 1.5rem !important;
            flex-wrap: wrap !important;
            gap: 1rem !important;
            width: 100% !important;
        }}
        .chat-header-left {{
            display: flex !important;
            flex-direction: column !important;
            gap: 0.2rem !important;
            text-align: left !important;
        }}
        .chat-header-title {{
            font-size: 1.4rem !important;
            font-weight: 700 !important;
            color: #ffffff !important;
            display: flex !important;
            align-items: center !important;
            gap: 0.5rem !important;
        }}
        .chat-header-subtitle {{
            font-size: 0.85rem !important;
            color: #8f95b2 !important;
            margin: 0 !important;
        }}
        .chat-header-right {{
            display: flex !important;
            align-items: center !important;
            justify-content: flex-end !important;
            gap: 0.8rem !important;
            flex-shrink: 0 !important;
        }}
        .header-badge {{
            padding: 0.4rem 0.8rem;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
            border: 1px solid transparent;
        }}
        .bg-blue {{
            background-color: rgba(45, 140, 255, 0.12) !important;
            color: #6ec0ff !important;
            border: 1px solid rgba(45, 140, 255, 0.3) !important;
        }}
        .bg-grey {{
            background-color: #171717 !important;
            color: #ffffff !important;
            border: 1px solid #2d2d2d !important;
        }}
        .header-avatar {{
            width: 36px;
            height: 36px;
            border-radius: 50%;
            border: 2px solid #2d8cff;
            background-color: #171717;
            box-shadow: 0 0 10px rgba(45, 140, 255, 0.3);
        }}
        
        /* Chat bubbles */
        div[data-testid="stChatMessage"] {{
            background-color: transparent !important;
            border: none !important;
            padding: 0.8rem 0 !important;
        }}
        div[data-testid="stChatMessage"][data-role="user"] {{
            display: flex !important;
            flex-direction: row-reverse !important;
            text-align: right !important;
        }}
        div[data-testid="stChatMessage"][data-role="user"] [data-testid="stChatMessageAvatar"] {{
            margin-left: 0.8rem !important;
            margin-right: 0 !important;
            order: 2 !important;
            background-color: #171717 !important;
            border: 1px solid #2d2d2d !important;
        }}
        div[data-testid="stChatMessage"][data-role="user"] div.stMarkdown {{
            background-color: #171717 !important;
            color: #ffffff !important;
            padding: 0.8rem 1.2rem !important;
            border-radius: 20px 20px 0px 20px !important;
            display: inline-block !important;
            max-width: 75% !important;
            text-align: left !important;
            border: 1px solid #2d2d2d !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4) !important;
        }}
        div[data-testid="stChatMessage"][data-role="assistant"] {{
            display: flex !important;
            flex-direction: row !important;
        }}
        div[data-testid="stChatMessage"][data-role="assistant"] [data-testid="stChatMessageAvatar"] {{
            margin-right: 0.8rem !important;
            background-color: #2d8cff !important;
            box-shadow: 0 0 10px rgba(45, 140, 255, 0.4) !important;
            border: none !important;
        }}
        div[data-testid="stChatMessage"][data-role="assistant"] div.stMarkdown {{
            color: #ffffff !important;
            background-color: transparent !important;
            padding: 0.2rem 0 !important;
            display: inline-block !important;
            max-width: 85% !important;
        }}
        
        /* Chat Input - Prevent white background and white overlay at the bottom */
        [data-testid="stBottom"],
        div[class*="stBottom"],
        .st-emotion-cache-12fmhud,
        .st-emotion-cache-1c7n2ri {{
            background: linear-gradient(180deg, rgba(4, 4, 4, 0) 0%, #040404 40%, #040404 100%) !important;
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }}
        
        div[data-testid="stChatInput"] {{
            background-color: transparent !important;
            border: none !important;
            padding: 1.5rem 0 !important;
        }}
        div[data-testid="stChatInput"] > div {{
            background-color: #171717 !important;
            border: 1px solid #2d2d2d !important;
            border-radius: 28px !important;
            padding: 0.3rem 0.8rem !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5) !important;
            transition: all 0.3s ease !important;
        }}
        div[data-testid="stChatInput"] > div:focus-within {{
            border-color: #2d8cff !important;
            box-shadow: 0 0 15px rgba(45, 140, 255, 0.3) !important;
        }}
        
        /* Force Textarea transparent background in both modes */
        div[data-testid="stChatInput"] textarea,
        div[data-testid="stChatInput"] [data-testid="stChatInputTextArea"],
        [data-testid="stChatInputTextArea"],
        .stChatInputTextArea {{
            background-color: transparent !important;
            background: transparent !important;
            color: #ffffff !important;
            font-size: 0.95rem !important;
            caret-color: #2d8cff !important;
            border: none !important;
            box-shadow: none !important;
        }}
        div[data-testid="stChatInput"] button {{
            background-color: #2d8cff !important;
            border-radius: 50% !important;
            width: 36px !important;
            height: 36px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            color: #ffffff !important;
            border: none !important;
            transition: all 0.2s ease !important;
        }}
        div[data-testid="stChatInput"] button:hover {{
            background-color: #6ec0ff !important;
            box-shadow: 0 0 10px rgba(45, 140, 255, 0.6) !important;
        }}
        
        /* Custom styled containers & inputs */
        .content-panel {{
            background-color: #171717 !important;
            border: 1px solid #2d2d2d !important;
            border-radius: 16px !important;
            padding: 1.8rem !important;
            margin-bottom: 1.5rem !important;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3) !important;
        }}
        
        /* Diagnostics KPI Cards */
        .kpi-container {{
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            margin-bottom: 1.5rem;
        }}
        .kpi-card {{
            flex: 1;
            min-width: 180px;
            background: linear-gradient(135deg, #171717 0%, #1a1a1a 100%) !important;
            border: 1px solid #2d2d2d !important;
            padding: 1.2rem !important;
            border-radius: 16px !important;
            text-align: center !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4) !important;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        }}
        .kpi-card:hover {{
            border-color: #2d8cff !important;
            transform: translateY(-3px) !important;
            box-shadow: 0 8px 25px rgba(45, 140, 255, 0.25) !important;
        }}
        .kpi-card p {{
            color: #8f95b2 !important;
            font-size: 0.85rem !important;
            font-weight: 500 !important;
            margin: 0 0 0.5rem 0 !important;
        }}
        .kpi-card h2 {{
            color: #ffffff !important;
            font-size: 1.8rem !important;
            font-weight: 700 !important;
            margin: 0 !important;
        }}
        
        /* Expander codes */
        div[data-testid="stExpander"] {{
            background-color: #0c0c0c !important;
            border: 1px solid #2d2d2d !important;
            border-radius: 12px !important;
            margin-top: 0.5rem !important;
            overflow: hidden !important;
        }}
        /* Expander header styling without layout disruption */
        div[data-testid="stExpander"] [data-testid="stExpanderHeader"] {{
            background-color: #171717 !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            border-bottom: 1px solid #2d2d2d !important;
        }}
        div[data-testid="stExpander"] [data-testid="stExpanderHeader"] * {{
            color: #ffffff !important;
        }}
        div[data-testid="stExpander"] [data-testid="stExpanderHeader"]:hover * {{
            color: #6ec0ff !important;
        }}
        div[data-testid="stExpander"] > div[role="transition"] {{
            padding: 1rem !important;
            background-color: #0c0c0c !important;
        }}
        
        /* Dataframes & Tables */
        div[data-testid="stDataFrame"] {{
            border: 1px solid #2d2d2d !important;
            border-radius: 12px !important;
            overflow: hidden !important;
            background-color: #171717 !important;
        }}
        
        /* Select and inputs */
        div[data-baseweb="select"] {{
            background-color: #171717 !important;
            border: 1px solid #2d2d2d !important;
            border-radius: 8px !important;
            color: #ffffff !important;
        }}
        div[data-baseweb="select"] * {{
            color: #ffffff !important;
            background-color: transparent !important;
        }}
        div[data-baseweb="popover"] {{
            background-color: #171717 !important;
            border: 1px solid #2d2d2d !important;
            color: #ffffff !important;
        }}
        div[data-baseweb="popover"] li {{
            color: #ffffff !important;
            background-color: #171717 !important;
            transition: all 0.2s ease !important;
        }}
        div[data-baseweb="popover"] li:hover {{
            background-color: #2d8cff !important;
        }}
        
        input[type="text"], input[type="number"], textarea {{
            background-color: #171717 !important;
            border: 1px solid #2d2d2d !important;
            border-radius: 8px !important;
            color: #ffffff !important;
            padding: 0.5rem 1rem !important;
        }}
        input[type="text"]:focus, textarea:focus {{
            border-color: #2d8cff !important;
            outline: none !important;
        }}
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
        }}
        ::-webkit-scrollbar-track {{
            background: #040404;
        }}
        ::-webkit-scrollbar-thumb {{
            background: #2d2d2d;
            border-radius: 4px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: #2d8cff;
        }}
    </style>
    
    <script>
        const runCustomTheme = () => {{
            // 1. Tag Sidebar Buttons
            const sidebar = window.parent.document.querySelector('[data-testid="stSidebar"]');
            if (sidebar) {{
                const buttons = sidebar.querySelectorAll('button');
                buttons.forEach(button => {{
                    const text = button.textContent || "";
                    if (text.includes("Chats")) {{
                        button.setAttribute('data-nav', 'chats');
                    }} else if (text.includes("Observability")) {{
                        button.setAttribute('data-nav', 'observability');
                    }} else if (text.includes("Benchmarks")) {{
                        button.setAttribute('data-nav', 'benchmarks');
                    }} else if (text.includes("Settings")) {{
                        button.setAttribute('data-nav', 'settings');
                    }} else if (text.includes("Top Customers")) {{
                        button.setAttribute('data-nav', 'ex-top');
                    }} else if (text.includes("Product Reviews")) {{
                        button.setAttribute('data-nav', 'ex-reviews');
                    }} else if (text.includes("Category Analysis")) {{
                        button.setAttribute('data-nav', 'ex-category');
                    }}
                }});
            }}

            // 2. Tag Chat Messages
            const messages = window.parent.document.querySelectorAll('[data-testid="stChatMessage"]');
            messages.forEach(msg => {{
                const avatar = msg.querySelector('[data-testid="stChatMessageAvatar"]');
                if (avatar) {{
                    const label = avatar.textContent || "";
                    if (label.includes("👤")) {{
                        msg.setAttribute('data-role', 'user');
                    }} else if (label.includes("✨")) {{
                        msg.setAttribute('data-role', 'assistant');
                    }}
                }}
            }});
        }};

        runCustomTheme();
        setInterval(runCustomTheme, 500);
    </script>
""", unsafe_allow_html=True)


# 4. SIDEBAR NAVIGATION
with st.sidebar:
    # DataSense AI Brand Logo
    st.markdown('<div class="logo-container"><span class="logo-text">DataSense</span><span class="logo-sub">AI</span></div>', unsafe_allow_html=True)
    
    # Search box mockup
    st.markdown('<div class="search-box"><span class="search-icon">🔍</span><input type="text" class="search-input" placeholder="Search..." readonly /></div>', unsafe_allow_html=True)
    
    # Sidebar Section: Settings (Navigation Links)
    st.markdown('<div class="sidebar-heading">Navigation</div>', unsafe_allow_html=True)
    
    if st.button("💬 Chats", use_container_width=True):
        st.session_state.active_page = "chats"
        st.rerun()
        
    if st.button("📊 Observability", use_container_width=True):
        st.session_state.active_page = "observability"
        st.rerun()
        
    if st.button("📈 Benchmarks", use_container_width=True):
        st.session_state.active_page = "benchmarks"
        st.rerun()
        
    if st.button("⚙️ Settings", use_container_width=True):
        st.session_state.active_page = "settings"
        st.rerun()
        
    # Sidebar Section: Chats (clickable mock prompts)
    st.markdown('<div class="sidebar-heading">Example Chats</div>', unsafe_allow_html=True)
    
    if st.button("🛍️ Top Customers Chat", use_container_width=True):
        st.session_state.active_page = "chats"
        st.session_state.prefilled_query = "Show the top 3 users by total order amount, ordered descending"
        st.rerun()
        
    if st.button("💻 Product Reviews Chat", use_container_width=True):
        st.session_state.active_page = "chats"
        st.session_state.prefilled_query = "Get all reviews for Laptop Model B2"
        st.rerun()
        
    if st.button("📦 Category Analysis Chat", use_container_width=True):
        st.session_state.active_page = "chats"
        st.session_state.prefilled_query = "Which category department has the highest number of products?"
        st.rerun()

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    
    # Bottom Sparkle Card
    st.markdown("""
        <div class="sidebar-footer-card">
            <div class="footer-card-icon">✨</div>
            <div class="footer-card-text">
                <div class="footer-card-title">Update the plan</div>
                <div class="footer-card-desc">Feel the power of AI</div>
            </div>
        </div>
    """, unsafe_allow_html=True)


# 5. RESOLVE CORE TELEMETRY / LLM ENGINE LABELS
last_prov = None
last_model = None
if st.session_state.last_metrics:
    last_prov = st.session_state.last_metrics.get("active_provider")
    last_model = st.session_state.last_metrics.get("active_model")
    
if last_prov and last_model:
    llm_engine_display = f"{last_prov.upper()} ({last_model})"
else:
    try:
        from llm.factory import get_provider
        prov = get_provider()
        prov_name = prov.__class__.__name__.replace("Provider", "")
        model_name = getattr(prov, "model", "Unknown")
        llm_engine_display = f"{prov_name} ({model_name})"
    except Exception:
        llm_engine_display = "Gemini 3.1 Flash Lite"


# 6. ROUTE MAIN PAGE CONTENT
if active_page == "chats":
    # --- HEADER BAR ---
    st.markdown(f"""
        <div class="chat-header-container">
            <div class="chat-header-left">
                <div class="chat-header-title">💬 DataSense AI Telemetry Workspace</div>
                <div class="chat-header-subtitle">Ask natural language queries to analyze database schemas and monitor step diagnostics.</div>
            </div>
            <div class="chat-header-right">
                <span class="header-badge bg-blue">💎 Engine: {llm_engine_display}</span>
                <span class="header-badge bg-grey">👤 {st.session_state.user_role.upper()} ({st.session_state.username})</span>
                <img class="header-avatar" src="https://api.dicebear.com/7.x/bottts/svg?seed={st.session_state.username}" />
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)

    # --- PROCESS PREFILLED RUNS ---
    prefilled_prompt = None
    if st.session_state.prefilled_query:
        prefilled_prompt = st.session_state.prefilled_query
        st.session_state.prefilled_query = None  # consume query

    # --- RENDER CHAT WORKSPACE ---
    # Render Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="✨" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])
            
            # Render SQL and table details
            if msg["role"] == "assistant" and "data" in msg:
                data = msg["data"]
                sql = data.get("sql_query")
                results = data.get("results")
                error_msg = data.get("error")
                active_prov = data.get("active_provider")
                active_model = data.get("active_model")
                
                if active_prov and active_model:
                    st.caption(f"🤖 Generated via: **{active_prov.upper()}** ({active_model})")
                
                with st.expander("🛠️ View SQL Statement"):
                    st.code(sql if sql else "-- No SQL query returned", language="sql")
                    if error_msg:
                        st.error(error_msg)
                        
                if results:
                    st.dataframe(pd.DataFrame(results), use_container_width=True)

    # Get input (from text entry OR template click)
    prompt = st.chat_input("Ask a question (e.g., Get top 3 spending users)...")
    if prefilled_prompt:
        prompt = prefilled_prompt

    # Handle input execution
    if prompt:
        # Append User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # Generate Assistant Response
        with st.chat_message("assistant", avatar="✨"):
            with st.spinner("Analyzing schema and generating optimized SQL..."):
                try:
                    payload = {
                        "query": prompt,
                        "user_role": st.session_state.user_role,
                        "username": st.session_state.username
                    }
                    if st.session_state.selected_provider != "Default":
                        payload["provider"] = st.session_state.selected_provider
                        if st.session_state.selected_model:
                            payload["model"] = st.session_state.selected_model

                    response = requests.post(API_URL, json=payload)
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
                    
                    active_prov = data.get("active_provider")
                    active_model = data.get("active_model")
                    if active_prov and active_model:
                        st.caption(f"🤖 Generated via: **{active_prov.upper()}** ({active_model})")

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
                    st.rerun()

                except requests.exceptions.RequestException as e:
                    error_text = f"An API connection error occurred: {e}"
                    st.error(error_text)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_text
                    })


elif active_page == "observability":
    st.title("📊 Observability Dashboard")
    st.caption("Live execution diagnostics and token telemetry logs.")
    st.markdown('<div style="height: 15px;"></div>', unsafe_allow_html=True)
    
    if st.session_state.last_metrics is None:
        st.info("💡 **No Active Telemetry**: Please execute a query inside the **Chats** workspace to view live performance telemetries.")
        
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
        
        # KPI Layout in custom styled boxes
        st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-card">
                    <p>Total Latency</p>
                    <h2>{total_latency:.2f} s</h2>
                </div>
                <div class="kpi-card">
                    <p>Total Tokens</p>
                    <h2>{total_tokens:,}</h2>
                </div>
                <div class="kpi-card">
                    <p>Prompt Tokens</p>
                    <h2>{prompt_tokens:,}</h2>
                </div>
                <div class="kpi-card">
                    <p>Completion Tokens</p>
                    <h2>{comp_tokens:,}</h2>
                </div>
                <div class="kpi-card">
                    <p>Repair Attempts</p>
                    <h2>{repair_attempts}</h2>
                </div>
            </div>
        """, unsafe_allow_html=True)

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


elif active_page == "benchmarks":
    st.title("📈 Multi-Dataset NL2SQL Benchmarks")
    st.caption("Evaluate accuracy metrics, latency bounds, retry statistics, and API cost distributions.")
    st.markdown('<div style="height: 15px;"></div>', unsafe_allow_html=True)

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
                total_cost = 0.0
                for r in results:
                    p_tok = r.get("prompt_tokens", 0)
                    c_tok = r.get("completion_tokens", 0)
                    total_cost += (p_tok * 0.000000075) + (c_tok * 0.00000030)

                corr_success = summary.get("correction_success_rate_pct", 0.0)
                corr_passed = summary.get("queries_corrected_successfully", 0)
                corr_total = summary.get("queries_needing_correction", 0)

                # Custom KPI panel rendering
                st.markdown(f"""
                    <div class="kpi-container">
                        <div class="kpi-card">
                            <p>Execution Accuracy</p>
                            <h2 style="color:#10b981 !important;">{acc:.1f}%</h2>
                            <span style="color:#8f95b2;font-size:0.75rem;">{passed} / {total} cases</span>
                        </div>
                        <div class="kpi-card">
                            <p>Avg Latency</p>
                            <h2>{avg_lat:.2f} s</h2>
                            <span style="color:#8f95b2;font-size:0.75rem;">per NL Query</span>
                        </div>
                        <div class="kpi-card">
                            <p>Avg Token Size</p>
                            <h2>{avg_tok:,.0f}</h2>
                            <span style="color:#8f95b2;font-size:0.75rem;">tokens / query</span>
                        </div>
                        <div class="kpi-card">
                            <p>Run API Cost</p>
                            <h2 style="color:#3b82f6 !important;">${total_cost:.5f}</h2>
                            <span style="color:#8f95b2;font-size:0.75rem;">for {total} queries</span>
                        </div>
                        <div class="kpi-card">
                            <p>Correction Rate</p>
                            <h2>{corr_success:.1f}%</h2>
                            <span style="color:#8f95b2;font-size:0.75rem;">{corr_passed} / {corr_total} repaired</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

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


elif active_page == "settings":
    st.title("⚙️ Telemetry & System Configurations")
    st.caption("Customize governance roles, adjust LLM router pathways, and inspect dynamic FAISS indexing constraints.")
    st.markdown('<div style="height: 15px;"></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="content-panel">', unsafe_allow_html=True)
    
    st.markdown("### 👤 User Governance Role Configuration")
    st.session_state.user_role = st.selectbox(
        "Governance Role Policy:",
        options=["restricted_user", "analyst", "manager", "admin"],
        index=["restricted_user", "analyst", "manager", "admin"].index(st.session_state.user_role),
        help="Enforces Table/Column RBAC permission controls on the AI graph."
    )
    st.session_state.username = st.text_input("Active Username Session:", value=st.session_state.username)
    
    st.divider()

    st.markdown("### 🤖 LLM Engine Router Settings")
    st.session_state.selected_provider = st.selectbox(
        "LLM Provider Pathway Override:",
        options=["Default", "gemini", "openai", "anthropic", "ollama", "vllm", "lmstudio"],
        index=["Default", "gemini", "openai", "anthropic", "ollama", "vllm", "lmstudio"].index(st.session_state.selected_provider),
        help="Override the globally configured LLM provider for this session."
    )

    if st.session_state.selected_provider != "Default":
        model_placeholders = {
            "gemini": ["gemini-3.1-flash-lite", "gemini-1.5-pro", "gemini-2.5-pro"],
            "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4"],
            "anthropic": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"],
            "ollama": ["qwen3:14b", "llama3", "deepseek-r1"],
            "vllm": ["Qwen/Qwen2.5-Coder-7B-Instruct"],
            "lmstudio": ["qwen3.5-9b", "qwen3-14b"]
        }
        
        opts = model_placeholders.get(st.session_state.selected_provider, [])
        opts = opts + ["Custom Model..."]
        
        # Calculate active index
        current_model = st.session_state.selected_model
        if current_model in opts:
            active_idx = opts.index(current_model)
        else:
            active_idx = len(opts) - 1 if current_model else 0
            
        model_choice = st.selectbox(
            "Model Name:",
            options=opts,
            index=active_idx,
            help="Choose the model to route queries to."
        )
        
        if model_choice == "Custom Model...":
            st.session_state.selected_model = st.text_input("Enter Custom Model Name:", value=st.session_state.selected_model or "")
        else:
            st.session_state.selected_model = model_choice
    else:
        st.session_state.selected_model = None

    st.divider()
    
    st.markdown("### 📊 Observability Specs & Index Details")
    col_inf1, col_inf2 = st.columns(2)
    with col_inf1:
        st.markdown("**Workflow Engine:** LangGraph (Hierarchical State Graph)")
        st.markdown("**Embedding Engine:** FAISS (`IndexFlatIP` - Cosine Similarity)")
    with col_inf2:
        st.markdown(f"**Default Server Provider:** {llm_engine_display}")
        st.markdown("**Telemetry Log Target:** Memory Buffer + Audit JSON Log")
        
    st.markdown('</div>', unsafe_allow_html=True)
