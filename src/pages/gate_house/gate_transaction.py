import os
import time
import pandas as pd

from pathlib import Path
from pandas.errors import EmptyDataError
from src.core.driver import BaseDriver
from helper.http.TAS_service import AppointmentService
from helper.logger import logger
from helper.paths import ProjectPaths
from helper.win_utils import wait_for_window, sendkeys, find_window
from src.common.menu import Menu

class GateTransaction(BaseDriver):
    MODULE = "GT"

    def __init__(self, external_driver=None):
        super().__init__(external_driver=external_driver)
        self.service = AppointmentService()
        self.gt = self.config["gt"]
        self.cp = self.gt["create_pickup"]
        self.cg = self.gt["create_grounding"]
        self.ins = self.cg["inspection"]

        self.type = "10"
        self.material = "S"
        self.gross_wt = "17500"
        self.max_gross = "32000"

    def create_gate_pickup(self) -> None:
        df, p = next(ProjectPaths.get_gate_pickup_data())
        self.get_tractor(df, p)

        df_filtered = df[df["mvt"].isna() & df["tractor"].notna() & df["pin"].notna()]
        if df_filtered.empty:
            raise EmptyDataError("No data to process")

        if not self.properties.visible(self.gt["search_tractor"], timeout=1):
            Menu.to_module(self.MODULE, self)

        for tractor, group in df_filtered.groupby("tractor"):
            logger.info(f"Processing tractor group: {tractor}, size: {len(group)}")
            if self.properties.editable(self.gt["search_tractor"]):
                self.actions.click(self.gt["search_tractor"])
                sendkeys(tractor)
                sendkeys("{ENTER}")
            else:
                raise RuntimeError("Search tractor field not editable")

            for _, row in group.iterrows():
                logger.info(f"Processing pickup for cntr_id: {row['cntr_id']}, tractor: {row['tractor']}, pin: {row['pin']}")
                self.service.create_appointment(row["cntr_id"])

                if self.properties.enabled(self.gt["pickup_btn"]):
                    sendkeys("%1")
                else:
                    raise RuntimeError("Pickup button not enabled")

                if wait_for_window("Create Pickup"):
                    self.actions.click(self.cp["pin"])
                    sendkeys(str(row["pin"])[:6])
                    self.actions.click(self.cp["driver"])
                    sendkeys(row["tractor"])
                    sendkeys("{ENTER}")
                else:
                    raise RuntimeError("Create Pickup window not found")

                if wait_for_window(".*gatex0225$"):
                    sendkeys("{ENTER}")
                else:
                    raise RuntimeError("gatex0225 window not found")

                time.sleep(1)
                if find_window(".*(gatex2421|gatex3276)$"):
                    self.handle_auth_window()

                self.actions.click(self.gt["create_pickup_ok_btn"])

                if wait_for_window("Confirmation"):
                    sendkeys("{ENTER}")
                else:
                    raise RuntimeError("Confirmation window not found")

                df.loc[df["cntr_id"] == row["cntr_id"], "mvt"] = "C"
                df.to_csv(p, index=False)

                self.actions.click(self.gt["gate_transaction_refresh_btn"])
            self.release_print_cwp()

    def create_gate_ground(self, df, p) -> None:
        # df, p = next(ProjectPaths.get_gate_ground_data())
        self.get_tractor(df, p)
        df_filtered = df[df["mvt"].isna()]
        if df_filtered.empty:
            raise EmptyDataError("No data to process")

        if not self.properties.visible(self.gt["search_tractor"], timeout=1):
            Menu.to_module(self.MODULE, self)

        for tractor, group in df_filtered.groupby("tractor"):
            logger.info(f"Processing tractor group: {tractor}, cntr_id: {group['cntr_id'].tolist()}")
            if self.properties.editable(self.gt["search_tractor"]):
                self.actions.click(self.gt["search_tractor"])
                sendkeys(tractor)
                sendkeys("{ENTER}")
            else:
                raise RuntimeError("Search tractor field not editable")

            for i, (_, row) in enumerate(group.iterrows()):
                logger.info(f"Processing ground for cntr_id: {row['cntr_id']}, tractor: {row['tractor']}")
                if self.properties.enabled(self.gt["ground_btn"]):
                    sendkeys("%2")
                else:
                    raise RuntimeError("Ground button not enabled")

                if wait_for_window("Create Gate Grounding"):
                    self.actions.click(self.cg["cntr_id"])
                    sendkeys(row["cntr_id"])
                    if i == 0:
                        self.actions.click(self.cg["driver"])
                        sendkeys(row["tractor"])
                    sendkeys("{ENTER}")
                else:
                    raise RuntimeError("Create Gate Grounding window not found")

                time.sleep(0.5)
                if find_window(".*gatex1536$"):
                    sendkeys("{ENTER}")

                if self.properties.editable(self.cg["size"]):
                    self.actions.click(self.cg["size"])
                    sendkeys(str(row["size"]))
                    sendkeys(self.type)
                    self.actions.click(self.cg["ok"])
                else:
                    self.actions.click(self.cg["ok"])

                if i == 0:
                    time.sleep(0.5)
                    if find_window(".*Gate Inspection$"):
                        sendkeys("%c")
                        self.actions.click(self.ins["ok"])
                        self.actions.click(self.cg["ok"])

                if i == 1:
                    self.actions.click(self.gt["ok"])

                if self.properties.editable(self.cg["material"]):
                    self.actions.click(self.cg["material"])
                else:
                    raise RuntimeError("Material field not editable")

                sendkeys(str(self.material))
                sendkeys(self.max_gross[:2])

                if i ==0:
                    sendkeys("Y")

                if i == 1:
                    # self.actions.click(self.cg["fa"])
                    sendkeys("A")
                    sendkeys("Y")

                self.actions.click(self.cg["ok"])

                if self.properties.editable(self.cg["gross"]):
                    sendkeys(self.gross_wt)
                else:
                    raise RuntimeError("Gross field not editable")

                self.actions.click(self.cg["ok"])

                time.sleep(0.5)
                # Appointment
                if find_window(".*(gatex2423|gatex3276)$"):
                    self.handle_auth_window()

                # if wait_for_window(".*gatex0792$", 1):
                #     self.handle_auth_window()

                self.actions.click(self.cg["ok"])

                if i == 1 and wait_for_window(".*gatex2153$", 1):
                    sendkeys("{ENTER}")

                for window in [".*gatex1990$", ".*gatex1247$", ".*cbo0644$"]:
                    time.sleep(0.5)
                    if find_window(window):
                        sendkeys("{ENTER}")
                    elif window == ".*gatex1247$":
                        raise RuntimeError("gatex1247 window not found")

                if wait_for_window("Confirm"):
                    self.actions.click(self.cg["noo"])

                time.sleep(0.5)
                if find_window(("User Error")):
                    logger.error("User Error window found")
                    raise

                df.loc[df["cntr_id"] == row["cntr_id"], "mvt"] = "C"
                df.to_csv(p, index=False)

                self.actions.click(self.gt["refresh"])
            self.release_print_cwp()

    def get_tractor(self, df: pd.DataFrame, path: Path) -> None:
        tdf, tp = next(ProjectPaths.get_tractor_usage_data())
        twin_col = "twin_ind"

        if twin_col not in df.columns:
            df[twin_col] = "S"
        if not df[twin_col].isin(["T", "S"]).all():
            raise ValueError("twin_ind must be 'T' or 'S'")

        df_filtered = df[df["tractor"].isna() & df["mvt"].isna()]
        if df_filtered.empty:
            return

        available_tractors = tdf[(tdf["reserved"] != "Y") & (tdf["problem"] != "Y")]
        if available_tractors.empty:
            raise EmptyDataError(f"No available tractors in {tp}")

        twin_indices = df_filtered.index[df_filtered[twin_col] == "T"].tolist()
        for i in range(0, len(twin_indices), 2):
            if i + 1 < len(twin_indices):
                if not available_tractors.empty:
                    tractor_id = available_tractors.iloc[0]["tractor_id"]
                    df.loc[twin_indices[i:i + 2], "tractor"] = tractor_id
                    tdf.loc[tdf["tractor_id"] == tractor_id, "reserved"] = "Y"
                    available_tractors = available_tractors[available_tractors["tractor_id"] != tractor_id]

        single_indices = df_filtered.index[df_filtered[twin_col] == "S"].tolist()
        for idx in single_indices:
            if not available_tractors.empty:
                tractor_id = available_tractors.iloc[0]["tractor_id"]
                df.loc[idx, "tractor"] = tractor_id
                tdf.loc[tdf["tractor_id"] == tractor_id, "reserved"] = "Y"
                available_tractors = available_tractors[available_tractors["tractor_id"] != tractor_id]

        logger.info(f"Assigned tractors: {df[[twin_col, 'tractor']].to_dict()}")
        df.to_csv(path, index=False)
        tdf.to_csv(tp, index=False)

    def release_print_cwp(self) -> None:
        self.actions.click(self.gt["refresh"])
        if self.properties.enabled(self.gt["release"]):
            sendkeys("%3")
        else:
            raise RuntimeError("Release button not enabled")

        if self.properties.enabled(self.gt["printCMS"]):
            sendkeys("%7")
        else:
            raise RuntimeError("Print CMS button not enabled")

        if wait_for_window("Print CMS"):
            if self.properties.text_value(self.gt["printer"]) != "DUMMY":
                self.actions.click(self.gt["printer"])
                sendkeys("DUMMY")
                sendkeys("{ENTER}")
            else:
                sendkeys("{ENTER}")
        else:
            raise RuntimeError("Print CMS window not found")

        if wait_for_window(".*gatex1305$"):
            sendkeys("{ENTER}")
        else:
            raise RuntimeError("User Information window not found")

    def handle_auth_window(self) -> None:
        sendkeys(os.getenv("USER"), with_tab=True)
        sendkeys(os.getenv("PASSWORD"))
        sendkeys("{ENTER}")

def main():
    g = GateTransaction()
    g.create_gate_pickup()

if __name__ == "__main__":
    main()