


import streamlit as st
from src.utils.llm import call_llm
from chatgpt_ui import render_chatgpt_ui
from llm_retry_utils import llm_handle_send_with_retry, llm_handle_retry

def main():
	st.title("Resume Summarization with LLM")
	if "messages" not in st.session_state:
		st.session_state["messages"] = []
	if "error" not in st.session_state:
		st.session_state["error"] = False
	if "last_user_input" not in st.session_state:
		st.session_state["last_user_input"] = None

	def handle_send(user_input):
		def llm_call(messages):
			prompt = [
				{"role": "system", "content": (
					"You are an expert resume writer. Read the following resume text and generate a concise, professional summary suitable for the top of a resume. "
					"Highlight the candidate's years of experience, main skills, industries, and key strengths. Limit to 3-5 sentences."
				)},
				{"role": "user", "content": user_input}
			]
			response = call_llm(prompt)
			summary = response.choices[0].message.content
			# Overwrite the last user message with the prompt for retry
			if messages and messages[-1]["role"] == "user":
				messages[-1]["content"] = user_input
			return type('Obj', (object,), {"choices": [type('Choice', (object,), {"message": type('Msg', (object,), {"content": f"Resume Summary: {summary.strip()}"})()})()]})()
		llm_handle_send_with_retry(
			user_input,
			messages_key="messages",
			last_user_input_key="last_user_input",
			error_key="error",
			llm_call_fn=llm_call
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
		input_key="user_input_summarize",
		on_send=handle_send,
		on_retry=handle_retry,
		placeholder="Paste resume text to generate a professional summary"
	)
