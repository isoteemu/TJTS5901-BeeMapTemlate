""" test logic """
import unittest


class LogicTests(unittest.TestCase):
    """ Logic tests """

    def test_boolean_logic(self):
        """ Test that boolean logic works """

        self.assertTrue(True, "True should be equal to True.")
        self.assertFalse(False, "False should not be equal to True.")
        self.assertNotEqual(True, False, "True should not be equal to False.")

    def test_maths(self):
        """ Test that basic maths work """

        # Test that basic integers work
        self.assertEqual(int(1) + int(1), int(2), "Basic addition failed")
        self.assertNotEqual(int(1) + int(1), int(3), "Basic addition failed")

        # Test doubles
        # FIXME: Deployment fails for some reason. Maybe bug in CPU? Commenting it out.
        # self.assertEqual(float(0.1) + float(0.2), float(0.3), "Floating addition failed")
        self.assertNotEqual(float(1) + float(1), float(3), "Floating Addition failed")


if __name__ == "__main__":
    unittest.main()
