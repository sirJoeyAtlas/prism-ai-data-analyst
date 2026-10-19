import streamlit as st
import pandas as pd
import time
import os
from database import db
from engine import llm, prompts, profiler, executor
from ui import upload, charts, chat

# ==========================================
# 1. PAGE CONFIG & PREMIUM CSS
# ==========================================
st.set_page_config(
    page_title="Local Data Intelligence",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    /* 1. Global Background & Typography */
    .stApp {
        background: linear-gradient(135deg, #f7f9fc 0%, #eef2f6 100%) !important;
    }
    html, body, [class*="css"], p, span, div {
        color: #1a1f2e !important;
        font-family: 'Inter', 'Segoe UI', sans-serif !important;
    }

    /* 2. Headings */
    h1 {
        background: -webkit-linear-gradient(45deg, #1f4e79, #2d6ba3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }
    h2, h3, h4 { color: #1f4e79 !important; }

    /* 3. Sidebar */
    section[data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1px solid #e1e6ee;
        box-shadow: 2px 0 10px rgba(0,0,0,0.02);
    }

    /* 4. Metric Cards */
    [data-testid="stMetric"] {
        background: #ffffff !important;
        border: 1px solid #e1e6ee;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 4px 6px rgba(31, 78, 121, 0.04);
        transition: transform 0.2s;
    }
    [data-testid="stMetric"]:hover { transform: translateY(-2px); }
    [data-testid="stMetricLabel"] { color: #6b7280 !important; font-weight: 600; }
    [data-testid="stMetricValue"] { color: #1f4e79 !important; font-weight: 700; }

    /* 5. Standard Buttons (Fix for dark text on dark background) */
    .stButton > button {
        background: #1f4e79 !important;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(31, 78, 121, 0.2);
    }
    .stButton > button:hover {
        background: #2d6ba3 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(31, 78, 121, 0.3);
    }
    /* Force all text inside buttons to be white */
    .stButton > button p, .stButton > button span, .stButton > button div {
        color: #ffffff !important;
    }

    /* 5b. Download Buttons */
    .stDownloadButton > button {
        background: #1f4e79 !important;
        border: none !important;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(31, 78, 121, 0.2);
        width: 100%;
    }
    .stDownloadButton > button:hover {
        background: #2d6ba3 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(31, 78, 121, 0.3);
    }
    .stDownloadButton > button p, .stDownloadButton > button span, .stDownloadButton > button div {
        color: #ffffff !important;
    }

    /* 6. Chat Messages */
    .stChatMessage {
        background: #ffffff !important;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border: 1px solid #e1e6ee;
    }
    
    /* 7. Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] {
        color: #6b7280 !important; 
        font-weight: 600;
        font-size: 1.1rem;
    }
    .stTabs [aria-selected="true"] {
        color: #1f4e79 !important; 
        border-bottom: 3px solid #1f4e79 !important;
    }

    /* 8. Code Blocks (Fix for invisible text in Schema and Generated Code) */
    [data-testid="stCode"], [data-testid="stCodeBlock"] {
        background-color: #1e1e2e !important; /* Dark background for code */
        border: 1px solid #313244 !important;
        border-radius: 8px !important;
    }
    [data-testid="stCode"] pre, [data-testid="stCodeBlock"] pre {
        background-color: transparent !important;
    }
    /* Force all text inside code blocks to be light */
    [data-testid="stCode"] span, [data-testid="stCodeBlock"] span {
        color: #cdd6f4 !important; 
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. INITIALIZATION & HERO HEADER
# ==========================================
db.init_db()

# The Unique Prism Header
st.markdown("""
<div style="
    background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
    padding: 40px 30px;
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
    margin-bottom: 30px;
    display: flex;
    align-items: center;
    gap: 25px;
">
    <div style="
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 15px;
        border-radius: 20px;
        font-size: 3rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    ">
        🔮
    </div>
    <div>
        <h1 style="
            margin: 0; 
            padding: 0; 
            font-size: 3rem; 
            font-weight: 800; 
            letter-spacing: -1.5px;
            background: linear-gradient(90deg, #ffffff, #a1c4fd);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        ">
            Local Data Intelligence Engine
        </h1>
        <p style="
            margin: 5px 0 0 0; 
            color: #a1c4fd; 
            font-size: 1.1rem; 
            font-weight: 500;
            letter-spacing: 0.5px;
        ">
            Local Data Intelligence Engine &bull; 100% Private
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

df = upload.render_upload()

# Clear Session Button
if st.sidebar.button("🗑️ Clear Session", use_container_width=True):
    keys_to_delete = ["df", "profile", "dataset_id", "last_result", "last_fig", 
                      "last_code", "last_explanation", "last_error", "last_question", "pending_question"]
    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

if df is None:
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    col1.markdown("### 📁 Upload\nDrop a CSV or Excel file in the sidebar.")
    col2.markdown("### 💬 Ask\nType any question in plain English.")
    col3.markdown("### 📊 Analyze\nGet code, charts, and explanations locally.")
    st.stop()

# ==========================================
# 3. AUTO-DASHBOARD
# ==========================================
st.markdown("### 📊 Dataset Overview")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Rows", f"{len(df):,}")
c2.metric("Columns", len(df.columns))
c3.metric("Missing Values", int(df.isnull().sum().sum()))
c4.metric("Numeric Columns", len(df.select_dtypes(include='number').columns))

with st.expander("🧠 What the AI sees (Schema)", expanded=False):
    st.code(profiler.profile_to_text(st.session_state.profile), language="text")

st.markdown("---")

# ==========================================
# 4. MAIN TABS (Analyze / History)
# ==========================================
tab_analyze, tab_history = st.tabs(["💬 Analyze", "📜 Query History"])

with tab_analyze:
    # --- SMART DYNAMIC BUTTONS ---
    if "df" in st.session_state:
        st.markdown("**Try one of these:**")
        num_cols = df.select_dtypes(include='number').columns.tolist()
        cat_cols = df.select_dtypes(include='object').columns.tolist()
        
        priority_num = [c for c in num_cols if c in ['points', 'sales', 'revenue', 'orders', 'age']]
        if priority_num:
            num_cols = priority_num + [c for c in num_cols if c not in priority_num]
        
        priority_cat = [c for c in cat_cols if c in ['driver', 'team', 'region', 'category', 'gender']]
        if priority_cat:
            cat_cols = priority_cat + [c for c in cat_cols if c not in priority_cat]
        
        examples = []
        if num_cols and cat_cols:
            examples.append(f"Show total {num_cols[0]} by {cat_cols[0]}")
            examples.append(f"Which {cat_cols[0]} had the highest {num_cols[0]}?")
        if num_cols:
            examples.append(f"What is the average {num_cols[0]}?")
        
        if examples:
            btn_cols = st.columns(len(examples))
            for i, ex in enumerate(examples):
                if btn_cols[i].button(ex, use_container_width=True):
                    st.session_state.pending_question = ex
                    st.rerun()

    st.markdown("---")

    # Render past chat history from DB (if any)
    chat.render_chat_history(st.session_state.dataset_id)
    
    # Accept click OR typed input
    typed = st.chat_input("Ask about your data")
    question = typed or st.session_state.pop("pending_question", None)

    if question:
        st.session_state.last_question = question
        
        with st.chat_message("user", avatar="❓"):
            st.markdown(question)

        schema_text = profiler.profile_to_text(st.session_state.profile)
        start_time = time.time()

        # CLEAN LOADING UI
        loading_placeholder = st.empty()
        with loading_placeholder.container():
            with st.spinner("🧠 Analyzing dataset locally... (This takes 10-20s)"):
                time.sleep(0.5) 

        max_attempts = 3
        code, result = None, None
        
        for attempt in range(1, max_attempts + 1):
            try:
                history = db.get_queries(st.session_state.dataset_id)
                messages = prompts.code_gen_messages(schema_text, question, history)
                
                if attempt > 1 and result and result.get("error"):
                    messages.append({"role": "assistant", "content": code})
                    messages.append({"role": "user", "content": f"That failed with: {result['error']}. Fix it."})
                
                code = llm.generate_code(messages)
            except Exception as e:
                st.error(f"Ollama error: {e}")
                st.stop()

            if not code.strip():
                continue

            result = executor.execute_code(code, st.session_state.df)
            if result["success"]:
                break

        # Clear the loading spinner!
        loading_placeholder.empty()

        latency = round(time.time() - start_time, 2)

        if not result or not result["success"]:
            st.error(f"Failed after {max_attempts} attempts: {result['error']}")
            st.stop()

        # Fallback chart
        if result["fig"] is None and result["result"] is not None:
            fallback = executor.auto_chart(result["result"], st.session_state.df)
            if fallback:
                result["fig"] = fallback

        result_text = executor.result_to_text(result["result"])
        
        with st.spinner("✍️ Generating explanation..."):
            explanation = llm.explain(prompts.explain_messages(question, code, result_text))
            
        # Save to Database
        db.save_query(st.session_state.dataset_id, question, code, result_text, explanation, True)

        # Display the Assistant's Answer
        with st.chat_message("assistant", avatar="📊"):
            st.markdown(f"**Answer:** {explanation}")
            st.caption(f"⚡ Analysis complete in {latency}s")
            st.markdown("---")
            
            charts.render_result(result["result"], result["fig"])
            
            with st.expander("💻 View generated code"):
                st.code(code, language="python")
                
            # Fast PDF Generation (Text Only)
            try:
                from engine import export
                pdf_bytes = export.export_analysis(question, code, result_text, explanation, fig=None)
                st.download_button(
                    label="📥 Download Analysis as PDF",
                    data=pdf_bytes,
                    file_name="analysis_report.pdf",
                    mime="application/pdf",
                    key="pdf_download_btn"
                )
            except Exception as e:
                st.warning(f"Could not generate PDF: {e}")

with tab_history:
    st.subheader("📜 Query History")
    
    # Clear History Button
    if st.button("🗑️ Clear Database History"):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM queries WHERE dataset_id = ?", (st.session_state.dataset_id,))
        conn.commit()
        cursor.close()
        conn.close()
        st.success("History cleared!")
        time.sleep(1)
        st.rerun()

    history = db.get_queries(st.session_state.dataset_id)
    if not history:
        st.info("No queries yet. Ask a question in the Analyze tab.")
    else:
        for q in history:
            with st.container(border=True):
                # Header
                col1, col2 = st.columns([3, 1])
                col1.markdown(f"#### ❓ {q['question']}")
                col2.caption(f"🕒 {q['created_at']}")
                
                # Explanation
                if q['explanation']:
                    st.markdown(f"**📊 Answer:** {q['explanation']}")
                
                # Expander for code
                with st.expander("💻 View generated code"):
                    st.code(q['generated_code'], language="python")