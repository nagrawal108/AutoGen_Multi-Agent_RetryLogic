def is_palindrome(text: str) -> bool:
    text = ''.join(char for char in text if char.isalnum()).lower()
    return text == text[::-1]