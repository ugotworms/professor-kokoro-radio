import json
import os
import unittest
from radio.config import Config

class TestConfig(unittest.TestCase):
    def setUp(self):
        self.config_path = "test_config.json"
        self.config = Config(self.config_path)
        self.test_data = {"key": "value"}

    def tearDown(self):
        if os.path.exists(self.config_path):
            os.remove(self.config_path)

    def test_load_and_save_config(self):
        with open(self.config_path, "w") as f:
            json.dump(self.test_data, f)

        loaded_config = self.config.load_config()
        self.assertEqual(loaded_config, self.test_data)

        new_data = {"new_key": "new_value"}
        self.config.save_config(new_data)

        with open(self.config_path, "r") as f:
            saved_config = json.load(f)
        self.assertEqual(saved_config, new_data)

if __name__ == "__main__":
    unittest.main()
