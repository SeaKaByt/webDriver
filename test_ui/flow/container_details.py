import argparse
import pandas as pd
from pathlib import Path
from pandas.errors import EmptyDataError
from test_ui.flow_config import BaseFlow
from helper.win_utils import wait_for_window, send_keys_wlog
from helper.container_utils import next_loc
from helper.logger import logger


class ContainerDetails(BaseFlow):
    """Handles container creation and management in a UI-based logistics application."""

    MODULE = "CD"

    def __init__(self, external_driver=None):
        """Initialize the ContainerDetails class with configuration."""
        super().__init__(external_driver=external_driver)
        self.cd_config = self.config["cd"]
        self.cntr_list = []

    def create_cntr(self, count: int, movement: str) -> None:
        """Create containers in the UI and update the corresponding CSV file.

        Args:
            count: Number of containers to create.
            movement: Type of movement ('loading' or 'gatePickup').

        Raises:
            ValueError: If movement type is invalid.
            RuntimeError: If UI gate_house fail.
        """
        df, path = self._load_data(movement)

        if not self.properties.visible(self.cd_config["cntr_id"], timeout=1):
            logger.info("Opening CD module")
            self.module_view(self.MODULE)

        for i in range(count):
            logger.info(f"Creating container {i + 1}/{count}")
            self._enter_container_details(movement)

        self._save_to_csv(df, path)

    def _load_data(self, movement: str) -> tuple[pd.DataFrame, Path]:
        """Load container data from CSV based on movement type.

        Args:
            movement: Type of movement ('loading' or 'gatePickup').

        Returns:
            Tuple of DataFrame and file path.

        Raises:
            ValueError: If movement type is invalid.
        """
        if movement == "loading":
            return next(self.get_loading_data())
        elif movement == "gatePickup":
            return next(self.get_gate_pickup_data())
        raise ValueError(f"Invalid movement: {movement}")

    def _enter_container_details(self, movement: str) -> None:
        """Enter container details in the UI and append to container list.

        Args:
            movement: Type of movement ('loading' or 'gatePickup').

        Raises:
            RuntimeError: If UI interactions fail.
        """
        details = {
            "cntr_id": self.cntr_id,
            "status": self.status,
            "size": self.size,
        }
        if movement == "gatePickup":
            details["twin_ind"] = "S"
        self.cntr_list.append(details)

        # Enter container ID
        self.actions.click(self.cd_config["cntr_id"])
        send_keys_wlog("^a")
        send_keys_wlog(self.cntr_id)
        send_keys_wlog("{ENTER}")

        # Handle Create Container window
        if not wait_for_window("Create Container", timeout=5):
            raise RuntimeError("Create Container window not found")
        self.actions.click(self.cd_config["create_yes_btn"])
        self.actions.click(self.cd_config["create_confirm_btn"])

        # Enter common container details
        self._set_common_fields()

        # Enter voyage-specific details if applicable
        if self.status in ("XF", "IF"):
            self._set_voyage_details(self.status)

        send_keys_wlog("{ENTER}")

        # Handle ags4999 window for lane adjustment
        if wait_for_window(".*ags4999$", timeout=1):
            self._handle_ags4999_error()

        # Handle Confirmation window
        if wait_for_window("Confirmation", timeout=1):
            send_keys_wlog("{TAB}")
            send_keys_wlog("{ENTER}")

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
            self.cntr_id, self.size, self.stack, self.lane,
            self._get_tier(), Path("data/data_templant.json")
        )
        for key, value in location_data.items():
            setattr(self, key, value)

    def _set_common_fields(self) -> None:
        """Set common container fields in the UI."""
        self.actions.click(self.cd_config["status"])
        send_keys_wlog(self.status)
        send_keys_wlog(self.size)
        send_keys_wlog(self.type)
        self.actions.click(self.cd_config["owner"])
        send_keys_wlog(self.owner, with_tab=True)
        send_keys_wlog("{TAB}")
        send_keys_wlog(self.block)
        send_keys_wlog(self.stack, with_tab=True)
        send_keys_wlog(self.lane)

    def _set_voyage_details(self, status: str) -> None:
        """Set voyage-specific details in the UI.

        Args:
            status: Container status ('XF' or 'IF').

        Raises:
            ValueError: If status is invalid.
        """
        self.actions.click(self.cd_config["voyage"])
        send_keys_wlog("^a")
        send_keys_wlog(self.line, with_tab=True)
        send_keys_wlog(self.vessel)
        send_keys_wlog(self.voy)

        if status == "IF":
            self.actions.click(self.cd_config["pol"])
            send_keys_wlog(self.pol)
            self.actions.click(self.cd_config["gross_wt"])
            send_keys_wlog(self.gross_wt)
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
        send_keys_wlog("{TAB}")
        send_keys_wlog("{TAB}")
        send_keys_wlog(self.lane)
        send_keys_wlog("{ENTER}")

    def _get_tier(self) -> str:
        """Extract the tier value from the yard field.

        Returns:
            The extracted tier value.

        Raises:
            ValueError: If yard value or format is invalid.
        """
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
        """Save container list to CSV, merging with existing data.

        Args:
            df: Existing DataFrame from CSV.
            path: Path to the CSV file.

        Raises:
            EmptyDataError: If no new data to save.
        """
        new_data = pd.DataFrame(self.cntr_list)
        if new_data.empty:
            raise EmptyDataError("No new data to save")

        updated_df = pd.concat([new_data, df]).drop_duplicates(
            subset=["cntr_id"], keep="first"
        ).reset_index(drop=True)

        logger.info(f"Updated DataFrame: {updated_df.to_dict()}")
        updated_df.to_csv(path, index=False)
        logger.debug(f"Saved DataFrame to {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create containers in logistics application")
    parser.add_argument(
        "count",
        type=int,
        nargs="?",
        default=1,
        help="Number of containers to create"
    )
    parser.add_argument(
        "movement",
        type=str,
        choices=["loading", "gatePickup"],
        help="Movement type (loading or gatePickup)"
    )
    args = parser.parse_args()

    cd = ContainerDetails()
    cd.create_cntr(args.count, args.movement)