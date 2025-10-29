# my_agent/tools/web_search.py

from serpapi import GoogleSearch
from google import genai
import os
import dotenv
from pathlib import Path
from typing import Dict, Any, List

# Load environment variables
dotenv_path = Path(__file__).parent.parent / ".local_env"
dotenv.load_dotenv(dotenv_path)

# Config
#SERP_API_KEY = "86a458c9d4ca871b4e1d1d3e3d00620cf6c85abc9b58b26535fe9b2675defb1d"
SERP_API_KEY = os.getenv("SERPER_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


# Initialize Gemini client
client = genai.Client(api_key=GOOGLE_API_KEY)

# Prompts
QUERY_TRANSFORM_PROMPT = """Transform questions into effective search queries.

Rules:
1. Remove generic question words (what, who, where, when, why, how)
2. KEEP source/authority words: script, official, documentation, specification, manual
3. KEEP identity/descriptor words: name, called, location, titled, referred to as
4. KEEP technical terms, proper nouns, and unique identifiers exactly as stated
5. KEEP episode/chapter/section numbers and specific references

Goal: Create queries that would appear in authoritative sources answering this question.

Examples:
"What is the capital of Turkey?" → "capital France"
"What is caffeine's molecular formula?" → "caffeine molecular formula"
"In the Python docs, what's the exception handling method?" → "Python documentation exception handling method"
"

Transform this question:"""

ANSWER_EXTRACTION_PROMPT = """Answer the question based only on the provided context.
Be concise and direct. If the context contains the exact answer, quote it directly.
Pay special attention to names, locations, and specific terminology mentioned in the context.
If you can't answer with confidence based on the context, say "I don't have enough information."
Don't make up information or draw conclusions not supported by the context."""

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

def transform_query(question: str) -> str:
    """Transform question to concise search query, focusing on key terms."""
    try:
        # Use the model for query transformation
        result = extract(QUERY_TRANSFORM_PROMPT, question, model="gemini-2.5-flash")

        # If result is too long (over 10 words), try to shorten it
        words = result.split()
        if len(words) > 10:
            # Keep only essential terms
            result = " ".join(words[:10])

        return result if result else question.replace("?", "").strip()
    except Exception as e:
        print(f"Error in transform_query: {e}")
        # Simple fallback - extract key nouns and proper nouns
        words = question.replace("?", "").split()
        # Keep words that start with uppercase (likely proper nouns) and longer words
        important_words = [w for w in words if (w[0].isupper() if w else False) or len(w) > 5]
        return " ".join(important_words[:7]) if important_words else question.replace("?", "").strip()

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

    answer = extract(ANSWER_EXTRACTION_PROMPT, content, model="gemini-2.5-flash")

    return answer if answer else "Could not extract answer."

def web_search(query: str) -> Dict[str, Any]:
    """Performs web search and returns results with extracted answer."""
    try:
        search_query = transform_query(query)
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
        "What is the capital of France?",
    ]

    for question in test_questions:
        print(f"\n{'='*80}\n{question}\n{'='*80}")
        results = web_search(question)
        print(f"\nSearch: {results['search_query']}")
        print(f"Answer: {results['answer']}")
        print(f"Results: {len(results['results'])}")