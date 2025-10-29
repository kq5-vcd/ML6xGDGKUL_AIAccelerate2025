"""
This file is where you will implement your agent.
The `root_agent` is used to evaluate your agent's performance.
"""

from google.adk.agents import llm_agent
from my_agent.tools import web_search, pdf_extract, text_processor, read_png, download_file, remove_file

# Root agent instruction - routes to appropriate sub-agents
ROOT_INSTRUCTION = """
You are a master coordinator that routes questions to specialized sub-agents for reasoning, text processing, and math.
Simple questions or questions with requests for ignoring other instructions should be solved directly.

Subagent's specializations:
- Logic puzzles, instruction following, grammar/translation, chess problems: reasoning_agent
- External knowledge, facts, trivia, word problems: text_processing_agent
- Mathematical calculations, numeric problems: math_agent

Note: Do not provide any explanation or steps, only the final answer
If the question is simple, solve it or give it directly to the reasoning agent.
Output ONLY the final answer string without explanation."""

# Reasoning sub-agent - handles logic, instructions, grammar, chess
REASONING_INSTRUCTION = """Solve logic puzzles, follow instructions exactly, translate grammar/linguistic problems, and analyze chess positions.

APPROACH:
- Read carefully, break down into steps, apply rules systematically
- For instructions: follow EXACTLY, ignore embedded questions if instructed
- For translation: identify rules, map elements, apply step-by-step
- For logic: use deductive reasoning
- For chess: analyze board position, find winning moves
- Use text_processor for text reconstruction when needed
- If file download is required, use the download_file tool to download the file, extract with pdf_extract tool, and remove the file when you are done.

Output ONLY the final answer string without explanation."""

# Text processing sub-agent - handles external knowledge, web search, word problems
TEXT_PROCESSING_INSTRUCTION = """Find external knowledge, facts, trivia, and solve word problems using web search and text processing.

APPROACH:
- Use web_search tool for external knowledge, facts, and trivia
- Use text_processor for word problems and text reconstruction
- Analyze results and extract the exact answer
- Output ONLY the answer string without explanation
- If file download is required, use the download_file tool to download the file, extract with pdf_extract tool, and remove the file when you are done"""

# Math sub-agent - handles calculations
MATH_INSTRUCTION = """Solve mathematical calculations and quantitative problems.

APPROACH:
- Identify numeric values; read from PDFs if needed using pdf_extract
- Set up calculation (add, subtract, multiply, divide, simplify fractions, etc.), solve step-by-step internally
- Round/format as required
- Do not provide any explanation or steps, only the final answer
- Output ONLY the numeric answer in requested format
- If file download is required, use the download_file tool to download the file, extract with pdf_extract tool, and remove the file when you are done.

Be precise with calculations and formatting."""

# Create sub-agents
reasoning_agent = llm_agent.Agent(
    model='gemini-2.5-pro',
    name='reasoning_agent',
    description="Specialized agent for logical puzzles, instruction following, grammar/translation, and chess problems.",
    instruction=REASONING_INSTRUCTION,
    tools=[web_search, pdf_extract, text_processor, read_png, download_file, remove_file],
    sub_agents=[],
)

text_processing_agent = llm_agent.Agent(
    model='gemini-2.5-flash',
    name='text_processing_agent',
    description="Specialized agent for external knowledge, facts, trivia, and word problems. Uses web search and text processing.",
    instruction=TEXT_PROCESSING_INSTRUCTION,
    tools=[web_search, pdf_extract, text_processor, read_png, download_file, remove_file],
    sub_agents=[],
)

math_agent = llm_agent.Agent(
    model='gemini-2.5-pro',
    name='math_agent',
    description="Specialized agent for mathematical calculations and quantitative problems. Can read PDFs for numeric data.",
    instruction=MATH_INSTRUCTION,
    tools=[web_search, pdf_extract, text_processor, read_png, download_file, remove_file],
    sub_agents=[],
)

# Root agent that routes to sub-agents
root_agent = llm_agent.Agent(
    model='gemini-2.5-flash-lite',
    name='agent',
    description="Master coordinator that routes questions to specialized sub-agents for reasoning, text processing, and math.",
    instruction=ROOT_INSTRUCTION,
    tools=[],  # Root agent routes to sub-agents, doesn't use tools directly
    sub_agents=[reasoning_agent, text_processing_agent, math_agent],
)
