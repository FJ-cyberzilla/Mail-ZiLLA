import unittest


class TestMinimal(unittest.TestCase):
    def test_always_passes(self):
        self.assertTrue(True)

    def test_addition(self):
        self.assertEqual(1 + 1, 2)


if __name__ == "__main__":
    unittest.main()
