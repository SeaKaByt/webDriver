import pandas as pd

from pathlib import Path
from pandas.errors import EmptyDataError
from helper.io_utils import read_json
from helper.paths import ProjectPaths
from src.core.driver import BaseDriver
from src.common.menu import Menu
from src.pages.inventory_operation.hold_release import HoldRelease
from helper.win_utils import wait_for_window, sendkeys, focus_window
from helper.container_utils import next_loc
from helper.logger import logger

class ContainerDetails(BaseDriver):
    MODULE = "CD"

    def __init__(self, external_driver=None):
        super().__init__(external_driver=external_driver)
        self.cd_config = self.config["cd"]
        self.cntr_list = []

        self.j = read_json(ProjectPaths.DATA / "data_template.json")
        self.cntr_id = self.j["cntr_id"]
        self.block = self.j["block"]
        self.stack = self.j["stack"]
        self.lane = self.j["lane"]

        self.owner = "NVD"
        self.line = "NVD"
        self.vessel = "TSHM04"
        self.voyage = "V01"
        self.pol = "HKHKG"
        self.blk = "HKHKG"
        self.gross_wt = "17500"

    def create_cntr(self, count: int, movement: str, status: str, size: str, type: str) -> None:
        df, path = self._load_data(movement)

        focus_window("nGen")

        if not self.properties.visible(self.cd_config["cntr_id"], timeout=1):
            logger.info("Opening CD module")
            Menu.to_module(self.MODULE, self)

        for i in range(count):
            logger.info(f"Creating container {i + 1}/{count}")
            self._enter_container_details(movement, status, size, type)

        self._save_to_csv(df, path)

    def _load_data(self, movement: str) -> tuple[pd.DataFrame, Path]:
        if movement == "loading":
            return next(ProjectPaths.get_loading_data())
        elif movement == "gatePickup":
            return next(ProjectPaths.get_gate_pickup_data())
        raise ValueError(f"Invalid movement: {movement}")

    def _enter_container_details(self, movement: str, status: str, size: str, type: str) -> None:
        details = {
            "cntr_id": self.cntr_id,
            "status": status,
            "size": size,
            "type": type,
        }
        if movement == "gatePickup":
            details["twin_ind"] = "S"
        self.cntr_list.append(details)

        # Enter container ID
        self.actions.click(self.cd_config["cntr_id"])
        sendkeys("^a")
        sendkeys(self.cntr_id)
        sendkeys("{ENTER}")

        # Handle Create Container window
        if not wait_for_window("Create Container", timeout=5):
            raise RuntimeError("Create Container window not found")
        self.actions.click(self.cd_config["create_yes_btn"])
        self.actions.click(self.cd_config["create_confirm_btn"])

        # Enter common container details
        self._set_common_fields(status, size, type)

        # Enter voyage-specific details if applicable
        if status in ("XF", "IF"):
            self._set_voyage_details(status)

        sendkeys("{ENTER}")

        # Handle ags4999 window for lane adjustment
        if wait_for_window(".*ags4999$", timeout=1):
            self._handle_ags4999_error()

        # Handle Confirmation window
        if wait_for_window("Confirmation", timeout=1):
            sendkeys("{TAB}")
            sendkeys("{ENTER}")

        # Check for User Error
        if wait_for_window("User Error", timeout=1):
            logger.error("Container cannot be created")
            raise RuntimeError("Container cannot be created")

        # Verify container creation
        if not self.properties.editable(self.cd_config["cntr_id"]):
            logger.error("Container creation failed: cntr_id not editable")
            raise RuntimeError("Container creation failed: cntr_id not editable")

        # Update location attributes
        location_data = next_loc(
            self.cntr_id, size, self.stack, self.lane,
            self._get_tier(), Path("data/data_template.json")
        )
        for key, value in location_data.items():
            setattr(self, key, value)

    def _set_common_fields(self, status: str, size: str, type: str) -> None:
        """Set common container fields in the UI."""
        self.actions.click(self.cd_config["status"])
        sendkeys(status)
        sendkeys(size)
        sendkeys(type)
        self.actions.click(self.cd_config["owner"])
        sendkeys(self.owner, with_tab=True)
        sendkeys("{TAB}")
        sendkeys(self.block)
        sendkeys(self.stack, with_tab=True)
        sendkeys(self.lane)

    def _set_voyage_details(self, status: str) -> None:
        self.actions.click(self.cd_config["voyage"])
        sendkeys("^a")
        sendkeys(self.line, with_tab=True)
        sendkeys(self.vessel)
        sendkeys(self.voyage)

        if status == "IF":
            self.actions.click(self.cd_config["pol"])
            sendkeys(self.pol)
            self.actions.click(self.cd_config["gross_wt"])
            sendkeys(self.gross_wt)
        elif status == "XF":
            self.actions.set_text(self.cd_config["loading_blk"], self.blk)
            self.actions.set_text(self.cd_config["loading_shipper"], "BOT")
            self.actions.set_text(self.cd_config["loading_gross_wt"], self.gross_wt)
        else:
            raise ValueError(f"Invalid status: {status}")

    def _handle_ags4999_error(self) -> None:
        """Handle the ags4999 window by updating the lane and retrying."""
        self.lane = f"{int(self.lane) + 1}"
        self.actions.click(self.cd_config["ags4999"])
        self.actions.click(self.cd_config["yard"])
        sendkeys("{TAB}")
        sendkeys("{TAB}")
        sendkeys(self.lane)
        sendkeys("{ENTER}")

    def _get_tier(self) -> str:
        yard_value = self.properties.text_value(self.cd_config["yard"])
        if not yard_value:
            raise ValueError("Invalid cd_yard value")

        parts = yard_value.split()
        if not parts or "/" not in parts[-1]:
            raise ValueError(f"Invalid cd_yard format: {yard_value}")

        tier = parts[-1].split("/")[-1]
        logger.debug(f"Extracted tier: {tier}")
        return tier

    def _save_to_csv(self, df: pd.DataFrame, path: Path) -> None:
        new_data = pd.DataFrame(self.cntr_list)
        if new_data.empty:
            raise EmptyDataError("No new data to save")

        updated_df = pd.concat([new_data, df]).drop_duplicates(
            subset=["cntr_id"], keep="first"
        ).reset_index(drop=True)

        logger.info(f"Updated DataFrame: {updated_df.to_dict()}")
        updated_df.to_csv(path, index=False)
        logger.debug(f"Saved DataFrame to {path}")

    def click(self):
        self.actions.click(self.home)

def main():
    focus_window("nGen")

    c = ContainerDetails()
    c.click()
    h = HoldRelease()
    h.click()

if __name__ == "__main__":
    main()
