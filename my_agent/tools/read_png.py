

import os
import dotenv

from google import genai
from google.genai import types

# Load environment variables from .env file
dotenv.load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

def read_png(file_path: str) -> str:
    """Reads a PNG file and returns the content as a string.
    If you are provided a file path to a .PNG file, you MUST invoke this tool to
    read the file and use the content to answer the question.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The content of the file.
    """
    # TODO: Improve this function and add functions for other types.
    if client is None:
        raise ValueError(
            "GOOGLE_API_KEY environment variable is not set. "
            "Please set it before using this function."
        )
    
    with open(file_path, 'rb') as file:
        file_content = file.read()

    response = client.models.generate_content(
        model='gemini-2.5-flash-lite',
        contents=[
        types.Part.from_bytes(
            data=file_content,
            mime_type='image/png',
        ),
        'Describe this image in great detail.'
        ]
    )

    return response.text

if __name__ == "__main__":
    print(read_png("benchmark/attachments/11.png"))
