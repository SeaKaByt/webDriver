import sys
import argparse
import pandas as pd
from typing import Optional
from pathlib import Path

from helper.sys_utils import raise_with_log
from test_ui.base_flow import BaseFlow
from helper.win_utils import wait_for_window, send_keys_with_log
from helper.container_utils import next_loc
from helper.logger import logger

class ContainerDetails(BaseFlow):
    module = "CD"
    cntr_list = []

    def __init__(self):
        super().__init__()
        cd_config = self.config.get("cd", {})
        self.cd_cntr_id = cd_config.get("cntr_id")
        self.cd_owner = cd_config.get("owner")
        self.cd_voyage = cd_config.get("voyage")
        self.cd_pol = cd_config.get("pol")
        self.cd_gross_wt = cd_config.get("gross_wt")
        self.cd_status = cd_config.get("status")
        self.cd_yard = cd_config.get("yard")
        self.loading_blk = cd_config.get("loading_blk")
        self.loading_shipper = cd_config.get("loading_shipper")
        self.loading_gross_wt = cd_config.get("loading_gross_wt")
        self.create_yes = cd_config.get("create_yes_btn")
        self.create_confirm = cd_config.get("create_confirm_btn")
        self.cancel = cd_config.get("cancel_btn")
        self.confirm_yes = cd_config.get("confirm_yes_btn")
        self.ags4999 = cd_config.get("ags4999")

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
            self.save_as_csv(self.cntr_list, self.gate_pickup_df, self.gate_pickup_data_path)
        except Exception as e:
            logger.error(f"Container creation failed: {e}")
            raise

    def common_details(self) -> None:
        self.cntr_list.append({
            "cntr_id": self.cntr_id,
            "status": self.status,
            "size": self.size,
            "twin": "N"
        })
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
        if self.status in ("XF", "IF"):
            self.voyage_details(self.status)
        send_keys_with_log("{ENTER}")

        if wait_for_window(".*ags4999$", 1):
            self.lane = f"{int(self.lane) + 1}"
            self.actions.click(self.ags4999)
            self.actions.click(self.cd_yard)
            send_keys_with_log("{TAB}")
            send_keys_with_log("{TAB}")
            send_keys_with_log(self.lane)
            send_keys_with_log("{ENTER}")

        if wait_for_window("Confirmation", 1):
            send_keys_with_log("{TAB}")
            send_keys_with_log("{ENTER}")

        if wait_for_window("User Error", 1):
            raise_with_log("Container cannot be created")

        if not self.properties.editable(self.cd_cntr_id):
            raise_with_log("Container creation failed: cntr_id not editable")
        d = next_loc(self.cntr_id, self.size, self.stack, self.lane, self.get_tier(), self.json_data_path)
        for k, v in d.items():
            setattr(self, k, v)

    def voyage_details(self, status) -> None:
        if status == "IF":
            self.actions.click(self.cd_voyage)
            send_keys_with_log("^a")
            send_keys_with_log(self.line, with_tab=True)
            send_keys_with_log(self.vessel)
            send_keys_with_log(self.voyage)
            self.actions.click(self.cd_pol)
            send_keys_with_log(self.pol)
            self.actions.click(self.cd_gross_wt)
            send_keys_with_log(self.gross_wt)
        elif status == "XF":
            self.actions.click(self.cd_voyage)
            send_keys_with_log("^a")
            send_keys_with_log(self.line, with_tab=True)
            send_keys_with_log(self.vessel)
            send_keys_with_log(self.voyage)
            self.actions.set_text(self.loading_blk, self.blk)
            self.actions.set_text(self.loading_shipper, "BOT")
            self.actions.set_text(self.loading_gross_wt, self.gross_wt)
        else:
            raise_with_log(f"Invalid status: {status}")

    def get_tier(self) -> str:
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

    @staticmethod
    def save_as_csv(cntr_list, df, path) -> None:
        try:
            new_data = pd.DataFrame(cntr_list)
            new_df = pd.concat([new_data, df]).drop_duplicates(subset=["cntr_id"]).reset_index(drop=True)
            logger.info(f"Updated DataFrame: {df.to_dict()}")
            new_df.to_csv(path, index=False)
            logger.debug(f"Saved DataFrame to {path}")
        except Exception as e:
            raise_with_log(f"Save CSV failed: {e}")

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
        raise_with_log(f"ContainerDetails failed: {e}")