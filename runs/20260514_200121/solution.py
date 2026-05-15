def is_palindrome(text: str) -> bool:
    """
    Checks if the given text is a palindrome.

    Args:
    text (str): The input text to be checked.

    Returns:
    bool: True if the text is a palindrome, False otherwise.
    """
    # Remove non-alphanumeric characters and convert to lowercase
    cleaned_text = ''.join(filter(str.isalnum, text)).lower()

    # Compare the filtered text with its reverse
    return cleaned_text == cleaned_text[::-1]