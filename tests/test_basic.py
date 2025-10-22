import unittest

class TestBasicSetup(unittest.TestCase):
    """Basic tests to verify the testing environment works"""
    
    def test_addition(self):
        self.assertEqual(1 + 1, 2)
    
    def test_boolean(self):
        self.assertTrue(True)
        self.assertFalse(False)
    
    def test_list(self):
        test_list = [1, 2, 3]
        self.assertEqual(len(test_list), 3)
        self.assertIn(2, test_list)

if __name__ == '__main__':
    unittest.main()
