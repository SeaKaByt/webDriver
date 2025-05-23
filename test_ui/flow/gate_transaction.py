import argparse
from pathlib import Path
import pandas as pd
from pandas.errors import EmptyDataError
from helper.io_utils import read_csv
from helper.logger import logger
from helper.win_utils import wait_for_window, send_keys_with_log
from test_ui.base_flow import BaseFlow

class GateTransaction(BaseFlow):
    module = "GT"

    def __init__(self):
        super().__init__()
        self.ngen_config = self.config["nGen"]
        self.gt_config = self.config["gt"]
        self.create_pickup_config = self.gt_config["create_pickup"]

    def create_gate_pickup(self) -> None:
        df, p = next(self.get_gate_pickup_data())
        self.get_tractor(df, p)
        df_filtered = df[df["mvt"].isna()]
        if df_filtered.empty:
            raise EmptyDataError("No data to process")

        if not self.properties.visible(self.gt_config["search_tractor"], timeout=1):
            self.module_view(self.module)

        for tractor, group in df_filtered.groupby("tractor"):
            logger.info(f"Processing tractor group: {tractor}, size: {len(group)}")
            if self.properties.editable(self.gt_config["search_tractor"]):
                self.actions.set_text(self.gt_config["search_tractor"], tractor)
                send_keys_with_log("{ENTER}")
            else:
                raise RuntimeError("Search tractor field not editable")

            for _, row in group.iterrows():
                logger.info(f"Processing pickup for cntr_id: {row['cntr_id']}, tractor: {row['tractor']}, pin: {row['pin']}")
                if self.properties.enabled(self.gt_config["pickup_btn"]):
                    send_keys_with_log("%1")
                else:
                    raise RuntimeError("Pickup button not enabled")

                if wait_for_window("Create Pickup"):
                    self.actions.click(self.create_pickup_config["pin"])
                    send_keys_with_log(str(row["pin"])[:6])
                    # self.actions.click(self.create_pickup_config["tag"])
                    # send_keys_with_log(row["tractor"])
                    self.actions.click(self.create_pickup_config["driver"])
                    send_keys_with_log(row["tractor"])
                    send_keys_with_log("{ENTER}")
                else:
                    raise RuntimeError("Create Pickup window not found")

                if wait_for_window(".*gatex0225$"):
                    send_keys_with_log("{ENTER}")
                else:
                    raise RuntimeError("gatex0225 window not found")

                self.handle_auth_window(".*gatex3276$")
                self.actions.click(self.gt_config["create_pickup_ok_btn"])

                if wait_for_window("Confirmation"):
                    send_keys_with_log("{ENTER}")
                else:
                    raise RuntimeError("Confirmation window not found")

                df.loc[df["cntr_id"] == row["cntr_id"], "mvt"] = "C"
                df.to_csv(p, index=False)

            self.actions.click(self.gt_config["gate_transaction_refresh_btn"])
            self.release_print_cwp()

    def create_gate_ground(self) -> None:
        df, p = next(self.get_gate_ground_data())
        self.get_tractor(df, p)
        df_filtered = df[df["mvt"].isna()]
        if df_filtered.empty:
            raise EmptyDataError("No data to process")

        if not self.properties.visible(self.gt_config["search_tractor"], timeout=1):
            self.module_view(self.module)

        for tractor, group in df_filtered.groupby("tractor"):
            logger.info(f"Processing tractor group: {tractor}, cntr_id: {group['cntr_id'].tolist()}")
            if self.properties.editable(self.gt_config["search_tractor"]):
                self.actions.set_text(self.gt_config["search_tractor"], tractor)
                send_keys_with_log("{ENTER}")
            else:
                raise RuntimeError("Search tractor field not editable")

            for i, (_, row) in enumerate(group.iterrows()):
                logger.info(f"Processing ground for cntr_id: {row['cntr_id']}, tractor: {row['tractor']}")
                if self.properties.enabled(self.gt_config["ground_btn"]):
                    send_keys_with_log("%2")
                else:
                    raise RuntimeError("Ground button not enabled")

                if wait_for_window("Create Gate Grounding"):
                    self.actions.set_text(self.gt_config["create_grounding_cntr"], row["cntr_id"])
                    if i == 0:
                        self.actions.set_text(self.gt_config["create_grounding_driver"], row["tractor"])
                    send_keys_with_log("{ENTER}")
                else:
                    raise RuntimeError("Create Gate Grounding window not found")

                if wait_for_window(".*gatex1536$", 1):
                    send_keys_with_log("{ENTER}")

                if self.properties.editable(self.gt_config["create_grounding_size"]):
                    self.actions.set_text(self.gt_config["create_grounding_size"], str(row["size"]))
                    send_keys_with_log(self.type)
                    self.actions.click(self.gt_config["create_grounding_ok_btn"])
                else:
                    self.actions.click(self.gt_config["create_grounding_ok_btn"])

                if wait_for_window(".*Gate Inspection$", 1):
                    send_keys_with_log("%c")
                    self.actions.click(self.gt_config["gate_inspection_ok_btn"])
                    self.actions.click(self.gt_config["create_grounding_ok_btn"])
                else:
                    self.actions.click(self.gt_config["create_grounding_ok_btn"])

                if self.properties.editable(self.gt_config["create_grounding_material"]):
                    self.actions.set_text(self.gt_config["create_grounding_material"], self.material)
                    send_keys_with_log(self.max_gross_wt[:2])
                    send_keys_with_log("y")
                    self.actions.click(self.gt_config["create_grounding_ok_btn"])
                    if i == 1:
                        self.actions.set_text(self.gt_config["create_grounding_FA"], "a")
                    self.actions.set_text(self.gt_config["create_grounding_gross_wt"], self.gross_wt)
                    self.actions.click(self.gt_config["create_grounding_ok_btn"])

                self.handle_auth_window(".*gatex0792$", 1)
                self.handle_auth_window(".*gatex3276$", 1)

                if not self.properties.editable(self.gt_config["create_grounding_gross_wt"], 1):
                    self.actions.click(self.gt_config["create_grounding_ok_btn"])
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

                df.loc[df["cntr_id"] == row["cntr_id"], "mvt"] = "C"
                df.to_csv(p, index=False)

                self.actions.click(self.gt_config["gate_transaction_refresh_btn"])
            self.release_print_cwp()

    @staticmethod
    def get_tractor(df: pd.DataFrame, path: Path) -> None:
        tractor_path = Path("data/tractor_usage.csv")
        tractor_df = read_csv(tractor_path)
        twin_col = "twin_ind"

        if twin_col not in df.columns:
            df[twin_col] = "S"
        if not df[twin_col].isin(["T", "S"]).all():
            raise ValueError("twin_ind must be 'T' or 'S'")

        df_filtered = df[df["tractor"].isna() & df["mvt"].isna()]
        if df_filtered.empty:
            return

        available_tractors = tractor_df[(tractor_df["reserved"] != "Y") & (tractor_df["problem"] != "Y")]
        if available_tractors.empty:
            raise EmptyDataError(f"No available tractors in {tractor_path}")

        twin_indices = df_filtered.index[df_filtered[twin_col] == "T"].tolist()
        for i in range(0, len(twin_indices), 2):
            if i + 1 < len(twin_indices):
                if not available_tractors.empty:
                    tractor_id = available_tractors.iloc[0]["tractor_id"]
                    df.loc[twin_indices[i:i + 2], "tractor"] = tractor_id
                    tractor_df.loc[tractor_df["tractor_id"] == tractor_id, "reserved"] = "Y"
                    available_tractors = available_tractors[available_tractors["tractor_id"] != tractor_id]

        single_indices = df_filtered.index[df_filtered[twin_col] == "S"].tolist()
        for idx in single_indices:
            if not available_tractors.empty:
                tractor_id = available_tractors.iloc[0]["tractor_id"]
                df.loc[idx, "tractor"] = tractor_id
                tractor_df.loc[tractor_df["tractor_id"] == tractor_id, "reserved"] = "Y"
                available_tractors = available_tractors[available_tractors["tractor_id"] != tractor_id]

        logger.info(f"Assigned tractors: {df[[twin_col, 'tractor']].to_dict()}")
        df.to_csv(path, index=False)
        tractor_df.to_csv(tractor_path, index=False)

    def release_print_cwp(self) -> None:
        try:
            self.actions.click(self.gt_config["gate_transaction_refresh_btn"])
            if self.properties.enabled(self.gt_config["release_btn"]):
                send_keys_with_log("%3")
            else:
                raise RuntimeError("Release button not enabled")

            if self.properties.enabled(self.gt_config["print_cms_btn"]):
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
        try:
            if not self.properties.visible(self.gt_config["search_tractor"], timeout=1):
                self.module_view(self.module)

            df, p = next(self.get_gate_pickup_data())

            for tractor, group in df.groupby("tractor"):
                self.actions.click(self.gt_config["gate_transaction_refresh_btn"])
                self.actions.click(self.gt_config["search_tractor"])
                send_keys_with_log(tractor)
                send_keys_with_log("%s")

                if self.properties.enabled(self.gt_config["confirm_btn"]):
                    send_keys_with_log("%4")
                else:
                    raise RuntimeError("Confirm button not enabled")

                twin_ind = group["twin_ind"].iloc[0]
                if twin_ind == "T":
                    if wait_for_window("Confirm"):
                        self.actions.click(self.gt_config["confirm_yes_btn"])
                    else:
                        raise RuntimeError("Confirm window not found")

                    for _, row in group.iterrows():
                        if wait_for_window("Exit Gate Inspection"):
                            self.actions.click(self.gt_config["exit_gate_inspection_size"])
                            send_keys_with_log(row["size"])
                            send_keys_with_log(self.type)
                            self.actions.click(self.gt_config["inspection_seal"])
                            send_keys_with_log(self.seal_ind)
                            if row["status"] == "IF":
                                send_keys_with_log("F")
                            elif row["status"] == "EM":
                                send_keys_with_log("E")
                            send_keys_with_log(self.oog_ind)
                            send_keys_with_log("{ENTER}")

                    for idx, row in group.iterrows():
                        if wait_for_window("Gate Confirm Information"):
                            self.actions.click(self.gt_config["gate_confirm_manual_confirm_btn"])
                        else:
                            raise RuntimeError("Gate Confirm Information window not found")

                        if idx == group.index[0] and wait_for_window("Gate Confirm"):
                            send_keys_with_log("{ENTER}")
                        elif idx == group.index[0]:
                            raise RuntimeError("Gate Confirm window not found")

                elif twin_ind == "S":
                    if wait_for_window("Confirm"):
                        self.actions.click(self.gt_config["confirm_yes_btn"])
                    else:
                        raise RuntimeError("Confirmation window not found")

                    if wait_for_window("Exit Gate Inspection", timeout=1):
                        send_keys_with_log(group["size"].iloc[0])
                        send_keys_with_log(self.type)
                        self.actions.click(self.gt_config["inspection_seal"])
                        send_keys_with_log(self.seal_ind)
                        if group["status"].iloc[0] == "IF":
                            send_keys_with_log("F")
                        elif group["status"].iloc[0] == "EM":
                            send_keys_with_log("E")
                        send_keys_with_log(self.oog_ind)
                        send_keys_with_log("{ENTER}")

                    if wait_for_window("Gate Confirm Information"):
                        self.actions.click(self.gt_config["gate_confirm_manual_confirm_btn"])
                    else:
                        raise RuntimeError("Gate Confirm Information window not found")

                    if wait_for_window("Gate Confirm"):
                        send_keys_with_log("{ENTER}")
                    else:
                        raise RuntimeError("Gate Confirm window not found")

        except Exception as e:
            raise RuntimeError(f"Confirm pickup failed: {e}")

    def confirm_ground(self) -> None:
        try:
            if not self.properties.visible(self.gt_config["search_tractor"], timeout=1):
                self.module_view(self.module)

            df, p = next(self.get_gate_ground_data())

            for idx, row in df.iterrows():
                self.actions.click(self.gt_config["gate_transaction_refresh_btn"])
                if idx % 2 == 0:
                    self.actions.set_text(self.gt_config["search_tractor"], row["tractor"])
                    send_keys_with_log("%s")
                send_keys_with_log("%4")

                if wait_for_window("Gate Confirm Information", timeout=2):
                    self.actions.click(self.gt_config["gate_confirm_manual_confirm_btn"])
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
            send_keys_with_log(self.ngen_config["username"], with_tab=True)
            send_keys_with_log(self.ngen_config["password"])
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
        method = methods.get(method_name)
        if method is None:
            raise ValueError(f"Unknown method: {method_name}")
        logger.info(f"Running method: {method_name}")
        method()

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