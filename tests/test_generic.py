import unittest
from Utils import General_Utils as utility

class Test_Generic(unittest.TestCase):
    def test_example(self):
        # Example test case
        self.assertTrue(True)

    def test_load_config(self):
        # Test loading configuration
        config = utility.load_json(name_of_file="Msg_Responses")
        self.assertIsInstance(config, dict)
        self.assertIn("good_bot", config)