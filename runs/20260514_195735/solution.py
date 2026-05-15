def is_palindrome(text: str) -> bool:
    text = ''.join(c for c in text if c.isalnum()).lower()
    return text == text[::-1]