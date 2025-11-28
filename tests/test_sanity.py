import os
import sys
import unittest


class TestSanity(unittest.TestCase):
    """Sanity checks to verify basic setup and imports"""

    def test_imports(self):
        """Test that core modules can be imported without syntax errors"""
        try:
            # Add project root to Python path
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            
            # Attempt to import a few key modules
            import core.config
            import api.main
            import database.db
            import monitoring.logging_config
            import monitoring.health_checks
            import monitoring.alerts
            import monitoring.metrics
            
            self.assertTrue(True, "Key modules imported successfully")
        except Exception as e:
            self.fail(f"Import failed for core modules: {e}")

    def test_basic_arithmetic(self):
        """Verify basic arithmetic operations"""
        self.assertEqual(1 + 1, 2)
        self.assertEqual(5 * 5, 25)
        self.assertNotEqual(10 - 3, 6)

    def test_boolean_logic(self):
        """Verify basic boolean logic"""
        self.assertTrue(True)
        self.assertFalse(False)
        self.assertIs(True, not False)
        self.assertIsNot(False, True)

    def test_list_operations(self):
        """Verify basic list operations"""
        test_list = [1, 2, 3]
        self.assertEqual(len(test_list), 3)
        self.assertIn(2, test_list)
        self.assertNotIn(4, test_list)
        self.assertListEqual([1, 2, 3], [1, 2, 3])


if __name__ == "__main__":
    unittest.main()