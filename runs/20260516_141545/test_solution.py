from solution import is_palindrome

def test_empty_string():
    assert is_palindrome("") == True

def test_single_character():
    assert is_palindrome("a") == True

def test_palindrome():
    assert is_palindrome("madam") == True

def test_not_palindrome():
    assert is_palindrome("hello") == False

def test_mixed_case_palindrome():
    assert is_palindrome("Madam") == True

def test_punctuation_palindrome():
    assert is_palindrome("A man, a plan, a canal, Panama") == True

def test_long_palindrome():
    long_string = "a" * 1000
    assert is_palindrome(long_string) == True

def test_long_not_palindrome():
    long_string = "a" * 999 + "b"
    assert is_palindrome(long_string) == False

def test_only_punctuation():
    assert is_palindrome("!@#$") == True

def test_punctuation_and_spaces():
    assert is_palindrome("   !@#   $@!   ") == True

def run_tests():
    test_empty_string()
    test_single_character()
    test_palindrome()
    test_not_palindrome()
    test_mixed_case_palindrome()
    test_punctuation_palindrome()
    test_long_palindrome()
    test_long_not_palindrome()
    test_only_punctuation()
    test_punctuation_and_spaces()
    print("All tests passed.")

if __name__ == "__main__":
    run_tests()