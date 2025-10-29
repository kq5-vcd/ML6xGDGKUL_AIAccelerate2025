def read_block_of_text(text_block_string: str) -> str:
    """Reads a single multi-line string input, removes all newlines and whitespace, 
    and joins the text into one continuous string.
    """
    
    # Split the input string into lines (handling different newline types)
    lines_list = text_block_string.splitlines()

    # Strip whitespace from each line and filter out any empty lines (like those from \n\n)
    cleaned_lines = [line.strip() for line in lines_list if line.strip()]
    
    # Join the clean lines together without any separator
    return "".join(cleaned_lines)