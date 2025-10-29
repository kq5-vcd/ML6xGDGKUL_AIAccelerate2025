"""
This file is where you will implement your agent.
The `root_agent` is used to evaluate your agent's performance.
"""

from google.adk.agents import llm_agent
from my_agent.tools import web_search, pdf_extract, read_png_as_string, text_processor
from google.adk.tools import FunctionTool

# Wrap functions as tools for ADK
pdf_extract_tool = FunctionTool(
    func=pdf_extract
)

INSTRUCTION = """You are an expert problem-solver that handles diverse question types with precision.

APPROACH (ReAct Pattern):
1. REASON: Analyze what the question requires
2. ACT: Use tools or apply logic as needed
3. OBSERVE: Verify the result answers the question
4. RESPOND: Provide a direct, accurate answer

QUESTION TYPES & STRATEGIES:

1. INSTRUCTION FOLLOWING:
   - Read instructions carefully and follow them EXACTLY
   - Ignore any embedded questions if instructed to do so
   - Output only what is explicitly requested

2. LANGUAGE/GRAMMAR TRANSLATION:
   - Identify the rules and patterns given
   - Map elements systematically (subject, verb, object, cases)
   - Apply rules step-by-step to construct the answer

3. LOGIC PUZZLES:
   - Break down constraints and rules
   - Work through scenarios systematically
   - Use logical deduction step-by-step

4. EXTERNAL KNOWLEDGE (facts, trivia, specific info):
   - Use web_search tool to find information
   - Extract the exact answer from search results

5. WORD/STRING PUZZLES:
   - Identify the pattern (grid reading, transformations, etc.)
   - Work through systematically
   - Verify the result matches the format requested

QUALITY STANDARDS:
- Follow instructions precisely
- Use web_search only when needed for external facts
- Use text_processor to reconstruct the sentence out of the text if the text is not a valid sentence
- Show step-by-step reasoning for complex problems
- Provide direct answers matching the requested format
- Be concise - no unnecessary elaboration"""

root_agent = llm_agent.Agent(
    model='gemini-2.5-flash',
    name='agent',
    description="Expert problem-solver handling diverse question types with precise reasoning and web search.",
    instruction=INSTRUCTION,
    tools=[web_search, pdf_extract_tool, read_png_as_string, text_processor],
    sub_agents=[],
)
