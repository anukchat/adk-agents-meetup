


import streamlit as st
from src.utils.llm import call_llm
from chatgpt_ui import render_chatgpt_ui
from llm_retry_utils import llm_handle_send_with_retry, llm_handle_retry

def main():
	st.title("Simple LLM Chat (No Tools)")
	if "messages" not in st.session_state:
		st.session_state["messages"] = []
	if "error" not in st.session_state:
		st.session_state["error"] = False
	if "last_user_input" not in st.session_state:
		st.session_state["last_user_input"] = None

	def handle_send(user_input):
		llm_handle_send_with_retry(
			user_input,
			messages_key="messages",
			last_user_input_key="last_user_input",
			error_key="error",
			llm_call_fn=call_llm
		)

	def handle_retry():
		llm_handle_retry(
			messages_key="messages",
			last_user_input_key="last_user_input",
			error_key="error",
			handle_send_fn=handle_send
		)

	render_chatgpt_ui(
		st.session_state["messages"],
		input_key="user_input",
		on_send=handle_send,
		on_retry=handle_retry,
		placeholder="Type your message and press Enter"
	)
