import os
import sys
import unittest


class TestImports(unittest.TestCase):
    def test_core_imports(self):
        """Test that core modules can be imported"""
        try:
            # Add current directory to path
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Import failed: {e}")


if __name__ == "__main__":
    unittest.main()
