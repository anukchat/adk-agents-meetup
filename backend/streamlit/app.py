"""
Unified Streamlit App for LLM Use Cases - ChatGPT Style
Main entry point that loads different use cases
"""
import sys
import os
import streamlit as st
import importlib


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from recruitment_workflow import recruitment_workflow


st.set_page_config(page_title="LLM Chat Playground", page_icon="💬", layout="wide")

use_cases = {
    "Simple LLM Chat (No Tools)": "simple_llm_without_tools",
    "LLM Chat with Web Search Tool": "simple_llm_with_tools",
    "Intent Classification": "classification",
    "Information Extraction": "extraction",
    "Summarization": "summarization",
}

workflow_cases = {
    "Prompt Chaining": "recruitment_workflow_demo",
    "LLM-Based Routing": "llm_routing",
    "Parallel Processing": "parallel_processing",
}

# # --- Custom CSS for ChatGPT-style interface ---
st.markdown(
    """
    <style>
    header {visibility: hidden; height: 0 !important;}
    .css-18ni7ap.e8zbici2 {display: none;}

    /* Keep main layout scrollable but preserve chat input at bottom */
    .main .block-container {
        padding: 1rem 2rem;
        max-width: 100%;
        display: flex;
        flex-direction: column;
    }
    .stChatInputContainer {
        bottom: 0;
        background-color: white;
        padding-top: 0.5rem;
    }

    section[data-testid="stSidebar"] { background: #23272f; color: #fff; }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] h4 { color: #fff !important; }
    section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] .stMarkdown { color: #ccc !important; }
    .chat-message { padding: 0.75rem 1rem; border-radius: 1rem; margin-bottom: 0.75rem;
                    max-width: 75%; word-break: break-word; line-height: 1.5; }
    .user-msg { background-color: #DCF8C6; margin-left: auto; }
    .bot-msg { background-color: #F1F0F0; margin-right: auto; }
    </style>
    """,
    unsafe_allow_html=True,
)





def load_and_run_workflow_module(workflow_name: str, module_name: str):
    """Helper function to load and run workflow modules."""
    try:
        module = importlib.import_module(module_name)
        if hasattr(module, "main"):
            module.main()
        else:
            st.info(f"Please add a `main()` function to `{module_name}.py` for unified loading.")
    except Exception as e:
        st.error(f"Error loading {workflow_name}: {e}")
        st.exception(e)


# --- Sidebar: App Selection with Button Group and Contextual Sidebar ---
with st.sidebar:
    if "app_tab" not in st.session_state:
        st.session_state["app_tab"] = "LLM Playground"
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧠 Playground", type="primary" if st.session_state["app_tab"] == "LLM Playground" else "secondary"):
            st.session_state["app_tab"] = "LLM Playground"
            st.rerun()
    with col2:
        if st.button("⚡ Workflow", type="primary" if st.session_state["app_tab"] == "Workflow Execution Demo" else "secondary"):
            st.session_state["app_tab"] = "Workflow Execution Demo"
            st.rerun()
    st.markdown("---")
    app_tab = st.session_state["app_tab"]
    if app_tab == "LLM Playground":
        st.title("🧠 LLM Playground")
        prev_selected = st.session_state.get("_prev_use_case_selector", None)
        selected = st.selectbox(
            "Select Use Case", 
            list(use_cases.keys()),
            key="use_case_selector"
        )

        # Reset session state if selection changes
        if prev_selected is not None and prev_selected != selected:
            for k in st.session_state.keys():
                if k not in ("use_case_selector", "_prev_use_case_selector"):
                    del st.session_state[k]
        st.session_state["_prev_use_case_selector"] = selected

        st.markdown("---")
        st.markdown("**Tip:** Use the chat window to interact with the selected use case.")

        # Role Sequence
        messages = st.session_state.get("messages", [])
        st.markdown("---")
        st.subheader("🔎 Message Role Sequence")
        if messages:
            role_map = {"user": "🧑 User","assistant": "🤖 Assistant","tool": "🔧 Tool","system": "⚙️ System"}
            role_labels = [role_map.get(m.get("role", "?"), m.get("role", "?")) for m in messages]
            roles_html = "".join(
                f"<li style='margin-bottom:0.3rem;font-size:1.1rem;color:#fff;'>{label}</li>"
                for label in role_labels
            )
            st.markdown(f"<ul style='list-style-type:none; padding-left:0;'>{roles_html}</ul>", unsafe_allow_html=True)
            st.caption("This shows the order and type of message roles exchanged in the chat.")
        else:
            st.info("No messages yet. Start chatting to see the sequence!")
    elif app_tab == "Workflow Execution Demo":
        st.title("⚡ Workflow Demo")
        prev_selected_workflow = st.session_state.get("_prev_workflow_selector", None)
        selected_workflow = st.selectbox(
            "Select Workflow", 
            list(workflow_cases.keys()),
            key="workflow_selector"
        )

        # Reset session state if selection changes
        if prev_selected_workflow is not None and prev_selected_workflow != selected_workflow:
            for k in st.session_state.keys():
                if k not in ("workflow_selector", "_prev_workflow_selector", "app_tab"):
                    del st.session_state[k]
        st.session_state["_prev_workflow_selector"] = selected_workflow

        st.markdown("---")
        if selected_workflow == "Prompt Chaining":
            st.markdown("**Tip:** This demonstrates a step-by-step workflow for resume processing.")
        elif selected_workflow == "LLM-Based Routing":
            st.markdown("**Tip:** This shows how LLM can automatically classify and route different types of user queries.")
        elif selected_workflow == "Parallel Processing":
            st.markdown("**Tip:** This demonstrates parallel execution of multiple LLM calls using LangGraph.")

        # Role Sequence for workflow cases that use chat interface
        if selected_workflow == "LLM-Based Routing":
            messages = st.session_state.get("messages", [])
            st.markdown("---")
            st.subheader("🔎 Message Role Sequence")
            if messages:
                role_map = {"user": "🧑 User","assistant": "🤖 Assistant","tool": "🔧 Tool","system": "⚙️ System"}
                role_labels = [role_map.get(m.get("role", "?"), m.get("role", "?")) for m in messages]
                roles_html = "".join(
                    f"<li style='margin-bottom:0.3rem;font-size:1.1rem;color:#fff;'>{label}</li>"
                    for label in role_labels
                )
                st.markdown(f"<ul style='list-style-type:none; padding-left:0;'>{roles_html}</ul>", unsafe_allow_html=True)
                st.caption("This shows the order and type of message roles exchanged in the chat.")
            else:
                st.info("No messages yet. Start chatting to see the sequence!")

