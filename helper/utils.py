import yaml
import time
import json
import pywinauto
import pandas as pd
from helper.logger import logger

def read_excel(path: str):
    return pd.read_excel(path)

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

def send_keys(keys):
    logger.info(f"Sending keys: {keys}")
    send_keys(keys)

def send_keys_tab(keys):
    logger.info(f"Sending keys: {keys}")
    send_keys(keys)
    send_keys('{TAB}')

def get_match_windows(title):
    window = pywinauto.findwindows.find_windows(title_re=title)
    logger.info(f"Found window: {window}")
    return window

def wait_for_window(title, timeout=30):
    logger.info(f"Waiting for window: {title}")
    for _ in range(timeout):
        window = pywinauto.findwindows.find_windows(title_re=title)
        if window:
            logger.info(f"Found window: {window}")
            return window
        time.sleep(1)
    logger.info(f"Window not found: {title} after {timeout} seconds")

def window_exists(title, timeout=10):
    if wait_for_window(title, timeout):
        logger.info(f"Window exists: {title}")
        return True
    logger.warning(f"Window does not exist: {title}")
    raise

def update_next_stowage(cntr_id, bay, row, tier, path):
    logger.info("=== Generating next cntr ===")
    bay_l = bay[-1]
    bay_n = int(bay[:-1])

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
        logger.info(f"{k}: {v}")
        update_json(path, [k], v)

    logger.info("=== JSON Updated ===")
    return update_data

def next_loc(cntr_id, stack, lane, tier, path):
    stack_n = int(stack)
    lane_n = int(lane)

    logger.info(f"Current tier: {tier}")
    logger.info("=== Generating next cntr ===")
    cntr_id = f"test{int(cntr_id[4:]) + 1:06}"
    stack_n += 2 if int(lane) == 99 and int(tier) == 5 else 0
    lane_n += 1 if int(tier) == 5 else 0

    update_data = {
        'cntr_id': cntr_id,
        'stack': str(stack_n),
        'lane': str(lane_n),
    }

    for k, v in update_data.items():
        logger.info(f"{k}: {v}")
        update_json(path, [k], v)
    logger.info("=== JSON Updated ===")

    return update_data