from pathlib import Path
from typing import Dict, Any, List, Union
import yaml
import json
import pandas as pd
from helper.logger import logger

def read_excel(path: Union[str, Path]) -> pd.DataFrame:
    """Read an Excel file into a DataFrame."""
    path = Path(path)
    try:
        df = pd.read_excel(path)
        logger.debug(f"Read Excel from {path}")
        return df
    except Exception as e:
        logger.error(f"Failed to read Excel {path}: {e}")
        raise

def read_csv(path: Union[str, Path]) -> pd.DataFrame:
    """Read a CSV file into a DataFrame."""
    path = Path(path)
    try:
        df = pd.read_csv(path)
        logger.debug(f"Read CSV from {path}")
        return df
    except Exception as e:
        logger.error(f"Failed to read CSV {path}: {e}")
        raise

def read_yaml(path: Union[str, Path]) -> Dict[str, Any]:
    """Read a YAML file into a dictionary."""
    path = Path(path)
    try:
        with path.open("r") as f:
            data = yaml.safe_load(f) or {}
        logger.debug(f"Read YAML from {path}")
        return data
    except Exception as e:
        logger.error(f"Failed to read YAML {path}: {e}")
        raise

def write_yaml(data: Dict[str, Any], path: Union[str, Path]) -> None:
    """Write a dictionary to a YAML file."""
    path = Path(path)
    try:
        with path.open("w") as f:
            yaml.safe_dump(data, f, indent=2)
        logger.debug(f"Wrote YAML to {path}")
    except Exception as e:
        logger.error(f"Failed to write YAML {path}: {e}")
        raise

def update_yaml(path: Union[str, Path], key: str, value: Any) -> None:
    """Update a nested key in a YAML file."""
    path = Path(path)
    try:
        data = read_yaml(path)
        current = data
        keys = key.split(".")
        for k in keys[:-1]:
            current = current.setdefault(k, {})
        current[keys[-1]] = value
        write_yaml(data, path)
        logger.info(f"Updated YAML {path} with {key}={value}")
    except Exception as e:
        logger.error(f"Failed to update YAML {path}: {e}")
        raise

def read_json(path: Union[str, Path]) -> Dict[str, Any]:
    """Read a JSON file into a dictionary."""
    path = Path(path)
    try:
        with path.open("r") as f:
            data = json.load(f) or {}
        logger.debug(f"Read JSON from {path}")
        return data
    except Exception as e:
        logger.error(f"Failed to read JSON {path}: {e}")
        raise

def write_json(path: Union[str, Path], data: Dict[str, Any]) -> None:
    """Write a dictionary to a JSON file."""
    path = Path(path)
    try:
        with path.open("w") as f:
            json.dump(data, f, indent=4)
        logger.debug(f"Wrote JSON to {path}")
    except Exception as e:
        logger.error(f"Failed to write JSON {path}: {e}")
        raise

def update_json(path: Union[str, Path], keys: List[str], value: Any) -> None:
    """Update a nested key in a JSON file."""
    path = Path(path)
    try:
        data = read_json(path)
        current = data
        for k in keys[:-1]:
            current = current.setdefault(k, {})
        current[keys[-1]] = value
        write_json(path, data)
        logger.info(f"Updated JSON {path} with {keys}={value}")
    except Exception as e:
        logger.error(f"Failed to update JSON {path}: {e}")
        raise