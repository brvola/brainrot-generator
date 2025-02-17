import json
import os

def load_config(config_file='src/config/config.json'):
    abs_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(abs_path, 'r') as f:
        config = json.load(f)
    return config

CONFIG = load_config() 