


import streamlit as st
from src.utils.llm import call_llm
from chatgpt_ui import render_chatgpt_ui
from llm_retry_utils import llm_handle_send_with_retry, llm_handle_retry
import json as pyjson

def main():
	st.title("Structured Extraction with LLM")
	if "messages" not in st.session_state:
		st.session_state["messages"] = []
	if "error" not in st.session_state:
		st.session_state["error"] = False
	if "last_user_input" not in st.session_state:
		st.session_state["last_user_input"] = None


	# Resume extraction schema
	SCHEMA = {
		"summary": "string",
		"category": "string",  # e.g. HR, Marketing, Medical, etc.
		"skills": ["string"],
		"experience_years": "number",
		"roles": ["string"],
		"top_companies": ["string"]
	}


	def handle_send(user_input):
		def llm_call(messages):
			prompt = [
				{"role": "system", "content": (
					"You are an expert resume parser. Extract the following structured fields from the resume text and return a JSON object with this schema: "
					"{\n"
					"  'summary': string,\n"
					"  'category': string,\n"
					"  'skills': list of strings,\n"
					"  'experience_years': number,\n"
					"  'roles': list of strings,\n"
					"  'top_companies': list of strings\n"
					"}.\n"
					"- 'summary': A concise summary of the candidate.\n"
					"- 'category': The main professional category (e.g. HR, Marketing, Medical, etc).\n"
					"- 'skills': List of key skills.\n"
					"- 'experience_years': Total years of professional experience (estimate if needed).\n"
					"- 'roles': List of unique job titles/roles held.\n"
					"- 'top_companies': List of top companies/organizations worked at.\n"
					"If a field is not present, use an empty string or empty list. Respond with only the JSON."
				)},
				{"role": "user", "content": user_input}
			]
			response = call_llm(prompt)
			result = response.choices[0].message.content
			# Overwrite the last user message with the prompt for retry
			if messages and messages[-1]["role"] == "user":
				messages[-1]["content"] = user_input
			return type('Obj', (object,), {"choices": [type('Choice', (object,), {"message": type('Msg', (object,), {"content": result.strip()})()})()]})()
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
		input_key="user_input_extract",
		on_send=handle_send,
		on_retry=handle_retry,
		placeholder="Paste a resume to extract structured fields (skills, roles, summary, etc) as JSON"
	)
