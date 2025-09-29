import streamlit as st
from src.utils.llm import call_llm

def llm_handle_send_with_retry(user_input, messages_key, last_user_input_key, error_key, llm_call_fn, **llm_call_kwargs):
    """
    Generic handler for LLM send with error handling and retry support.
    - user_input: The user message to send
    - messages_key: session_state key for messages
    - last_user_input_key: session_state key for last user input
    - error_key: session_state key for error flag
    - llm_call_fn: function to call the LLM (should accept messages and **kwargs)
    - llm_call_kwargs: extra kwargs for llm_call_fn
    """
    st.session_state[messages_key].append({"role": "user", "content": user_input})
    st.session_state[last_user_input_key] = user_input
    try:
        with st.spinner("LLM is thinking..."):
            response = llm_call_fn(st.session_state[messages_key], **llm_call_kwargs)
            content = response.choices[0].message.content
            st.session_state[messages_key].append({"role": "assistant", "content": content})
        st.session_state[error_key] = False
    except Exception as e:
        st.session_state[messages_key].append({
            "role": "assistant",
            "content": f"Error: {str(e)}",
            "is_error": True
        })
        st.session_state[error_key] = True

def llm_handle_retry(messages_key, last_user_input_key, error_key, handle_send_fn):
    """
    Generic retry handler for LLM chat flows.
    - handle_send_fn: function to call with user_input
    """
    if st.session_state[messages_key] and st.session_state[messages_key][-1].get("is_error", False):
        st.session_state[messages_key].pop()  # Remove error
    if st.session_state[messages_key] and st.session_state[messages_key][-1]["role"] == "user":
        user_input = st.session_state[messages_key].pop()["content"]
    else:
        user_input = st.session_state.get(last_user_input_key, None)
    if user_input:
        handle_send_fn(user_input)
