import unittest
from shared.constants import STATUS_HEALTHY, TRIAGE_LEVELS

class TestConstants(unittest.TestCase):
    def test_constants(self):
        self.assertEqual(STATUS_HEALTHY, "HEALTHY")
        self.assertIn("RED", TRIAGE_LEVELS)

if __name__ == "__main__":
    unittest.main()
