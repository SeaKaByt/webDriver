import yaml
import json
import pandas as pd

from pathlib import Path
from typing import Dict, Any, List, Union
from helper.logger import logger

def read_excel(path: Union[str, Path]) -> pd.DataFrame:
    """Read an Excel file into a DataFrame."""
    path = Path(path)
    df = pd.read_excel(path)
    logger.debug(f"Read Excel from {path}")
    return df

def read_csv(path: Union[str, Path]) -> pd.DataFrame:
    """Read a CSV file into a DataFrame."""
    path = Path(path)
    df = pd.read_csv(path)
    logger.debug(f"Read CSV from {path}")
    return df

def save_csv(df: pd.DataFrame, path: Union[str, Path], backup: bool = True) -> None:
    """Save DataFrame to CSV with optional backup."""
    path = Path(path)
    
    if backup and path.exists():
        backup_path = path.with_suffix('.bak.csv')
        # Read existing file and save as backup
        existing_df = pd.read_csv(path)
        existing_df.to_csv(backup_path, index=False)
        logger.info(f"Created backup at {backup_path}")
    
    df.to_csv(path, index=False)
    logger.info(f"Saved CSV to {path}")

def read_yaml(path: Union[str, Path]) -> Dict[str, Any]:
    """Read a YAML file into a dictionary."""
    path = Path(path)
    with path.open("r") as f:
        data = yaml.safe_load(f)
    logger.debug(f"Read YAML from {path}")
    return data

def write_yaml(data: Dict[str, Any], path: Union[str, Path]) -> None:
    """Write a dictionary to a YAML file."""
    path = Path(path)
    with path.open("w") as f:
        yaml.safe_dump(data, f, indent=2)
    logger.debug(f"Wrote YAML to {path}")

def update_yaml(path: Union[str, Path], key: str, value: Any) -> None:
    """Update a nested key in a YAML file."""
    path = Path(path)
    data = read_yaml(path)
    current = data
    keys = key.split(".")
    for k in keys[:-1]:
        current = current.setdefault(k, {})
    current[keys[-1]] = value
    write_yaml(data, path)
    logger.info(f"Updated YAML {path} with {key}={value}")

def read_json(path: Union[str, Path]) -> Dict[str, Any]:
    """Read a JSON file into a dictionary."""
    path = Path(path)
    with path.open("r") as f:
        data = json.load(f) or {}
    logger.debug(f"Read JSON from {path}")
    return data

def write_json(path: Union[str, Path], data: Dict[str, Any]) -> None:
    """Write a dictionary to a JSON file."""
    path = Path(path)
    with path.open("w") as f:
        json.dump(data, f, indent=4)
    logger.debug(f"Wrote JSON to {path}")

def update_json(path: Union[str, Path], keys: List[str], value: Any) -> None:
    """Update a nested key in a JSON file."""
    path = Path(path)
    data = read_json(path)
    current = data
    for k in keys[:-1]:
        current = current.setdefault(k, {})
    current[keys[-1]] = value
    write_json(path, data)
    logger.info(f"Updated JSON {path} with {keys}={value}")

def update_column(df, cntr_id, column: str, value) -> None:
    mask = df["cntr_id"] == cntr_id
    if mask.any():
        df.loc[mask, column] = value
        logger.info(f"Updated {column} for {cntr_id} to {value}")
    else:
        raise Exception(f"Cannot update {column} for {cntr_id}")

def create_csv_snapshot(csv_path: Union[str, Path], snapshot_suffix: str = "_snapshot") -> Path:
    """Create a snapshot copy of a CSV file."""
    csv_path = Path(csv_path)
    if not csv_path.exists():
        logger.warning(f"CSV file {csv_path} does not exist, skipping snapshot")
        return None
    
    snapshot_path = csv_path.with_name(f"{csv_path.stem}{snapshot_suffix}.csv")
    df = pd.read_csv(csv_path)
    df.to_csv(snapshot_path, index=False)
    logger.debug(f"Created snapshot: {csv_path} → {snapshot_path}")
    return snapshot_path

def restore_csv_from_snapshot(csv_path: Union[str, Path], snapshot_suffix: str = "_snapshot") -> bool:
    """Restore CSV file from its snapshot."""
    csv_path = Path(csv_path)
    snapshot_path = csv_path.with_name(f"{csv_path.stem}{snapshot_suffix}.csv")
    
    if not snapshot_path.exists():
        logger.warning(f"Snapshot {snapshot_path} does not exist, cannot restore")
        return False
    
    df = pd.read_csv(snapshot_path)
    df.to_csv(csv_path, index=False)
    logger.debug(f"Restored: {snapshot_path} → {csv_path}")
    return True