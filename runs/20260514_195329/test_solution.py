from solution import is_palindrome

def test_empty_string():
    assert is_palindrome("") == True

def test_single_character():
    assert is_palindrome("a") == True

def test_palindrome():
    assert is_palindrome("madam") == True

def test_not_palindrome():
    assert is_palindrome("hello") == False

def test_mixed_case():
    assert is_palindrome("Madam") == True

def test_punctuation():
    assert is_palindrome("A man, a plan, a canal: Panama") == True

def test_long_string():
    assert is_palindrome("Was it a car or a cat I saw") == True

def test_numbers():
    assert is_palindrome("12321") == True

def test_special_characters():
    assert is_palindrome("!@#$%^&*()") == False

def test_whitespace():
    assert is_palindrome("   ") == True

# Run tests
test_empty_string()
test_single_character()
test_palindrome()
test_not_palindrome()
test_mixed_case()
test_punctuation()
test_long_string()
test_numbers()
test_special_characters()
test_whitespace()