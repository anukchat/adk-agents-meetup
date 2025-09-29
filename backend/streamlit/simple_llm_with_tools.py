"""
LLM Chat with Web Search Tool (Function Calling)
"""

import streamlit as st
import json
from src.utils.llm import call_llm
from src.tools.serper_search import serper_search
from chatgpt_ui import render_chatgpt_ui
from llm_retry_utils import llm_handle_retry


def web_search(query: str) -> str:
    """Web search using SERPER API."""
    result = serper_search(query)
    if "organic" in result and isinstance(result["organic"], list):
        output = []
        for item in result["organic"]:
            link = item.get("link", "")
            snippet = item.get("snippet", "")
            output.append({"Link": link, "Snippet": snippet})
        return output
    return result.get("organic", {}).get("snippet", "[No result]")


# Define the OpenAI function tool schema for function calling
WEB_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Web search using SERPER API to find current information on the web.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string", 
                    "description": "The search query to find relevant information."
                }
            },
            "required": ["query"]
        }
    }
}


def main():

    st.title("💬 LLM Chat with Web Search Tool")
    if "messages" not in st.session_state:
        # Add system prompt as the first message
        st.session_state["messages"] = [{
            "role": "system",
            "content": (
                "You are a helpful assistant that can use web search to answer user queries. "
                "If you need current information or facts you're not sure about, use the web_search tool. "
                "Provide a detailed and accurate answer."
            )
        }]
    if "error" not in st.session_state:
        st.session_state["error"] = False
    if "last_user_input" not in st.session_state:
        st.session_state["last_user_input"] = None

    def handle_send(user_input):
        st.session_state["messages"].append({"role": "user", "content": user_input})
        st.session_state["last_user_input"] = user_input
        try:
            with st.spinner("LLM is thinking..."):
                response = call_llm(
                    st.session_state["messages"],
                    tools=[WEB_SEARCH_TOOL]
                )
                msg = response.choices[0].message
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    st.session_state["messages"].append({
                        "role": "assistant",
                        "content": msg.content,
                        "tool_calls": msg.tool_calls
                    })
                    for tool_call in msg.tool_calls:
                        if tool_call.function.name == "web_search":
                            args = json.loads(tool_call.function.arguments)
                            tool_result = web_search(args["query"])
                            if isinstance(tool_result, list):
                                formatted_result = "\n\n".join([
                                    f"**Source:** [{item['Link']}]({item['Link']})\n{item['Snippet']}" 
                                    for item in tool_result[:5]
                                ])
                            else:
                                formatted_result = str(tool_result)
                            st.session_state["messages"].append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": "web_search",
                                "content": formatted_result
                            })
                    # Final LLM call after tool result
                    response2 = call_llm(
                        st.session_state["messages"],
                        tools=[WEB_SEARCH_TOOL]
                    )
                    content = response2.choices[0].message.content
                    st.session_state["messages"].append({
                        "role": "assistant",
                        "content": content
                    })
                else:
                    st.session_state["messages"].append({
                        "role": "assistant",
                        "content": msg.content
                    })
            st.session_state["error"] = False
        except Exception as e:
            st.session_state["messages"].append({
                "role": "assistant",
                "content": f"Error: {str(e)}",
                "is_error": True
            })
            st.session_state["error"] = True

    def handle_retry():
        llm_handle_retry(
            messages_key="messages",
            last_user_input_key="last_user_input",
            error_key="error",
            handle_send_fn=handle_send
        )

    # Only show non-system messages in the UI
    ui_messages = [m for m in st.session_state["messages"] if m.get("role") != "system"]
    render_chatgpt_ui(
        messages=ui_messages,
        input_key="user_input_tools",
        on_send=handle_send,
        on_retry=handle_retry,
        placeholder="Ask me anything... I can search the web if needed!"
    )