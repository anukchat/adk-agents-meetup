import os
from dotenv import load_dotenv

load_dotenv()

from google.adk.agents import LlmAgent
from google.adk.planners import PlanReActPlanner
from google.adk.tools import google_search, agent_tool, load_memory
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.adk.code_executors import BuiltInCodeExecutor
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StdioServerParameters,
    StdioConnectionParams,
)

from src.tools.file_tools import get_file_tools
from src.tools.todo_tools import get_todo_tools
from src.tools.web_tools import get_web_tools
from src.tools.system_tools import get_system_tools

from .prompts import SYSTEM_PROMPT

# ----------------------------
file_tools = get_file_tools()
todo_tools = get_todo_tools()
web_tools = get_web_tools()
system_tools = get_system_tools()
playwright_tools = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@executeautomation/playwright-mcp-server"],
        ),
        timeout=100,
    ),
    tool_filter=["*"],  # Optional: "*" means all tools
)

local_tools = file_tools + todo_tools + web_tools + system_tools

def grounding_callback(event) -> list[str]:
    """Extracts the URLs from the search results to be used for grounding."""
    if event.tool_name == "google_search" and event.output:
        grounding_metadata = event.output.get("groundingMetadata", {})
        grounding_chunks = grounding_metadata.get("groundingChunks", [])
        return [chunk["uri"] for chunk in grounding_chunks if "uri" in chunk]
    return []

search_agent = LlmAgent(
    name="search_agent",
    model="gemini-2.5-flash-lite",
    instruction=(
        "You are the Google Search Specialist. Your job is strictly: "
        "1. Receive a query from the Deep_Research_Agent. "
        "2. Run the `google_search` tool for that query. "
        "3. Output the results as a list of URLs. Do not analyze or summarize."
    ),
    tools=[google_search],
    after_tool_callback=grounding_callback,

)

code_agent = LlmAgent(
    name="code_agent",
    model="gemini-2.5-flash-lite",
    instruction=(
        "You are a specialist in code execution. You will be given Python code "
        "to execute. You should not make any assumptions about the files "
        "available. Always list the files in the current directory before "
        "attempting to read a file. If any code fails due to a missing package, automatically install it using `pip install <package>`."
    ),
    code_executor=BuiltInCodeExecutor(error_retry_attempts=3, stateful=True),
)


browser_agent = LlmAgent(
    name="browser_agent",
    model="gemini-2.5-flash-lite",
    instruction="You are a specialist in browser operations. You will be given a task to perform in a browser. You should not make any assumptions about the browser or the task. You should always list the current URL before and after performing the task.",
    tools=[playwright_tools],
)

deep_research_agent = LlmAgent(
    name="Deep_Research_Agent",
    description="A deep research agent that conducts web-backed, evidence-driven investigations.",
    model="gemini-2.5-flash-lite",
    instruction=SYSTEM_PROMPT,
    planner=PlanReActPlanner(),
    tools=local_tools + [
        agent_tool.AgentTool(agent=search_agent),
        agent_tool.AgentTool(agent=code_agent),
        agent_tool.AgentTool(agent=browser_agent),
        PreloadMemoryTool(),
        load_memory
    ],
)

root_agent = deep_research_agent

__all__ = ['deep_research_agent']

