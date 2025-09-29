"""
Reusable ChatGPT-style UI component for Streamlit apps
"""
import streamlit as st


def render_chatgpt_ui(messages, input_key="user_input", on_send=None, on_retry=None, placeholder="Type your message..."):
    """
    Renders a ChatGPT-style UI with messages and input box.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content'
        input_key: Unique key for the chat input widget
        on_send: Callback function to handle user input (receives user_input as parameter)
        on_retry: Callback function to handle retry when error occurs (no parameters)
        placeholder: Placeholder text for input box
    """
    # Display chat messages
    import re
    import json as pyjson
    for idx, msg in enumerate(messages):
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if content is None:
            content = ""
        is_error = msg.get("is_error", False)

        # Skip system messages in UI
        if role == "system":
            continue

        # Skip error messages completely (don't show to user)
        if is_error:
            continue

        # Skip tool messages or render them differently
        if role == "tool":
            with st.expander("🔧 Tool Result", expanded=False):
                st.markdown(content, unsafe_allow_html=True)
            continue

        # Render user and assistant messages
        if role == "user":
            st.markdown(
                f'<div class="chat-message user-msg">🧑 {content}</div>',
                unsafe_allow_html=True
            )
        elif role == "assistant":
            # Try to pretty print JSON if present
            json_to_show = None
            match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", content)
            if match:
                try:
                    json_to_show = pyjson.loads(match.group(1))
                except Exception:
                    pass
            else:
                try:
                    json_to_show = pyjson.loads(content)
                except Exception:
                    pass
            if json_to_show is not None:
                st.markdown("**Extracted Resume Data:**")
                st.code(pyjson.dumps(json_to_show, indent=2), language="json")
            else:
                st.markdown(
                    f'<div class="chat-message bot-msg">🤖 {content}</div>',
                    unsafe_allow_html=True
                )
    
    # Check if the last message is an error
    show_retry = False
    if messages and messages[-1].get("is_error", False):
        show_retry = True
    
    # Show retry button if there's an error
    if show_retry and on_retry:
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            if st.button("🔄 Retry", key=f"{input_key}_retry", type="primary"):
                on_retry()
                st.rerun()
        with col2:
            st.caption("Something went wrong")
    
    # Chat input at the bottom
    user_input = st.chat_input(placeholder=placeholder, key=input_key)
    
    # Handle user input immediately
    if user_input:
        # Immediately append user message to session state
        if on_send:
            on_send(user_input)
        st.rerun()