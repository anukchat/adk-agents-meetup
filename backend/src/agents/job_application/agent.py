import sys
import os
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from google.adk.models.lite_llm import LiteLlm  # For multi-model support
from google.adk.tools.agent_tool import AgentTool
from google.adk.code_executors import BuiltInCodeExecutor
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StdioServerParameters,
    StdioConnectionParams,
)
from google.adk.agents import LlmAgent
from google.adk.planners import PlanReActPlanner
from src.agents.job_application.models import CVScreenerOutput
from src.agents.job_application.prompts import JOB_DISCOVERY_PROMPT, SCORER_PROMPT, CV_SCREENER_PROMPT
from src.tools.file_tools import get_file_tools
from src.tools.todo_tools import get_todo_tools
from src.tools.web_tools import get_web_tools
from src.tools.system_tools import get_system_tools
from src.tools.serper_search import get_serper_tools


file_tools = get_file_tools()
todo_tools = get_todo_tools()
web_tools = get_web_tools()
system_tools = get_system_tools()
serper_tools = get_serper_tools()
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
    description="A CV Screener Agent that screens the candidate's profile and extracts the relevant information. Accepts candidate profile as input and returns the candidate's profile in a structured format as per provided output schema",
    model=LiteLlm(model="openai/gemini-2.5-pro"),
    instruction=CV_SCREENER_PROMPT,
    output_schema=CVScreenerOutput
)

search_agent = LlmAgent(
    name="search_agent",
    description="A Search Agent that searches the web for job postings. Accepts a query and returns the results as a list of URLs",
    model=LiteLlm(model="openai/gemini-2.5-pro"),
    instruction=(
        "You are the Search Specialist. Your job is strictly: "
        "1. Receive a query from the job_discovery_agent. "
        "2. Run the `serper_search` tool for that query. "
        "3. Output the results as a list of URLs. Do not analyze or summarize."
    ),
    tools=serper_tools,
    disallow_transfer_to_parent=False

)

browser_agent = LlmAgent(
    name="browser_agent",
    description="A Browser Agent that navigates to job postings and extracts the relevant information. Accepts a URL and returns the relevant information",
    model=LiteLlm(model="openai/gemini-2.5-pro"),
    instruction=(
        "You are a specialist in browser operations. You will be given a task to perform "
        "in a browser. You should not make any assumptions about the browser or the task. "
        "You should always list the current URL before and after performing the task."
    ),
    tools=[playwright_tools],
    disallow_transfer_to_parent=False

)

code_agent = LlmAgent(
    name="code_agent",
    description="A Code Agent that executes code to download the job postings and extract the relevant information. Accepts a code and returns the results",
    model=LiteLlm(model="openai/gemini-2.5-pro"),
    instruction=(
        "You are a specialist in code execution. You will be given Python code "
        "to execute. You should not make any assumptions about the files "
        "available. Always list the files in the current directory before "
        "attempting to read a file. If any code fails due to a missing package, "
        "automatically install it using `pip install <package>`."
    ),
    code_executor=BuiltInCodeExecutor(error_retry_attempts=3, stateful=True),
    disallow_transfer_to_parent=False
)

job_discovery_agent = LlmAgent(
    name="job_discovery_agent",
    description="A Job Discovery Agent that searches the web, does browser navigation and has coding abilities to accurately find job postings.",
    model=LiteLlm(model="openai/gemini-2.5-pro"),
    instruction=JOB_DISCOVERY_PROMPT,
    tools=[AgentTool(search_agent), AgentTool(browser_agent), AgentTool(code_agent)]
)

scorer_agent = LlmAgent(
    name="scorer_agent",
    description="A Scorer Agent that scores the CV with the available openings and gives a score, returns the detailed scoring report.",
    model=LiteLlm(model="openai/gemini-2.5-pro"),
    instruction=SCORER_PROMPT,
)

# Main Assistant Agent
assistant_agent = LlmAgent(
    name="assistant_agent",
    description="An Assistant Agent that assists users in the job application process by providing information, answering questions, and coordinating with other agents/tools as needed.",
    model=LiteLlm(model="openai/gemini-2.5-pro"),
    instruction=(
        "You are the Assistant Agent. Your job is to assist users in the job application process by "
        "providing information, answering questions, and coordinating with other agents/tools as needed. "
        "First you need to analyze the user's request and understand the user's intent. Then ask for additional information if needed. including user preferences for job search (like location, industry etc.)"
        "You need to create a step by step plan and call the relevant agents/tools in loop to complete the user's request. "
        "Always follow the sequence: "
        "1. `cv_screener_agent`: First screens the CV and converts to a structured output "
        "2. `job_discovery_agent`: Uses web search, browser and coding agents to search the matching requirements "
        "3. `scorer_agent`: Scores the CV with the available openings and gives a score, returns the detailed scoring report,"
        "Finally, you need to generate the scoring report for all job postings"
        "Return in a markdown format with the following details for all job postings: "
        "- Job Title"
        "- Company"
        "- Job URL"
        "- Location"
        "- Job Description"
        "- Requirements"
        "- Score"  
        "- Reasoning"
        "Always make sure to review before returning the output, if the profile is correctly matched with the job postings. Do understand the reasoning for the score. and provide a recommendation for the candidate on which job postings to prioritize for application."
    ),
    tools=[
        AgentTool(cv_screener_agent),
        AgentTool(job_discovery_agent),
        AgentTool(scorer_agent),
    ],
    planner=PlanReActPlanner(),
)

root_agent = assistant_agent
