import json

class Config:
    def __init__(self, config_path="radio_config.json"):
        self.config_path = config_path

    def load_config(self):
        with open(self.config_path, "r") as f:
            return json.load(f)

    def save_config(self, config):
        with open(self.config_path, "w") as f:
            json.dump(config, f)
