import argparse
import sys
from typing import Optional
from pathlib import Path
import time
from helper.logger import logger
from helper.win_utils import wait_for_window, send_keys_with_log
from test_ui.base_flow import BaseFlow

class GateTransaction(BaseFlow):
    """Handles gate transaction UI flows for pickup and confirmation."""
    module = "GT"
    tractor_list = []

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize GateTransaction with config and UI settings.

        Args:
            config_path: Optional path to YAML config file.
        """
        super().__init__(config_path=config_path)
        try:
            self.username = self.config["nGen"]["username"]
            self.password = self.config["nGen"]["password"]
            gt_config = self.config.get("gt", {})
            self.search_tractor = gt_config.get("search_tractor")
            self.create_pin = gt_config.get("create_pin")
            self.create_driver = gt_config.get("create_driver")
            self.row0_cntr_id = gt_config.get("row0_cntr_id")
            self.inspection_seal = gt_config.get("inspection_seal")
            self.manual_confirm_btn = gt_config.get("manual_confirm_btn")
            self.printer_id = gt_config.get("printer_id")
            self.gate_settings = self.config.get("gate_settings", {
                "confirmation_code": "2000",
                "inspection_seal_value": "yfn",
                "printer_dummy": "dummy"
            })
            # Validate DataFrame
            required_columns = ["cntr_id", "pin", "tractor"]
            if not all(col in self.df.columns for col in required_columns):
                logger.error(f"data.csv missing columns: {required_columns}")
                raise ValueError(f"Invalid CSV: missing {required_columns}")
        except KeyError as e:
            logger.error(f"Config missing key: {e}")
            raise ValueError(f"Invalid config: {e}")

    def create_pickup(self) -> None:
        """Create pickup transactions for containers."""
        try:
            self.get_tractor()
            if not self.properties.visible(self.search_tractor, timeout=1):
                self.module_view(self.module)

            for i in range(len(self.df)):
                cntr_id = self.df["cntr_id"][i]
                tractor = self.df["tractor"][i]
                pin= self.df["pin"][i]

                logger.info(f"Processing pickup for cntr_id: {cntr_id}, tractor: {tractor}, pin: {pin}")
                self.actions.click(self.search_tractor)
                send_keys_with_log(str(tractor))
                send_keys_with_log("{ENTER}")
                send_keys_with_log("%1")
                if not wait_for_window("Create", timeout=5):
                    raise RuntimeError("Create window not found")
                self.actions.click(self.create_pin)
                send_keys_with_log(str(pin))
                self.actions.click(self.create_driver)
                send_keys_with_log(str(tractor))
                send_keys_with_log("{ENTER}")
                if not wait_for_window("Confirmation", timeout=5):
                    raise RuntimeError("Confirmation window not found")
                send_keys_with_log("{ENTER}")
                if wait_for_window("Insufficient", timeout=2):
                    send_keys_with_log(self.username, with_tab=True)
                    send_keys_with_log(self.password)
                    send_keys_with_log("{ENTER}")
                    time.sleep(1)
                    send_keys_with_log("{ENTER}")
                if wait_for_window("Confirmation", timeout=2):
                    send_keys_with_log("{ENTER}")
                    time.sleep(1)
                self.release_print_cwp()
        except Exception as e:
            logger.error(f"Create pickup failed: {e}")
            raise

    def get_tractor(self) -> None:
        """Generate tractor IDs and update DataFrame."""
        try:
            count = len(self.df)
            if count == 0:
                logger.error("DataFrame is empty")
                raise ValueError("Empty DataFrame")
            self.tractor_list = [f"OXT{i:02d}" for i in range(1, count + 1)]
            self.df["tractor"] = self.tractor_list
            logger.info(f"Updated DataFrame with tractors: {self.df}")
            # Save to CSV, not Excel
            self.df.to_csv(self.data_path, index=False)
            logger.debug(f"Saved DataFrame to {self.data_path}")
        except Exception as e:
            logger.error(f"Failed to update tractors: {e}")
            raise

    def release_print_cwp(self) -> None:
        """Release and print CWP for a transaction."""
        try:
            self.actions.click(self.row0_cntr_id)
            send_keys_with_log("%3")
            time.sleep(1)
            send_keys_with_log("%7")
            if not wait_for_window("Print", timeout=5):
                raise RuntimeError("Print window not found")
            send_keys_with_log(self.gate_settings["printer_dummy"])
            send_keys_with_log("{ENTER}")
            if not wait_for_window("User Information", timeout=5):
                logger.error("User Information window not found")
                raise RuntimeError("User Information window not found")
            send_keys_with_log("{ENTER}")
        except Exception as e:
            logger.error(f"Release print CWP failed: {e}")
            raise

    def confirm_pickup(self) -> None:
        """Confirm pickup transactions for tractors."""
        try:
            if not self.properties.visible(self.search_tractor, timeout=1):
                self.module_view(self.module)

            for tractor in self.df["tractor"]:
                logger.info(f"Confirming pickup for tractor: {tractor}")
                self.actions.click(self.search_tractor)
                send_keys_with_log(tractor)
                send_keys_with_log("{ENTER}")
                send_keys_with_log("%4")
                if wait_for_window("Confirm", timeout=5):
                    send_keys_with_log("{TAB}")
                    send_keys_with_log("{ENTER}")
                    if not wait_for_window("Exit Gate", timeout=5):
                        raise RuntimeError("Exit Gate window not found")
                    send_keys_with_log(self.gate_settings["confirmation_code"])
                    self.actions.click(self.inspection_seal)
                    send_keys_with_log(self.gate_settings["inspection_seal_value"])
                    send_keys_with_log("{ENTER}")
                elif not wait_for_window("Gate Confirm", timeout=1):
                    raise RuntimeError("Gate Confirm window not found")
                self.actions.click(self.manual_confirm_btn)
                if not wait_for_window("Gate Confirm", timeout=5):
                    raise RuntimeError("Gate Confirm window not found")
                send_keys_with_log("{ENTER}")
                time.sleep(1)
        except Exception as e:
            logger.error(f"Confirm pickup failed: {e}")
            raise

    def run_method(self, method_name: str) -> None:
        """Execute a specified method by name."""
        methods = {
            "create_pickup": self.create_pickup,
            "confirm_pickup": self.confirm_pickup
        }
        method = methods.get(method_name)
        if method is None:
            logger.error(f"Invalid method: {method_name}")
            raise ValueError(f"Method {method_name} not found")
        logger.info(f"Running method: {method_name}")
        method()

    def test(self):
        print(self.df)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gate Transaction Automation")
    parser.add_argument(
        "method",
        choices=["create_pickup", "confirm_pickup", "test"],
        help="Method to execute (create_pickup or confirm_pickup)"
    )
    args = parser.parse_args()

    try:
        gt = GateTransaction()
        gt.run_method(args.method)
        # gt.test()
    except Exception as e:
        logger.error(f"GateTransaction failed: {e}")
        sys.exit(1)