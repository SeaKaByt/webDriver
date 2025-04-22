import sys
import argparse
import pandas as pd
from typing import Optional
from pathlib import Path
from test_ui.base_flow import BaseFlow
from helper.win_utils import wait_for_window, send_keys_with_log
from helper.container_utils import next_loc
from helper.logger import logger

class ContainerDetails(BaseFlow):
    """Handles CD module for creating container details."""
    module = "CD"
    cntr_list = []

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize ContainerDetails with config and UI settings.

        Args:
            config_path: Optional path to YAML config file.
        """
        super().__init__(config_path=config_path)
        try:
            cd_config = self.config.get("cd", {})
            self.cd_cntr_id = cd_config.get("cntr_id")
            self.cd_owner = cd_config.get("owner")
            self.cd_voyage = cd_config.get("voyage")
            self.cd_pol = cd_config.get("pol")
            self.cd_gross_wt = cd_config.get("gross_wt")
            self.cd_status = cd_config.get("status")
            self.cd_yard = cd_config.get("yard")
            self.create_yes = cd_config.get("create_yes_btn")
            self.create_confirm = cd_config.get("create_confirm_btn")
            self.cancel = cd_config.get("cancel_btn")
            self.confirm_yes = cd_config.get("confirm_yes_btn")
            self.ags4999 = cd_config.get("ags4999")
            # Additional attributes (from BaseFlow or config)
            # self.bol = cd_config.get("bol", "BOL001")
            # self.owner = cd_config.get("owner_value", "TEST")
            # self.block = cd_config.get("block", "A")
            # self.stack = cd_config.get("stack", "01")
            # self.lane = cd_config.get("lane", "1")
            # self.line = cd_config.get("line", "LINE1")
            # self.vessel = cd_config.get("vessel", "VESSEL1")
            # self.voyage = cd_config.get("voyage_value", "VOY001")
            # self.pol = cd_config.get("pol_value", "POL001")
            # self.gross_wt = cd_config.get("gross_wt_value", "1000")
            # self.status = cd_config.get("status_value", "if")
            # self.size = cd_config.get("size", "40")
            # self.type = cd_config.get("type", "HC")
            # Validate DataFrame
            if "cntr_id" not in self.df.columns:
                logger.error("gate_pickup_data.csv missing 'cntr_id' column")
                raise ValueError("Invalid DataFrame: missing cntr_id")
        except KeyError as e:
            logger.error(f"Config missing key: {e}")
            raise ValueError(f"Invalid config: {e}")

    def create_cntr(self, count: int) -> None:
        """Create a specified number of containers."""
        try:
            if not self.properties.visible(self.cd_cntr_id, timeout=1):
                logger.info("Opening CD module")
                self.module_view(self.module)
            self.cntr_list = []
            for i in range(count):
                logger.info(f"Creating container {i+1}/{count}")
                self.common_details()
            self.save_as_csv()
        except Exception as e:
            logger.error(f"Container creation failed: {e}")
            raise

    def common_details(self) -> None:
        """Handle common UI steps for container creation."""
        try:
            self.cntr_list.append(self.cntr_id)
            self.actions.click(self.cd_cntr_id)
            send_keys_with_log("^a")
            send_keys_with_log(self.cntr_id)
            send_keys_with_log("{ENTER}")
            if wait_for_window("Create Container", timeout=5):
                self.actions.click(self.create_yes)
                self.actions.click(self.create_confirm)
            else:
                logger.error("Create Container window not found")
                raise RuntimeError("Create Container window not found")
            self.actions.click(self.cd_status)
            send_keys_with_log(self.status)
            send_keys_with_log(self.size)
            send_keys_with_log(self.type)
            self.actions.click(self.cd_owner)
            send_keys_with_log(self.owner, with_tab=True)
            send_keys_with_log("{TAB}")
            send_keys_with_log(self.block)
            send_keys_with_log(self.stack, with_tab=True)
            send_keys_with_log(self.lane)
            if self.status == "if":
                self.voyage_details()
            send_keys_with_log("{ENTER}")

            if wait_for_window("User Error ags4999", timeout=1):
                self.lane = f"{int(self.lane) + 1}"
                self.actions.click(self.ags4999)
                self.actions.click(self.cd_yard)
                send_keys_with_log("{TAB}")
                send_keys_with_log("{TAB}")
                send_keys_with_log(self.lane)
                send_keys_with_log("{ENTER}")

            if not self.properties.editable(self.cd_cntr_id):
                logger.error("cd_cntr_id not editable")
                raise RuntimeError("Container creation failed: cntr_id not editable")
            d = next_loc(self.cntr_id, self.stack, self.lane, self.get_tier(), self.json_data_path)
            for k, v in d.items():
                setattr(self, k, v)
        except Exception as e:
            logger.error(f"Common details failed: {e}")
            raise

    def voyage_details(self) -> None:
        """Enter voyage-specific details."""
        try:
            self.actions.click(self.cd_voyage)
            send_keys_with_log("^a")
            send_keys_with_log(self.line, with_tab=True)
            send_keys_with_log(self.vessel)
            send_keys_with_log(self.voyage)
            self.actions.click(self.cd_pol)
            send_keys_with_log(self.pol)
            self.actions.click(self.cd_gross_wt)
            send_keys_with_log(self.gross_wt)
        except Exception as e:
            logger.error(f"Voyage details failed: {e}")
            raise

    def get_tier(self) -> str:
        """Extract tier from cd_yard text."""
        try:
            v = self.properties.text_value(self.cd_yard)
            if not v:
                logger.error("cd_yard text is empty")
                raise ValueError("Invalid cd_yard value")
            parts = v.split()
            if not parts or "/" not in parts[-1]:
                logger.error(f"Invalid cd_yard format: {v}")
                raise ValueError(f"Invalid cd_yard format: {v}")
            self.tier = parts[-1].split("/")[-1]
            logger.debug(f"Extracted tier: {self.tier}")
            return self.tier
        except Exception as e:
            logger.error(f"Get tier failed: {e}")
            raise

    def save_as_csv(self) -> None:
        """Save container IDs to CSV, merging with existing DataFrame."""
        try:
            new_data = pd.DataFrame({"cntr_id": self.cntr_list})
            self.df = pd.concat([new_data, self.gate_pickup_df]).drop_duplicates(subset=["cntr_id"]).reset_index(drop=True)
            logger.info(f"Updated DataFrame: {self.df.to_dict()}")
            self.df.to_csv(self.gate_pickup_data_path, index=False)
            logger.debug(f"Saved DataFrame to {self.gate_pickup_data_path}")
        except Exception as e:
            logger.error(f"Save CSV failed: {e}")
            raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create containers")
    parser.add_argument("count", type=int, nargs="?", default=1, help="Number of containers to create")
    parser.add_argument("--test", action="store_true", help="Run test code")
    args = parser.parse_args()

    try:
        cd = ContainerDetails()
        if args.test:
            logger.info("Test mode not implemented")
        elif args.count is not None:
            cd.create_cntr(args.count)
    except Exception as e:
        logger.error(f"ContainerDetails failed: {e}")
        sys.exit(1)