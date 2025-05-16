import argparse
from pathlib import Path
import pandas as pd
from helper.logger import logger
from helper.win_utils import wait_for_window, send_keys_with_log
from test_ui.base_flow import BaseFlow

class GateTransaction(BaseFlow):
    """Handles gate transaction UI flows for pickup, grounding, and confirmation."""
    module = "GT"

    def __init__(self):
        super().__init__()
        self.username = self.config["nGen"]["username"]
        self.password = self.config["nGen"]["password"]
        gt_config = self.config["gt"]
        self.search_tractor = gt_config["search_tractor"]
        self.create_pin = gt_config["create_pin"]
        self.create_driver = gt_config["create_driver"]
        self.inspection_seal = gt_config["inspection_seal"]
        self.manual_confirm_btn = gt_config["manual_confirm_btn"]
        self.pickup_btn = gt_config["pickup_btn"]
        self.ground_btn = gt_config["ground_btn"]
        self.confirm_btn = gt_config["confirm_btn"]
        self.create_grounding_cntr = gt_config["create_grounding_cntr"]
        self.create_grounding_driver = gt_config["create_grounding_driver"]
        self.create_grounding_owner = gt_config["create_grounding_owner"]
        self.create_grounding_size = gt_config["create_grounding_size"]
        self.create_grounding_ok_btn = gt_config["create_grounding_ok_btn"]
        self.create_grounding_material = gt_config["create_grounding_material"]
        self.create_grounding_FA = gt_config["create_grounding_FA"]
        self.create_grounding_gross_wt = gt_config["create_grounding_gross_wt"]
        self.create_pickup_ok_btn = gt_config["create_pickup_ok_btn"]
        self.gate_inspection_ok_btn = gt_config["gate_inspection_ok_btn"]
        self.gate_transaction_refresh_btn = gt_config["gate_transaction_refresh_btn"]
        self.gate_confirm_manual_confirm_btn = gt_config["gate_confirm_manual_confirm_btn"]
        self.exit_gate_inspection_size = gt_config["exit_gate_inspection_size"]
        self.release_btn = gt_config["release_btn"]
        self.print_cms_btn = gt_config["print_cms_btn"]
        self.gate_confirm_ok_btn = gt_config["gate_confirm_ok_btn"]
        self.confirm_yes_btn = gt_config["confirm_yes_btn"]

    def create_gate_pickup(self) -> None:
        df = self.gate_pickup_df
        path = self.gate_pickup_data_path

        self.get_tractor(df, path)

        if not self.properties.visible(self.search_tractor, timeout=1):
            self.module_view(self.module)

        grouped = df.groupby("tractor")
        for tractor, group in grouped:
            logger.info(f"Processing tractor group: {tractor}, size: {len(group)}")
            if self.properties.editable(self.search_tractor):
                self.actions.set_text(self.search_tractor, tractor)
                send_keys_with_log("{ENTER}")
            else:
                raise RuntimeError("Search tractor field not editable")

            for _, row in group.iterrows():
                logger.info(
                    f"Processing pickup for cntr_id: {row['cntr_id']}, tractor: {row['tractor']}, pin: {row['pin']}")
                if self.properties.enabled(self.pickup_btn):
                    send_keys_with_log("%1")
                else:
                    raise RuntimeError("Pickup button not enabled")

                if wait_for_window("Create Pickup"):
                    self.actions.set_text(self.create_pin, str(row["pin"]))
                    self.actions.set_text(self.create_driver, row["tractor"])
                    send_keys_with_log("{ENTER}")
                else:
                    raise RuntimeError("Create Pickup window not found")

                if wait_for_window(".*gatex0225$"):
                    send_keys_with_log("{ENTER}")
                else:
                    raise RuntimeError("gatex0225 window not found!")

                self.handle_auth_window(".*gatex3276$")
                self.actions.click(self.create_pickup_ok_btn)

                if wait_for_window("Confirmation"):
                    send_keys_with_log("{ENTER}")
                else:
                    raise RuntimeError("Confirmation window not found")

            self.actions.click(self.gate_transaction_refresh_btn)
            self.release_print_cwp()

    def create_gate_ground(self) -> None:
        self.get_tractor(self.gate_ground_df, self.gate_ground_data_path)

        if not self.properties.visible(self.search_tractor, 1):
            self.module_view(self.module)

        grouped = self.gate_ground_df.groupby("tractor")
        for tractor, group in grouped:
            logger.info(f"Processing tractor group: {tractor}, cntr_id: {group['cntr_id'].tolist()}")
            if self.properties.editable(self.search_tractor):
                self.actions.set_text(self.search_tractor, tractor)
                send_keys_with_log("{ENTER}")
            else:
                raise RuntimeError("Search tractor field not editable")

            for i, (_, row) in enumerate(group.iterrows()):
                logger.info(f"Processing ground for cntr_id: {row['cntr_id']}, tractor: {row['tractor']}")
                if self.properties.enabled(self.ground_btn):
                    send_keys_with_log("%2")
                else:
                    raise RuntimeError("Ground button not enabled")

                if wait_for_window("Create Gate Grounding"):
                    self.actions.set_text(self.create_grounding_cntr, row["cntr_id"])
                    if i == 0:
                        self.actions.set_text(self.create_grounding_driver, row["tractor"])
                    send_keys_with_log("{ENTER}")
                else:
                    raise RuntimeError("Create Gate Grounding window not found")

                if wait_for_window(".*gatex1536$", 1):
                    send_keys_with_log("{ENTER}")

                if self.properties.editable(self.create_grounding_size):
                    self.actions.set_text(self.create_grounding_size, str(row["size"]))
                    send_keys_with_log(self.type)
                    self.actions.click(self.create_grounding_ok_btn)
                else:
                    self.actions.click(self.create_grounding_ok_btn)

                if wait_for_window(".*Gate Inspection$", 1):
                    send_keys_with_log("%c")
                    self.actions.click(self.gate_inspection_ok_btn)
                    self.actions.click(self.create_grounding_ok_btn)
                else:
                    self.actions.click(self.create_grounding_ok_btn)

                if self.properties.editable(self.create_grounding_material):
                    self.actions.set_text(self.create_grounding_material, self.material)
                    send_keys_with_log(self.max_gross_wt[:2])
                    send_keys_with_log("y")
                    self.actions.click(self.create_grounding_ok_btn)
                    if i == 1:
                        self.actions.set_text(self.create_grounding_FA, "a")
                    self.actions.set_text(self.create_grounding_gross_wt, self.gross_wt)
                    self.actions.click(self.create_grounding_ok_btn)

                self.handle_auth_window(".*gatex0792$", 1)
                self.handle_auth_window(".*gatex3276$", 1)

                if not self.properties.editable(self.create_grounding_gross_wt, 1):
                    self.actions.click(self.create_grounding_ok_btn)
                else:
                    raise RuntimeError("Create Grounding Gross Weight field should not be editable")

                if i == 1 and wait_for_window(".*gatex2153$", 1):
                    send_keys_with_log("{ENTER}")

                for window in [".*gatex1990$", ".*gatex1247$", ".*cbo0644$"]:
                    if wait_for_window(window, 1):
                        send_keys_with_log("{ENTER}")
                    elif window == ".*gatex1247$":
                        raise RuntimeError("gatex1247 window not found")

                if wait_for_window("Confirm"):
                    send_keys_with_log("{ENTER}")
                else:
                    raise RuntimeError("Confirm window not found")

                self.actions.click(self.gate_transaction_refresh_btn)
            self.release_print_cwp()

    @staticmethod
    def get_tractor(df: pd.DataFrame, path: Path, twin_col: str = "twin_ind", tractor_prefix: str = "XT") -> None:
        if df.empty:
            raise ValueError("DataFrame is empty")
        if twin_col not in df.columns:
            df[twin_col] = "S"
        if not df[twin_col].isin(["T", "S"]).all():
            raise ValueError("twin_ind must be 'T' or 'S'")

        df['tractor'] = None
        tractor_counter = 1

        twin_indices = df.index[df[twin_col] == "T"].tolist()
        for i in range(0, len(twin_indices), 2):
            tractor_id = f"{tractor_prefix}{str(tractor_counter).zfill(3)}"
            df.loc[twin_indices[i:i+2], 'tractor'] = tractor_id
            tractor_counter += 1

        single_indices = df.index[df[twin_col] == "S"].tolist()
        for idx in single_indices:
            df.loc[idx, 'tractor'] = f"{tractor_prefix}{str(tractor_counter).zfill(3)}"
            tractor_counter += 1

        logger.info(f"Assigned tractors: {df[[twin_col, 'tractor']].to_dict()}")
        df.to_csv(path, index=False)

    def release_print_cwp(self) -> None:
        try:
            self.actions.click(self.gate_transaction_refresh_btn)
            if self.properties.enabled(self.release_btn):
                send_keys_with_log("%3")
            else:
                raise RuntimeError("Release button not enabled")

            if self.properties.enabled(self.print_cms_btn):
                send_keys_with_log("%7")
            else:
                raise RuntimeError("Print CMS button not enabled")

            if wait_for_window("Print CMS"):
                send_keys_with_log("{ENTER}")
            else:
                raise RuntimeError("Print CMS window not found")

            if wait_for_window(".*gatex1305$"):
                send_keys_with_log("{ENTER}")
            else:
                raise RuntimeError("User Information window not found")

        except Exception as e:
            raise RuntimeError(f"Release print CWP failed: {e}")

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
                            send_keys_with_log(row["size"])
                            send_keys_with_log(self.type)
                            self.actions.click(self.inspection_seal)
                            send_keys_with_log(self.seal_ind)
                            if row["status"] == "IF":
                                send_keys_with_log("F")
                            elif row["status"] == "EM":
                                send_keys_with_log("E")
                            send_keys_with_log(self.oog_ind)
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
                        raise RuntimeError("Confirmation window not found")

                    # Process Exit Gate Inspection
                    if wait_for_window("Exit Gate Inspection", timeout=1):
                        send_keys_with_log(group["size"])
                        send_keys_with_log(self.type)
                        self.actions.click(self.inspection_seal)
                        send_keys_with_log(self.seal_ind)
                        if group["status"] == "IF":
                            send_keys_with_log("F")
                        elif group["status"] == "EM":
                            send_keys_with_log("E")
                        send_keys_with_log(self.oog_ind)
                        send_keys_with_log("{ENTER}")

                    # Process Gate Confirm Information
                    if wait_for_window("Gate Confirm Information"):
                        self.actions.click(self.gate_confirm_manual_confirm_btn)
                    else:
                        raise RuntimeError("Gate Confirm Information window not found")

                    # Process Gate Confirm
                    if wait_for_window("Gate Confirm"):
                        send_keys_with_log("{ENTER}")
                    else:
                        raise RuntimeError("Gate Confirm window not found")

        except Exception as e:
            raise RuntimeError(f"Confirm pickup failed: {e}")

    def confirm_ground(self) -> None:
        try:
            if not self.properties.visible(self.search_tractor, timeout=1):
                self.module_view(self.module)

            for idx, row in self.gate_ground_df.iterrows():
                self.actions.click(self.gate_transaction_refresh_btn)
                if idx % 2 == 0:
                    self.actions.set_text(self.search_tractor, row["tractor"])
                    send_keys_with_log("%s")
                send_keys_with_log("%4")

                if wait_for_window("Gate Confirm Information", timeout=2):
                    self.actions.click(self.gate_confirm_manual_confirm_btn)
                else:
                    raise RuntimeError("Gate Confirm Information window not found")

                if wait_for_window("Gate Confirm", timeout=5):
                    send_keys_with_log("{ENTER}")
                else:
                    raise RuntimeError("Gate Confirm window not found")

        except Exception as e:
            raise RuntimeError(f"Confirm ground failed: {e}")

    def handle_auth_window(self, window_pattern: str, timeout: int = 1) -> None:
        if wait_for_window(window_pattern, timeout):
            send_keys_with_log(self.username, with_tab=True)
            send_keys_with_log(self.password)
            send_keys_with_log("{ENTER}")
        else:
            raise RuntimeError(f"Authentication window {window_pattern} not found")

    def run_method(self, method_name: str) -> None:
        methods = {
            "create_gate_pickup": self.create_gate_pickup,
            "confirm_pickup": self.confirm_pickup,
            "create_gate_ground": self.create_gate_ground,
            "confirm_ground": self.confirm_ground,
            "release_print_cwp": self.release_print_cwp,
        }
        _method = methods.get(method_name)
        if _method is None:
            raise ValueError(f"Unknown method: {method_name}")
        logger.info(f"Running method: {method_name}")
        _method()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gate Transaction Automation")
    parser.add_argument(
        "--methods",
        nargs="+",
        choices=["create_gate_pickup", "confirm_pickup", "create_gate_ground", "release_print_cwp", "confirm_ground"],
        help="List of methods to execute in order",
    )
    args = parser.parse_args()

    gt = GateTransaction()
    for method in args.methods:
        gt.run_method(method)