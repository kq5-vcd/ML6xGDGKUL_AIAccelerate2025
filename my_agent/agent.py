"""
This file is where you will implement your agent.
The `root_agent` is used to evaluate your agent's performance.
"""

from google.adk.agents import llm_agent
from my_agent.tools import web_search, pdf_extract, read_block_of_text
from google.adk.tools import FunctionTool

# Wrap functions as tools for ADK
pdf_extract_tool = FunctionTool(
    func=pdf_extract
)

root_agent = llm_agent.Agent(
    model='gemini-2.5-flash-lite',
    name='agent',
    description="A helpful assistant that can answer questions.",
    instruction="You are a helpful assistant that answers questions directly and concisely.",
    tools=[web_search, pdf_extract_tool, read_block_of_text],
    sub_agents=[],
)