# --- Main Content: Use Case or Workflow Demo ---
if 'app_tab' not in locals():
    app_tab = "LLM Playground"

if app_tab == "LLM Playground":
    module_name = use_cases[st.session_state.get("use_case_selector", list(use_cases.keys())[0])]
    try:
        module = importlib.import_module(module_name)
        if hasattr(module, "main"):
            module.main()  # <- this is where render_chatgpt_ui() runs
        else:
            st.info(f"Please add a `main()` function to `{module_name}.py` for unified loading.")
    except Exception as e:
        st.error(f"Error loading {module_name}: {e}")
        st.exception(e)

elif app_tab == "Workflow Execution Demo":
    selected_workflow = st.session_state.get("workflow_selector", list(workflow_cases.keys())[0])
    
    if selected_workflow == "Prompt Chaining":
        # Original recruitment workflow functionality
        st.title("⚡ Step-by-Step Workflow Execution")
        st.write("Enter a CV/resume text below to see how the workflow executes **step by step** with intermediate outputs.")

        cv_text = st.text_area("Paste Resume Text", height=200, placeholder="Paste candidate CV/resume here...")

        if st.button("🚀 Run Workflow"):
            if not cv_text.strip():
                st.warning("Please provide some resume text.")
            else:
                with st.spinner("Running recruitment workflow..."):
                    result = recruitment_workflow(cv_text)

                # Step 1: Domain classification
                st.markdown("### 📝 Step 1: Classify Domain/Technology")
                st.success(f"**Identified Domain:** {result['domain']}")

                # Step 2: Match requirements
                st.markdown("### 🎯 Step 2: Match Against Open Requirements")
                if result["matched"]:
                    st.success(f"✅ Match Found → {result['matched_role']}")
                else:
                    st.error("❌ No Match Found")

                # Step 3: Email drafting (only if matched)
                st.markdown("### 📧 Step 3: Email to Hiring Manager")
                if result["email"]:
                    st.info(result["email"])
                else:
                    st.warning("No email generated since no match was found.")

                # Final Output
                st.markdown("---")
                st.subheader("✅ Final Workflow Result")
                st.json(result)
                
    elif selected_workflow == "LLM-Based Routing":
        # Load and run the LLM routing module
        load_and_run_workflow_module(selected_workflow, workflow_cases[selected_workflow])
            
    elif selected_workflow == "Parallel Processing":
        # Load and run the parallel processing module
        load_and_run_workflow_module(selected_workflow, workflow_cases[selected_workflow])
