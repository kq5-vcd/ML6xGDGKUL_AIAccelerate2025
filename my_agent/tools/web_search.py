# my_agent/tools/web_search.py

from serpapi import GoogleSearch
from google import genai
import os
import dotenv
from pathlib import Path
from typing import Dict, Any, List

# Load environment variables
dotenv.load_dotenv()

SERP_API_KEY = os.getenv("SERP_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize Gemini client
client = genai.Client(api_key=GOOGLE_API_KEY)

# Prompts
QUERY_TRANSFORM_PROMPT = """Transform questions into effective search queries.
Remove question words and focus on key terms."""

ANSWER_EXTRACTION_PROMPT = """Answer the question based only on the provided context.
Answer format: only extract the meaningful English word from the context and relevant to the question.
"""

# Core helper
def extract(prompt: str, content: str, model: str = "gemini-2.5-flash") -> str:
    try:
        response = client.models.generate_content(
            model=model,
            contents=f"{prompt}\n\n{content}"
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error in extract: {e}")
        return ""

def generate_search_query(question: str) -> str:
    try:
        result = extract(QUERY_TRANSFORM_PROMPT, question, model="gemini-2.5-pro")
        return result
    except Exception as e:
        print(f"Error in transform_query: {e}")

def search_google(query: str) -> Dict[str, Any]:
    try:
        search = GoogleSearch({"q": query, "api_key": SERP_API_KEY, "num": 10})
        return search.get_dict()
    except Exception as e:
        print(f"Error searching: {e}")
        return {"error": str(e)}

def get_ai_overview(query: str) -> List[str]:
    try:
        search = GoogleSearch({"q": query, "api_key": SERP_API_KEY})
        results = search.get_dict()

        if "ai_overview" not in results or "page_token" not in results["ai_overview"]:
            return []

        ai_search = GoogleSearch({
            "engine": "google_ai_overview",
            "page_token": results["ai_overview"]["page_token"],
            "api_key": SERP_API_KEY
        })
        ai_results = ai_search.get_dict()

        if "ai_overview" in ai_results and "text_blocks" in ai_results["ai_overview"]:
            return [block["snippet"] for block in ai_results["ai_overview"]["text_blocks"] if "snippet" in block]

        return []
    except:
        return []

def extract_snippets(results: Dict[str, Any]) -> List[Dict[str, str]]:
    snippets = []

    if "answer_box" in results and "snippet" in results["answer_box"]:
        snippets.append({
            "title": results["answer_box"].get("title", "Featured Snippet"),
            "snippet": results["answer_box"]["snippet"],
            "link": results["answer_box"].get("link", "")
        })

    if "knowledge_graph" in results and "description" in results["knowledge_graph"]:
        snippets.append({
            "title": results["knowledge_graph"].get("title", "Knowledge Graph"),
            "snippet": results["knowledge_graph"]["description"],
            "link": ""
        })

    for result in results.get("organic_results", []):
        if "snippet" in result:
            snippets.append({
                "title": result.get("title", ""),
                "snippet": result["snippet"],
                "link": result.get("link", "")
            })

    return snippets

def extract_answer(question: str, snippets: List[Dict[str, str]]) -> str:
    if not snippets:
        return "No search results found."

    context_parts = []
    for i, s in enumerate(snippets[:10], 1):
        context_parts.append(f"[{i}] Title: {s['title']}\nContent: {s['snippet']}")

    context = "\n\n".join(context_parts)
    content = f"Question: {question}\n\nContext:\n{context}"

    answer = extract(ANSWER_EXTRACTION_PROMPT, content)

    return answer if answer else "Could not extract answer."

def web_search(query: str) -> Dict[str, Any]:
    """
    Search the web for the given query and return the results.

    Args:
        query: The query to search for.

    Returns:
        A dictionary containing the search query, results, and answer.
    """
    try:
        search_query = generate_search_query(query)
        print(f"Query: '{query}' → '{search_query}'")

        search_results = search_google(search_query)
        snippets = extract_snippets(search_results)

        ai_snippets = get_ai_overview(search_query)
        for ai_snippet in ai_snippets:
            snippets.insert(0, {"title": "AI Overview", "snippet": ai_snippet, "link": ""})

        print(f"Found {len(snippets)} snippets ({len(ai_snippets)} AI overview)")

        answer = extract_answer(query, snippets)

        return {
            "search_query": search_query,
            "results": snippets,
            "answer": answer
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            "search_query": query,
            "results": [],
            "answer": f"Error: {e}",
            "error": str(e)
        }

if __name__ == "__main__":
    test_questions = [
        "In Series 9, Episode 11 of Doctor Who, the Doctor is trapped inside an ever-shifting maze. What is this location called in the official script for the episode?",
        #"What is the capital of France?",
        #"What is the name of the teacher of Princess Carolyn's future descendant?",
    ]

    for question in test_questions:
        print(f"\n{'='*80}\n{question}\n{'='*80}")
        results = web_search(question)
        print(f"\nSearch: {results['search_query']}")
        print(f"Answer: {results['answer']}")
        print(f"Results: {len(results['results'])}")