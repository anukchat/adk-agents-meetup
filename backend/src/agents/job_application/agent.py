from google.adk.tools import google_search, load_memory, url_context
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.adk.code_executors import BuiltInCodeExecutor
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StdioServerParameters,
    StdioConnectionParams,
)
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.planners import PlanReActPlanner
from src.agents.deep_research.agent import grounding_callback
from src.agents.job_application.models import CVScreenerOutput, JobPosting
from src.agents.job_application.prompts import JOB_DISCOVERY_PROMPT, SCORER_PROMPT
from src.tools.file_tools import get_file_tools
from src.tools.todo_tools import get_todo_tools
from src.tools.web_tools import get_web_tools
from src.tools.system_tools import get_system_tools


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

# Specialized Sub-Agents

cv_screener_agent = LlmAgent(
    name="cv_screener_agent",
    model="gemini-2.5-flash-lite",
    instruction=(
        "You are the CV Screener Agent. Given a CV/Resume, you will analyze and extract "
        "key information such as skills, experience, and qualifications. "
        "Save output in state['cv_screener_output']."
    ),
    output_schema=CVScreenerOutput,
    output_key="cv_screener_output",
)

search_agent = LlmAgent(
    name="search_agent",
    model="gemini-2.5-flash-lite",
    instruction=(
        "You are the Google Search Specialist. Your job is strictly: "
        "1. Receive a query from the job_discovery_agent. "
        "2. Run the `google_search` tool for that query. "
        "3. Output the results as a list of URLs. Do not analyze or summarize."
    ),
    tools=[google_search],
    after_tool_callback=grounding_callback,
)

browser_agent = LlmAgent(
    name="browser_agent",
    model="gemini-2.5-flash-lite",
    instruction=(
        "You are a specialist in browser operations. You will be given a task to perform "
        "in a browser. You should not make any assumptions about the browser or the task. "
        "You should always list the current URL before and after performing the task."
    ),
    tools=[playwright_tools],
)

code_agent = LlmAgent(
    name="code_agent",
    model="gemini-2.5-flash-lite",
    instruction=(
        "You are a specialist in code execution. You will be given Python code "
        "to execute. You should not make any assumptions about the files "
        "available. Always list the files in the current directory before "
        "attempting to read a file. If any code fails due to a missing package, "
        "automatically install it using `pip install <package>`."
    ),
    code_executor=BuiltInCodeExecutor(error_retry_attempts=3, stateful=True),
)

job_discovery_agent = LlmAgent(
    name="job_discovery_agent",
    model="gemini-2.5-flash-lite",
    instruction=JOB_DISCOVERY_PROMPT,
    tools=[
        AgentTool(search_agent),
        AgentTool(browser_agent),
        AgentTool(code_agent),
        PreloadMemoryTool(),
        load_memory,
    ],
    output_key="job_postings",
)

scorer_agent = LlmAgent(
    name="scorer_agent",
    model="gemini-2.5-flash-lite",
    instruction=SCORER_PROMPT,
)

# Main Assistant Agent
assistant_agent = LlmAgent(
    name="assistant_agent",
    model="gemini-2.5-flash-lite",
    instruction=(
        "You are the Assistant Agent. Your job is to assist users in the job application process by "
        "providing information, answering questions, and coordinating with other agents/tools as needed. "
        "You need to create a step by step plan and call the relevant agents/tools in loop to complete the user's request. "
        "Always follow the sequence: "
        "1. `cv_screener_agent`: First screens the CV and converts to a structured output "
        "2. `job_discovery_agent`: Uses web search, browser and coding agents to search the matching requirements "
        "3. `scorer_agent`: Scores the CV with the available openings and gives a score"
    ),
    tools=[
        AgentTool(cv_screener_agent),
        AgentTool(job_discovery_agent),
        AgentTool(scorer_agent),
    ],
    planner=PlanReActPlanner(),
)

root_agent = assistant_agent