import base64
import json
from configparser import ConfigParser
from pathlib import Path
from keyhoard.encryption import generate_salt

CONFIG_FILE = Path("config.json")

def load_config():
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    else:
        salt = generate_salt()
        config = {"salt": base64.b64encode(salt).decode()}
        CONFIG_FILE.write_text(json.dumps(config, indent=2))
        return config

