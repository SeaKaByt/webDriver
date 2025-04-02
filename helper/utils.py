import yaml
import time
import json

import pywinauto
from pywinauto.keyboard import send_keys

def read_yaml(path: str) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)

def write_yaml(data, path: str):
    with open(path, "w") as f:
        yaml.safe_dump(data, f)

def update_yaml(path: str, key: str, value):
    data = read_yaml(path)

    keys = key.split('.')
    current = data
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value

    write_yaml(data, path)
    
def read_json(path):
    with open(path, 'r') as file:
        data = json.load(file)
    return data

def write_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)


def update_json(path, keys, value):
    with open(path, 'r') as file:
        data = json.load(file)

    current = data
    for key in keys[:-1]:
        current = current.setdefault(key, {})
    current[keys[-1]] = value

    write_json(path, data)

def send_keys_tab(keys):
    send_keys(keys)
    send_keys('{TAB}')

def get_match_windows(title):
    window = pywinauto.findwindows.find_windows(title_re=title)
    print(f"Found windows: {window}")
    return window

def wait_for_window(title, timeout=30):
    print(f"Waiting for window: {title}")
    while timeout > 0:
        window = pywinauto.findwindows.find_windows(title_re=title)
        if window:
            return window
        time.sleep(1)
        timeout -= 1
    return None
