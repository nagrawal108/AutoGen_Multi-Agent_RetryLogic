import unittest
from solution import is_palindrome

class TestIsPalindrome(unittest.TestCase):
    def test_simple_palindrome(self):
        self.assertTrue(is_palindrome("madam"))

    def test_not_palindrome(self):
        self.assertFalse(is_palindrome("hello"))

    def test_empty_string(self):
        self.assertTrue(is_palindrome(""))

    def test_single_character(self):
        self.assertTrue(is_palindrome("a"))

    def test_punctuation(self):
        self.assertTrue(is_palindrome("A man, a plan, a canal: Panama"))
        self.assertTrue(is_palindrome("Was it a car or a cat I saw?"))

    def test_mixed_case(self):
        self.assertTrue(is_palindrome("Able was I ere I saw Elba"))
        self.assertTrue(is_palindrome("A Santa at NASA"))

    def test_long_string(self):
        long_palindrome = "a" * 1000
        self.assertTrue(is_palindrome(long_palindrome))
        long_not_palindrome = "a" * 999 + "b"
        self.assertFalse(is_palindrome(long_not_palindrome))

if __name__ == '__main__':
    unittest.main()