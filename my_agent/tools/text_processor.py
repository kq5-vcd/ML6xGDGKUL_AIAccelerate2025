"""
Text reconstruction tool for splitting concatenated text into proper words.

This tool takes text chunks (strings without spaces) and reconstructs them
into readable sentences by intelligently inserting word boundaries.
"""

import wordninja


def text_processor(text_chunk: str) -> str:
    """
    Reconstructs a sentence from a text chunk by inserting spaces between words.
    """
    # Normalize input to string (handle edge cases)
    if isinstance(text_chunk, list):
        # If list provided, join into single string
        combined_text = ''.join(str(line).strip() for line in text_chunk).lower()
    elif isinstance(text_chunk, str):
        combined_text = text_chunk.strip().lower()
    else:
        # Convert to string if needed
        combined_text = str(text_chunk).strip().lower()
    
    # Split the concatenated text into words using wordninja
    words = wordninja.split(combined_text)
    
    # Reconstruct the sentence
    sentence = ' '.join(words)
    
    # Capitalize first letter
    sentence = sentence.capitalize()
    
    # Add period if missing
    if not sentence.endswith('.'):
        sentence += '.'
    
    return sentence


# Test cases
if __name__ == "__main__":
    # Test with single string
    test_string = "THESEAGULLGLIDEDPEACEFULLYTOMYCHAIR"
    result = text_processor(test_string)
    print(f"Input: {test_string}")
    print(f"Output: {result}")
    
    print("\n" + "="*60 + "\n")
    
    # Test with list of strings
    test_list = ["THESE", "AGULL", "GLIDE", "DPEAC", "EFULL", "YTOMY", "CHAIR"]
    result = text_processor(test_list)
    print(f"Input: {test_list}")
    print(f"Output: {result}")
