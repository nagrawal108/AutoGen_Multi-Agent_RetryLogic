from solution import is_palindrome

def test_is_palindrome():
    # Typical cases
    assert is_palindrome("radar") == True
    assert is_palindrome("hello") == False

    # Edge cases
    assert is_palindrome("") == True
    assert is_palindrome("a") == True

    # Punctuation
    assert is_palindrome("A man, a plan, a canal: Panama") == True
    assert is_palindrome("Not a palindrome!") == False

    # Mixed case
    assert is_palindrome("RaDaR") == True
    assert is_palindrome("HeLlO") == False

    # Long string
    assert is_palindrome("a" * 1000) == True
    assert is_palindrome("a" * 1000 + "b") == False

if __name__ == "__main__":
    test_is_palindrome()
    print("All tests passed.")