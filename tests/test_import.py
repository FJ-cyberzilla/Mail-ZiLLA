import unittest
import sys
import os

class TestImports(unittest.TestCase):
    def test_core_imports(self):
        """Test that core modules can be imported"""
        try:
            # Add current directory to path
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from core.base_agent import BaseAgent, ProfileData, Platform
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Import failed: {e}")

if __name__ == '__main__':
    unittest.main()
