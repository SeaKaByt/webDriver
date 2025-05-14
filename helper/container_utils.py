from typing import Dict, Union
from pathlib import Path
from helper.logger import logger
from helper.io_utils import read_json, write_json

class ContainerError(Exception):
    """Raised for container-related errors."""
    pass

def _increment_cntr_id(cntr_id: str) -> str:
    """Increment a container ID (e.g., test000001 -> test000002)."""
    try:
        prefix, num = cntr_id[:4], int(cntr_id[4:])
        return f"{prefix}{num + 1:06d}"
    except (ValueError, IndexError) as e:
        logger.error(f"Invalid cntr_id format: {cntr_id}")
        raise ContainerError(f"Invalid cntr_id: {cntr_id}") from e

def update_next_stowage(
    cntr_id: str, bay: str, row: str, tier: str, path: Union[str, Path]
) -> Dict[str, str]:
    """Update stowage data and save to JSON."""
    path = Path(path)
    logger.info("Generating next container stowage")
    try:
        bay_letter = bay[-1]
        bay_num = int(bay[:-1])
        row_num = int(row)
        tier_num = int(tier)
        rules = self.config.get(stowage_rules, {})
        max_row = rules.get("max_row", 12)
        max_tier = rules.get("max_tier", 98)
        reset_tier = rules.get("reset_tier", 82)

        # Increment container ID
        new_cntr_id = _increment_cntr_id(cntr_id)

        # Update bay, row, tier
        if row_num == max_row and tier_num == max_tier:
            bay_letter = "D" if bay_letter == "H" else "H"
            bay_num += 2 if bay_letter == "D" else 0
        new_bay = f"{bay_num:02d}{bay_letter}"

        if tier_num == max_tier and row_num == max_row:
            new_tier = reset_tier
        elif row_num == max_row:
            new_tier = f"{tier_num + 2}"
        else:
            new_tier = tier

        new_row = "01" if row_num == max_row else f"{row_num + 1:02d}"

        update_data = {
            "cntr_id": new_cntr_id,
            "bay": new_bay,
            "row": new_row,
            "tier": new_tier,
        }

        # Update JSON
        for k, v in update_data.items():
            logger.info(f"{k}: {v}")
            write_json(path, {**read_json(path), k: v})

        logger.info("JSON updated for stowage")
        return update_data
    except Exception as e:
        logger.error(f"Failed to update stowage: {e}")
        raise ContainerError(f"Failed to update stowage") from e

def next_loc(
    cntr_id: str, size: str, stack: str, lane: str, tier: str, path: Union[str, Path]
) -> Dict[str, str]:
    """Update location data and save to JSON."""
    path = Path(path)
    logger.info("Generating next container location")
    try:
        size_num = int(size)
        stack_num = int(stack)
        lane_num = int(lane)
        tier_num = int(tier)

        # Increment container ID
        new_cntr_id = _increment_cntr_id(cntr_id)

        # Update stack and lane
        new_stack = stack_num + 2 if lane_num == 99 and tier_num == 5 else stack_num
        # if size_num == 20:
        new_lane = lane_num + 1 if tier_num == 5 else lane_num
        # elif size_num == 40:
        #     new_lane = lane_num + 2 if tier_num == 5 else lane_num

        update_data = {
            "cntr_id": new_cntr_id,
            "stack": str(new_stack),
            "lane": str(new_lane),
        }

        # Update JSON
        for k, v in update_data.items():
            logger.info(f"{k}: {v}")
            write_json(path, {**read_json(path), k: v})

        logger.info("JSON updated for location")
        return update_data
    except Exception as e:
        logger.error(f"Failed to update location: {e}")
        raise ContainerError(f"Failed to update location") from e