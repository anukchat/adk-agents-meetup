

# Minimal LiteLLM-based LLM client (supports OpenAI, Gemini, Azure, etc.)
import os
from dotenv import load_dotenv
import litellm

load_dotenv()


def call_llm(messages, model=None, tools=None, tool_choice="auto", **kwargs):
    """
    Call an LLM using LiteLLM (supports OpenAI, Gemini, Groq, Anthropic, etc.).
    Args:
        messages (list): List of dicts with 'role' and 'content'.
        model (str): Model name (e.g., 'gpt-3.5-turbo', 'gemini/gemini-pro').
        tools (list): OpenAI-style function/tool definitions.
        tool_choice (str): 'auto', 'none', or function name.
        **kwargs: Extra params for the API.
    Returns:
        dict: API response from litellm.completion()
    """
    model = model or os.getenv("LITELLM_MODEL", "gpt-3.5-turbo")
    params = {
        "model": model,
        "messages": messages,
    }
    if tools:
        params["tools"] = tools
        params["tool_choice"] = tool_choice
    params.update(kwargs)
    return litellm.completion(**params)


if __name__ == "__main__":
	# Simple test
	test_messages = [
		{"role": "system", "content": "You are a helpful assistant."},
		{"role": "user", "content": "Hello, who won the world series in 2020?"}
	]
	# Example: OpenAI
	response = call_llm(test_messages)
	print("OpenAI:", response["choices"][0]["message"]["content"])

	# Example: Tool/function calling
	tools = [
		{
			"type": "function",
			"function": {
				"name": "get_weather",
				"description": "Get the current weather in a location",
				"parameters": {
					"type": "object",
					"properties": {
						"location": {"type": "string", "description": "City and state"},
						"unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
					},
					"required": ["location"]
				}
			}
		}
	]
	tool_messages = [
		{"role": "user", "content": "What's the weather in Boston?"}
	]
	response = call_llm(tool_messages, tools=tools, tool_choice="auto")
	print("Tool call:", response)