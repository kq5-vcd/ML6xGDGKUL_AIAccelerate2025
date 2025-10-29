"""
This file is where you will implement your agent.
The `root_agent` is used to evaluate your agent's performance.
"""

from google.adk.agents import llm_agent
from my_agent.tools import web_search, pdf_extract
from google.adk.tools import FunctionTool

# Wrap functions as tools for ADK
pdf_extract_tool = FunctionTool(
    func=pdf_extract
)

root_agent = llm_agent.Agent(
    model='gemini-2.5-flash-lite', #TODO
    name='agent',
    description="A helpful assistant that can answer questions.",
    instruction="You are a helpful assistant that answers questions directly and concisely.",  # TODO
    tools=[web_search, pdf_extract_tool],  # TODO
    sub_agents=[],
)
