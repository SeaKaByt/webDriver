import argparse
import sys
from typing import Optional
from pathlib import Path
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
            self.inspection_seal = gt_config.get("inspection_seal")
            self.manual_confirm_btn = gt_config.get("manual_confirm_btn")
            self.pickup_btn = gt_config.get("pickup_btn")
            self.ground_btn = gt_config.get("ground_btn")
            self.confirm_btn = gt_config.get("confirm_btn")
            self.create_grounding_cntr = gt_config.get("create_grounding_cntr")
            self.create_grounding_driver = gt_config.get("create_grounding_driver")
            self.create_grounding_owner = gt_config.get("create_grounding_owner")
            self.create_grounding_size = gt_config.get("create_grounding_size")
            self.create_grounding_ok_btn = gt_config.get("create_grounding_ok_btn")
            self.create_grounding_material = gt_config.get("create_grounding_material")
            self.create_grounding_FA = gt_config.get("create_grounding_FA")
            self.create_grounding_gross_wt = gt_config.get("create_grounding_gross_wt")
            self.create_pickup_ok_btn = gt_config.get("create_pickup_ok_btn")
            self.gate_inspection_ok_btn = gt_config.get("gate_inspection_ok_btn")
            self.gate_transaction_refresh_btn = gt_config.get("gate_transaction_refresh_btn")
            self.gate_confirm_manual_confirm_btn = gt_config.get("gate_confirm_manual_confirm_btn")
            self.exit_gate_inspection_size = gt_config.get("exit_gate_inspection_size")
            self.release_btn = gt_config.get("release_btn")
            self.print_cms_btn = gt_config.get("print_cms_btn")
            self.gate_confirm_ok_btn = gt_config.get("gate_confirm_ok_btn")
            self.confirm_yes_btn = gt_config.get("confirm_yes_btn")
            self.gate_settings = self.config.get("gate_settings", {
                "size_type": "2000",
                "seal_ind": "y",
                "F/E": "f",
                "OOG_ind": "n",
            })
        except KeyError as e:
            logger.error(f"Config missing key: {e}")
            raise ValueError(f"Invalid config: {e}")

    def create_pickup(self) -> None:
        """Create pickup transactions for containers."""
        try:
            # Assign tractors based on twin_ind
            self._get_tractor(self.gate_pickup_df, self.gate_pickup_data_path)

            # Validate DataFrame
            required_columns = ["cntr_id", "pin", "tractor"]
            if not all(col in self.gate_pickup_df.columns for col in required_columns):
                logger.error(f"data.csv missing columns: {required_columns}")
                raise ValueError(f"Invalid CSV: missing {required_columns}")

            # Ensure the module is visible
            if not self.properties.visible(self.search_tractor, timeout=1):
                self.module_view(self.module)

            # Group DataFrame by tractor
            grouped = self.gate_pickup_df.groupby("tractor")
            for tractor, group in grouped:
                logger.info(f"Processing tractor group: {tractor}, size: {len(group)}")

                if self.properties.editable(self.search_tractor):
                    self.actions.click(self.search_tractor)
                    send_keys_with_log(tractor)
                    send_keys_with_log("{ENTER}")
                else:
                    logger.error("Search tractor field not editable")
                    raise RuntimeError("Search tractor field not editable")

                for _, row in group.iterrows():
                    logger.info(f"Processing pickup for cntr_id: {row["cntr_id"]}, tractor: {row["tractor"]}, pin: {row["pin"]}")

                    # Initiate pickup
                    if self.properties.enabled(self.pickup_btn):
                        send_keys_with_log("%1")
                    else:
                        logger.error("Pickup button not enabled")
                        raise RuntimeError("Pickup button not enabled")

                    # Enter PIN and driver ID
                    if wait_for_window("Create Pickup"):
                        self.actions.click(self.create_pin)
                        send_keys_with_log(str(row["pin"]))
                        self.actions.click(self.create_driver)
                        send_keys_with_log(row["tractor"])
                        send_keys_with_log("{ENTER}")
                    else:
                        logger.error("Create Pickup window not found")
                        raise RuntimeError("Create Pickup window not found")

                    # Handle gatex0225 window
                    if wait_for_window(".*gatex0225$", 1):
                        send_keys_with_log("{ENTER}")
                    else:
                        logger.error("gatex0225 window not found")
                        raise RuntimeError("gatex0225 window not found")

                    # Handle gatex3276 window (authentication)
                    if wait_for_window(".*gatex3276$", 1):
                        send_keys_with_log(self.username, with_tab=True)
                        send_keys_with_log(self.password)
                        send_keys_with_log("{ENTER}")
                        self.actions.click(self.create_pickup_ok_btn)
                    else:
                        logger.error("gatex3276 window not found")
                        raise RuntimeError("gatex3276 window not found")

                    # Handle Confirmation window
                    if wait_for_window("Confirmation"):
                        send_keys_with_log("{ENTER}")
                    else:
                        logger.error("Confirmation window not found")
                        raise RuntimeError("Confirmation window not found")

                # Refresh after processing the group
                self.actions.click(self.gate_transaction_refresh_btn)

                # Finalize with print release
                self.release_print_cwp()

        except Exception as e:
            logger.error(f"Create pickup failed: {e}")
            raise

    def create_gate_ground(self) -> None:
        """Create gate grounding transactions."""
        try:
            self._get_tractor(self.gate_ground_df, self.gate_ground_data_path)

            # Validate DataFrame
            required_columns = ["cntr_id", "tractor"]
            if not all(col in self.gate_pickup_df.columns for col in required_columns):
                logger.error(f"data.csv missing columns: {required_columns}")
                raise ValueError(f"Invalid CSV: missing {required_columns}")

            # Ensure the module is visible
            if not self.properties.visible(self.search_tractor):
                self.module_view(self.module)

            # Group DataFrame by tractor
            grouped = self.gate_ground_df.groupby("tractor")
            for tractor, group in grouped:
                logger.info(f"Processing tractor group: {tractor}, cntr_id: {group['cntr_id'].tolist()}")

                if self.properties.editable(self.search_tractor):
                    self.actions.click(self.search_tractor)
                    send_keys_with_log(tractor)
                    send_keys_with_log("{ENTER}")
                else:
                    logger.error("Search tractor field not editable")
                    raise RuntimeError("Search tractor field not editable")

                for i, (idx, row) in enumerate(group.iterrows()):
                    logger.info(f"Processing ground for idx: {i}, cntr_id: {row["cntr_id"]}, tractor: {row["tractor"]}")
                    logger.info(f"Processing ground for idx: {idx}, cntr_id: {row["cntr_id"]}, tractor: {row["tractor"]}")

                    # Initiate grounding
                    if self.properties.enabled(self.ground_btn):
                        send_keys_with_log("%2")
                    else:
                        logger.error("Ground button not enabled")
                        raise RuntimeError("Ground button not enabled")

                    # Enter container ID and driver ID
                    if wait_for_window("Create Gate Grounding"):
                        self.actions.click(self.create_grounding_cntr)
                        send_keys_with_log(row["cntr_id"])
                        if i == 0:
                            self.actions.click(self.create_grounding_driver)
                            send_keys_with_log(row["tractor"])
                        send_keys_with_log("{ENTER}")

                    if wait_for_window(".*gatex1536$", 1):
                        send_keys_with_log("{ENTER}")

                    if self.properties.editable(self.create_grounding_size):
                        self.actions.click(self.create_grounding_size)
                        send_keys_with_log(str(row["size"]))
                        send_keys_with_log(self.type)
                        self.actions.click(self.create_grounding_ok_btn)
                    else:
                        self.actions.click(self.create_grounding_ok_btn)

                    # Handle Gate Inspection window
                    if wait_for_window(".*Gate Inspection$", 1):
                        send_keys_with_log("%c")
                        self.actions.click(self.gate_inspection_ok_btn)
                        self.actions.click(self.create_grounding_ok_btn)
                    else:
                        self.actions.click(self.create_grounding_ok_btn)

                    if self.properties.editable(self.create_grounding_material):
                        self.actions.click(self.create_grounding_material)
                        send_keys_with_log(self.material)
                        send_keys_with_log(self.max_gross_wt[:2])
                        send_keys_with_log("y")
                        self.actions.click(self.create_grounding_ok_btn)
                        if i == 1:
                            self.actions.click(self.create_grounding_FA)
                            send_keys_with_log("a")
                        self.actions.click(self.create_grounding_gross_wt)
                        send_keys_with_log(self.gross_wt)
                        self.actions.click(self.create_grounding_ok_btn)

                    if wait_for_window(".*gatex0792$", 1):
                        send_keys_with_log(self.username, with_tab=True)
                        send_keys_with_log(self.password)
                        send_keys_with_log("{ENTER}")

                    if wait_for_window(".*gatex3276$", 2):
                        send_keys_with_log(self.username, with_tab=True)
                        send_keys_with_log(self.password)
                        send_keys_with_log("{ENTER}")

                    if not self.properties.editable(self.create_grounding_gross_wt, timeout=1):
                        self.actions.click(self.create_grounding_ok_btn)
                    else:
                        logger.error("Create Grounding Gross Weight field should not editable")
                        raise RuntimeError("Create Grounding Gross Weight field should not editable")

                    if i == 1:
                        if wait_for_window(".*gatex2153$", 1):
                            send_keys_with_log("{ENTER}")

                    if wait_for_window(".*gatex1990$", 1):
                        send_keys_with_log("{ENTER}")

                    if wait_for_window(".*gatex1247$", 1):
                        send_keys_with_log("{ENTER}")
                    else:
                        logger.error("gatex1247 window not found")
                        raise

                    if wait_for_window(".*cbo0644$", 1):
                        send_keys_with_log("{ENTER}")

                    if wait_for_window("Confirm"):
                        send_keys_with_log("{ENTER}")
                    else:
                        logger.error("Confirm window not found")
                        raise

                    self.actions.click(self.gate_transaction_refresh_btn)

                self.release_print_cwp()
        except Exception as e:
            logger.error(f"Create gate grounding failed: {e}")
            raise

    def _get_tractor(self, df, path) -> None:
        try:
            count = len(df)
            if count == 0:
                logger.error("DataFrame is empty")
                raise ValueError("Empty DataFrame")

            # Initialize tractor counter
            tractor_counter = 1
            tractor_list = [None] * len(df)

            # Separate 'T' and 'S' rows while keeping track of original indices
            twin_rows = df[df["twin_ind"] == "T"].index.tolist()
            single_rows = df[df["twin_ind"] == "S"].index.tolist()

            # Pair 'T' rows and assign shared tractor IDs
            for i in range(0, len(twin_rows), 2):
                tractor = f"XT{str(tractor_counter).zfill(3)}"
                if i + 1 < len(twin_rows):
                    # Pair the two 'T' rows
                    tractor_list[twin_rows[i]] = tractor
                    tractor_list[twin_rows[i + 1]] = tractor
                    tractor_counter += 1
                else:
                    # Odd number of 'T' rows, treat the last one as a single
                    tractor_list[twin_rows[i]] = tractor

            # Assign unique tractor IDs to 'S' rows
            for idx in single_rows:
                tractor = f"XT{str(tractor_counter).zfill(3)}"
                tractor_list[idx] = tractor
                tractor_counter += 1

            # Update DataFrame with tractor assignments
            df["tractor"] = tractor_list
            logger.info(f"Updated DataFrame with tractors: {df}")

            # Save to CSV
            df.to_csv(path, index=False)
        except Exception as e:
            logger.error(f"Failed to update tractors: {e}")
            raise

    def release_print_cwp(self) -> None:
        """Release and print CWP for a transaction."""
        try:
            self.actions.click(self.gate_transaction_refresh_btn)

            if self.properties.enabled(self.release_btn):
                send_keys_with_log("%3")
            else:
                raise

            if self.properties.enabled(self.print_cms_btn):
                send_keys_with_log("%7")
            else:
                raise

            if wait_for_window("Print CMS"):
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

            # Group DataFrame by tractor
            grouped = self.gate_pickup_df.groupby("tractor")
            for tractor , group in grouped:
                # Refresh and search for the tractor
                self.actions.click(self.gate_transaction_refresh_btn)
                self.actions.click(self.search_tractor)
                send_keys_with_log(tractor)
                send_keys_with_log("%s")

                if self.properties.enabled(self.confirm_btn):
                    send_keys_with_log("%4")
                else:
                    raise

                # Get the twin indicator
                twin_ind = group["twin_ind"].iloc[0]

                if twin_ind == "T":
                    # Handle twin containers
                    if wait_for_window("Confirm"):
                        self.actions.click(self.confirm_yes_btn)
                    else:
                        raise

                    # Process each row in the group (Exit Gate Inspection)
                    for _, row in group.iterrows():
                        if wait_for_window("Exit Gate Inspection"):
                            self.actions.click(self.exit_gate_inspection_size)
                            send_keys_with_log(self.gate_settings["size_type"])
                            self.actions.click(self.inspection_seal)
                            send_keys_with_log(self.gate_settings["seal_ind"])
                            send_keys_with_log(self.gate_settings["F/E"])
                            send_keys_with_log(self.gate_settings["OOG_ind"])
                            send_keys_with_log("{ENTER}")

                    # Process each row in the group (Gate Confirm Information)
                    for idx, row in group.iterrows():
                        if wait_for_window("Gate Confirm Information"):
                            self.actions.click(self.gate_confirm_manual_confirm_btn)
                        else:
                            raise

                        # Only process the first row for Gate Confirm
                        if idx == 0:
                            if wait_for_window("Gate Confirm"):
                                send_keys_with_log(self.gate_confirm_ok_btn)
                            else:
                                raise

                elif twin_ind == "S":
                    # Handle single container
                    if wait_for_window("Confirm"):
                        self.actions.click(self.confirm_yes_btn)
                    else:
                        raise

                    # Process Exit Gate Inspection
                    if wait_for_window("Exit Gate Inspection", timeout=1):
                        send_keys_with_log(self.gate_settings["size_type"])
                        self.actions.click(self.inspection_seal)
                        send_keys_with_log(self.gate_settings["seal_ind"])
                        send_keys_with_log(self.gate_settings["F/E"])
                        send_keys_with_log(self.gate_settings["OOG_ind"])
                        send_keys_with_log("{ENTER}")

                    # Process Gate Confirm Information
                    if wait_for_window("Gate Confirm Information"):
                        self.actions.click(self.gate_confirm_manual_confirm_btn)
                    else:
                        raise

                    # Process Gate Confirm
                    if wait_for_window("Gate Confirm"):
                        send_keys_with_log("{ENTER}")
                    else:
                        raise

        except Exception as e:
            logger.error(f"Confirm pickup failed: {e}")
            raise

    def confirm_ground(self) -> None:
        try:
            if not self.properties.visible(self.search_tractor, timeout=1):
                self.module_view(self.module)

            for idx, row in self.gate_ground_df.iterrows():
                self.actions.click(self.gate_transaction_refresh_btn)
                if idx % 2 == 0:
                    self.actions.click(self.search_tractor)
                    send_keys_with_log(row["tractor"])
                    send_keys_with_log("%s")
                send_keys_with_log("%4")
                if wait_for_window("Gate Confirm Information"):
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