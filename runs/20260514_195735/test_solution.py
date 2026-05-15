from solution import is_palindrome

def test_is_palindrome():
    # Typical cases
    assert is_palindrome("madam") == True
    assert is_palindrome("hello") == False

    # Edge cases
    assert is_palindrome("") == True  # Empty string
    assert is_palindrome("a") == True  # Single character
    assert is_palindrome("A") == True  # Single character, uppercase

    # Mixed case and punctuation
    assert is_palindrome("A man, a plan, a canal: Panama") == True
    assert is_palindrome("Was it a car or a cat I saw?") == True
    assert is_palindrome("No 'x' in Nixon") == True

    # Long string
    long_string = "a" * 1000
    assert is_palindrome(long_string) == True
    assert is_palindrome(long_string + "b") == False

if __name__ == "__main__":
    test_is_palindrome()
    print("All tests passed.")