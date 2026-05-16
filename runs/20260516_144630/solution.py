def is_palindrome(text: str) -> bool:
    text = ''.join(filter(str.isalnum, text)).lower()
    return text == text[::-1]