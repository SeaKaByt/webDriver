import argparse
import math
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
            self.ground_btn = gt_config.get("ground_btn")
            self.create_grounding_cntr = gt_config.get("create_grounding_cntr")
            self.create_grounding_driver = gt_config.get("create_grounding_driver")
            self.create_grounding_owner = gt_config.get("create_grounding_owner")
            self.create_grounding_size = gt_config.get("create_grounding_size")
            self.create_grounding_ok_btn = gt_config.get("create_grounding_ok_btn")
            self.create_grounding_material = gt_config.get("create_grounding_material")
            self.create_grounding_FA = gt_config.get("create_grounding_FA")
            self.create_grounding_gross_wt = gt_config.get("create_grounding_gross_wt")
            self.gate_inspection_ok_btn = gt_config.get("gate_inspection_ok_btn")
            self.gate_transaction_refresh_btn = gt_config.get("gate_transaction_refresh_btn")
            self.gate_confirm_manual_confirm_btn = gt_config.get("gate_confirm_manual_confirm_btn")
            self.print_cms_btn = gt_config.get("print_cms_btn")
            self.gate_settings = self.config.get("gate_settings", {
                "confirmation_code": "2000",
                "inspection_seal_value": "yfn",
                "printer": "dummy"
            })
            # Validate DataFrame
            required_columns = ["cntr_id", "pin", "tractor"]
            if not all(col in self.gate_pickup_df.columns for col in required_columns):
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

            for i in range(len(self.gate_pickup_df)):
                cntr_id = self.gate_pickup_df["cntr_id"][i]
                tractor = self.gate_pickup_df["tractor"][i]
                pin= self.gate_pickup_df["pin"][i]

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

    def create_gate_ground(self) -> None:
        """Create gate grounding transactions."""
        try:
            self._get_tractor()
            if not self.properties.visible(self.search_tractor):
                self.module_view(self.module)

            for idx, row in self.gate_ground_df.iterrows():
                if idx % 2 == 0:
                    self.actions.click(self.search_tractor)
                    send_keys_with_log(row["tractor"])
                    send_keys_with_log("{ENTER}")
                send_keys_with_log("%2")
                wait_for_window("Create Gate Grounding")
                self.actions.click(self.create_grounding_cntr)
                send_keys_with_log(row["cntr_id"])
                if idx % 2 == 0:
                    self.actions.click(self.create_grounding_driver)
                    send_keys_with_log(row["tractor"])
                send_keys_with_log("{ENTER}")

                if wait_for_window(".*gatex1536$", 1):
                    send_keys_with_log("{ENTER}")

                if not self.properties.editable(self.create_grounding_size):
                    raise

                self.actions.click(self.create_grounding_size)
                send_keys_with_log(self.size)
                send_keys_with_log(self.type)
                self.actions.click(self.create_grounding_ok_btn)

                if wait_for_window(".*Gate Inspection$", 1):
                    send_keys_with_log("{ENTER}")
                    self.actions.click(self.gate_inspection_ok_btn)
                    self.actions.click(self.create_grounding_ok_btn)

                if not self.properties.editable(self.create_grounding_material):
                    raise

                self.actions.click(self.create_grounding_material)
                send_keys_with_log(self.material)
                send_keys_with_log(self.max_gross_wt[:2])
                send_keys_with_log("y")
                self.actions.click(self.create_grounding_ok_btn)

                if idx % 2 != 0:
                    self.actions.click(self.create_grounding_FA)
                    send_keys_with_log("a")

                self.actions.click(self.create_grounding_gross_wt)
                send_keys_with_log(self.gross_wt)
                self.actions.click(self.create_grounding_ok_btn)

                if wait_for_window(".*gatex0792$", 1):
                    send_keys_with_log(self.username, with_tab=True)
                    send_keys_with_log(self.password)
                    send_keys_with_log("{ENTER}")

                if wait_for_window(".*gatex3276$", 1):
                    send_keys_with_log(self.username, with_tab=True)
                    send_keys_with_log(self.password)
                    send_keys_with_log("{ENTER}")

                if not self.properties.editable(self.create_grounding_gross_wt):
                    self.actions.click(self.create_grounding_ok_btn)
                else:
                    raise

                if idx % 2 != 0:
                    if wait_for_window(".*gatex2153$", 1):
                        send_keys_with_log("{ENTER}")

                    if wait_for_window(".*gatex1990$", 1):
                        send_keys_with_log("{ENTER}")

                if wait_for_window(".*gatex1990$", 1):
                    send_keys_with_log("{ENTER}")

                if wait_for_window(".*gatex1247$", 1):
                    send_keys_with_log("{ENTER}")
                else:
                    raise

                if wait_for_window(".*cbo0644$", 1):
                    send_keys_with_log("{ENTER}")

                if wait_for_window("Confirm"):
                    send_keys_with_log("{ENTER}")
                else:
                    raise

                if not self.properties.enabled(self.gate_transaction_refresh_btn):
                    raise

            self.release_print_cwp()
        except Exception as e:
            logger.error(f"Create gate grounding failed: {e}")
            raise

    def get_tractor(self) -> None:
        """Generate tractor IDs and update DataFrame."""
        try:
            count = len(self.gate_pickup_df)
            if count == 0:
                logger.error("DataFrame is empty")
                raise ValueError("Empty DataFrame")
            self.tractor_list = [f"OXT{i:02d}" for i in range(1, count + 1)]
            self.gate_pickup_df["tractor"] = self.tractor_list
            logger.info(f"Updated DataFrame with tractors: {self.gate_pickup_df}")
            # Save to CSV, not Excel
            self.gate_pickup_df.to_csv(self.gate_pickup_data_path, index=False)
            logger.debug(f"Saved DataFrame to {self.gate_pickup_data_path}")
        except Exception as e:
            logger.error(f"Failed to update tractors: {e}")
            raise

    def _get_tractor(self) -> None:
        try:
            count = len(self.gate_ground_df)
            if count == 0:
                logger.error("DataFrame is empty")
                raise ValueError("Empty DataFrame")

            num_tractors = math.ceil(count / 2)
            self.tractor_list = [f"OXT{i:02d}" for i in range(1, num_tractors + 1) for _ in range(2)][:count]

            self.gate_ground_df["tractor"] = self.tractor_list
            logger.info(f"Updated DataFrame with tractors: {self.gate_pickup_df}")

            # Save to CSV, not Excel
            self.gate_ground_df.to_csv(self.gate_ground_data_path, index=False)
            logger.debug(f"Saved DataFrame to {self.gate_ground_data_path}")
        except Exception as e:
            logger.error(f"Failed to update tractors: {e}")
            raise

    def release_print_cwp(self) -> None:
        """Release and print CWP for a transaction."""
        try:
            self.actions.click(self.title)
            send_keys_with_log("%3")
            if self.properties.enabled(self.print_cms_btn):
                send_keys_with_log("%7")

            if wait_for_window("Print CMS"):
                send_keys_with_log(self.gate_settings["printer"])
                send_keys_with_log("{ENTER}")
            else:
                raise RuntimeError("Print window not found")

            if wait_for_window(".*gatex1305$"):
                send_keys_with_log("{ENTER}")
            else:
                raise RuntimeError("User Information window not found")

        except Exception as e:
            logger.error(f"Release print CWP failed: {e}")
            raise

    def confirm_pickup(self) -> None:
        """Confirm pickup transactions for tractors."""
        try:
            if not self.properties.visible(self.search_tractor, timeout=1):
                self.module_view(self.module)

            for tractor in self.gate_pickup_df["tractor"]:
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

    def confirm_ground(self) -> None:
        try:
            if not self.properties.visible(self.search_tractor, timeout=1):
                self.module_view(self.module)

            self.actions.click(self.gate_transaction_refresh_btn)

            for idx, row in self.gate_ground_df.iterrows():
                if idx % 2 != 0:
                    self.actions.click(self.search_tractor)
                    send_keys_with_log(row["tractor"])
                send_keys_with_log("%4")
                if wait_for_window("Gate Confirm Information", timeout=5):
                    self.actions.click(self.gate_confirm_manual_confirm_btn)
                else:
                    raise RuntimeError("Gate Confirm window not found")

                if wait_for_window("Gate Confirm", timeout=5):
                    send_keys_with_log("{ENTER}")
                else:
                    raise RuntimeError("Gate Confirm window not found")

        except Exception as e:
            logger.error(f"Confirm ground failed: {e}")
            raise

    def run_method(self, method_name: str) -> None:
        """Execute a specified method by name."""
        methods = {
            "create_pickup": self.create_pickup,
            "confirm_pickup": self.confirm_pickup,
            "create_gate_ground": self.create_gate_ground,
            "confirm_ground": self.confirm_ground,
            "release_print_cwp": self.release_print_cwp,
        }
        method = methods.get(method_name)
        if method is None:
            logger.error(f"Invalid method: {method_name}")
            raise ValueError(f"Method {method_name} not found")
        logger.info(f"Running method: {method_name}")
        method()

if __name__ == "__main__":
    # python -m test_ui.flow.gate_transaction create_gate_ground
    # python -m test_ui.flow.gate_transaction release_print_cwp
    parser = argparse.ArgumentParser(description="Gate Transaction Automation")
    parser.add_argument(
        "method",
        choices=["create_pickup", "confirm_pickup", "create_gate_ground", "release_print_cwp", "confirm_ground"],
        help="Method to execute (create_pickup or confirm_pickup)"
    )
    args = parser.parse_args()

    try:
        gt = GateTransaction()
        gt.run_method(args.method)
    except Exception as e:
        logger.error(f"GateTransaction failed: {e}")
        sys.exit(1)