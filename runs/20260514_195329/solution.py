def is_palindrome(text: str) -> bool:
    text = ''.join(char for char in text if char.isalnum()).lower()
    return len(text) > 0 and text == text[::-1]