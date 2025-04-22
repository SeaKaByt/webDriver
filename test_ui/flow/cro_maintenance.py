import sys
from typing import Optional
from pathlib import Path
from datetime import datetime
from helper.logger import logger
from helper.win_utils import wait_for_window, send_keys_with_log
from test_ui.base_flow import BaseFlow


class CROMaintenance(BaseFlow):
    """Handles CRO module for creating release orders and fetching pins."""
    module = "CRO"
    pin_list = []
    cro_no_list = []

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize CROMaintenance with config and UI settings.

        Args:
            config_path: Optional path to YAML config file.
        """
        super().__init__(config_path=config_path)
        try:
            cro_config = self.config.get("cro", {})
            self.reset = cro_config.get("reset")
            self.create = cro_config.get("create")
            self.cro_cntr_id = cro_config.get("cro_cntr_id")
            self.cro_cro_no = cro_config.get("cro_cro_no")
            self.create_cntr_id = cro_config.get("create_cntr_id")
            self.cro_status = cro_config.get("cro_status")
            self.row0_pin = cro_config.get("row0_pin")
            # Validate DataFrame
            if "cntr_id" not in self.gate_pickup_df.columns:
                logger.error("gate_pickup_data.csv missing 'cntr_id' column")
                raise ValueError("Invalid DataFrame: missing cntr_id")
        except KeyError as e:
            logger.error(f"Config missing key: {e}")
            raise ValueError(f"Invalid config: {e}")

    def create_cro(self) -> None:
        """Create container release orders for each cntr_id."""
        try:
            if not self.properties.visible(self.cro_cntr_id, timeout=1):
                logger.info("Opening CRO module")
                self.module_view(self.module)
            if not self.properties.visible(self.create_cntr_id, timeout=1):
                logger.info("Resetting CRO form")
                self.actions.click(self.reset)

            self.cro_no_list = []
            for cntr_id in self.gate_pickup_df["cntr_id"]:
                logger.info(f"Creating CRO for cntr_id: {cntr_id}")
                self.actions.click(self.create)
                self.actions.click(self.create_cntr_id)
                send_keys_with_log(cntr_id, with_tab=True)
                send_keys_with_log(self.bol, with_tab=True)
                self.generate_cro()
                send_keys_with_log(self.cro_no, with_tab=True)
                send_keys_with_log(self.owner, with_tab=True)
                send_keys_with_log(self.date)
                send_keys_with_log(self.time)
                send_keys_with_log(self.agent, with_tab=True)
                send_keys_with_log("{TAB}")
                send_keys_with_log(self.date)
                send_keys_with_log("{ENTER}")
                if wait_for_window("User Error", timeout=1):
                    logger.error("User Error in CRO creation")
                    raise RuntimeError("User Error detected")
                if not wait_for_window("User Information", timeout=5):
                    logger.error("User Information window not found")
                    raise RuntimeError("User Information window not found")
                send_keys_with_log("{ENTER}")
                self.cro_no_list.append(self.cro_no)

            # Update DataFrame
            if len(self.cro_no_list) == len(self.gate_pickup_df):
                self.gate_pickup_df["cro_no"] = self.cro_no_list
                logger.info(f"Updated DataFrame: {self.gate_pickup_df.to_dict()}")
                self.gate_pickup_df.to_csv(self.gate_pickup_data_path, index=False)
        except Exception as e:
            logger.error(f"CRO creation failed: {e}")
            raise

    def generate_cro(self) -> None:
        """Generate a unique CRO number based on timestamp."""
        try:
            now = datetime.now()
            self.cro_no = now.strftime("%d%m%H%M%S")
            logger.debug(f"Generated CRO number: {self.cro_no}")
        except Exception as e:
            logger.error(f"Failed to generate CRO number: {e}")
            raise

    def get_pin(self) -> None:
        """Fetch pins for each cntr_id and update DataFrame."""
        try:
            logger.info("Fetching pins for CRO")
            self.actions.click(self.reset)
            self.actions.click(self.cro_status)
            send_keys_with_log("active")
            self.pin_list = []
            for cntr_id in self.gate_pickup_df["cntr_id"]:
                logger.info(f"Fetching pin for cntr_id: {cntr_id}")
                self.actions.click(self.cro_cntr_id)
                send_keys_with_log("^a")
                send_keys_with_log(cntr_id)
                send_keys_with_log("{ENTER}")
                pin = self.properties.text_value(self.row0_pin)
                try:
                    pin_value = int(pin) if pin else 0
                except (ValueError, TypeError):
                    logger.warning(f"Invalid pin for {cntr_id}: {pin}")
                    pin_value = 0
                self.pin_list.append(pin_value)
                if wait_for_window("User Information", timeout=1):
                    logger.error("User Information window unexpected")
                    raise RuntimeError("Unexpected User Information window")

            self.gate_pickup_df["pin"] = self.pin_list
            logger.info(f"Updated DataFrame: {self.gate_pickup_df.to_dict()}")
            self.gate_pickup_df.to_csv(self.gate_pickup_data_path, index=False)
        except Exception as e:
            logger.error(f"Get pin failed: {e}")
            raise

if __name__ == "__main__":
    try:
        cro = CROMaintenance()
        cro.create_cro()
        cro.get_pin()
    except Exception as e:
        logger.error(f"CROMaintenance failed: {e}")
        sys.exit(1)