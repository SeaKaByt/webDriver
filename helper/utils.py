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
    # breakpoint()

def update_next_stowage(cntr_id, bay, row, tier, path):
    bay_l = bay[-1]
    bay_n = int(bay[:-1])

    print("=== Generating next cntr ===")
    cntr_id = f"test{int(cntr_id[4:]) + 1:06}"

    if int(row) == 12 and int(tier) == 98:
        bay_l = "D" if bay_l == "H" else "H"
        bay_n += 2 if bay_l == "D" else 0
    bay = f"{bay_n:02d}{bay_l}"

    if int(tier) == 98 and row == "12":
        tier = "82"
    elif row == "12":
        tier = f"{int(tier) + 2}"

    row = "01" if int(row) == 12 else f"{int(row) + 1:02d}"

    update_data = {
        'cntr_id': cntr_id,
        'bay': bay,
        'row': row,
        'tier': tier
    }

    for k, v in update_data.items():
        print(f"{k}: {v}")
        update_json(path, [k], v)
    print("=== JSON Updated ===")

    return update_data

def next_loc(cntr_id, stack, lane, tier, path):
    stack_n = int(stack)
    lane_n = int(lane)

    print(f'current tier: {tier}')
    print("=== Generating next cntr ===")
    cntr_id = f"test{int(cntr_id[4:]) + 1:06}"
    stack_n += 2 if int(lane) == 99 and int(tier) == 5 else 0
    lane_n += 1 if int(tier) == 5 else 0

    update_data = {
        'cntr_id': cntr_id,
        'stack': str(stack_n),
        'lane': str(lane_n),
    }

    for k, v in update_data.items():
        print(f"{k}: {v}")
        update_json(path, [k], v)
    print("=== JSON Updated ===")

    return update_data