import sys
from typing import Optional
from pathlib import Path
from datetime import datetime

from numpy.ma.core import default_filler

from helper.logger import logger
from helper.sys_utils import raise_with_log
from helper.win_utils import wait_for_window, send_keys_with_log
from test_ui.base_flow import BaseFlow

class CROMaintenance(BaseFlow):
    module = "CRO"
    pin_list = []
    cro_no_list = []

    def __init__(self):
        super().__init__()
        cro_config = self.config.get("cro", {})
        self.reset = cro_config.get("reset")
        self.create = cro_config.get("create")
        self.cro_cntr_id = cro_config.get("cro_cntr_id")
        self.cro_cro_no = cro_config.get("cro_cro_no")
        self.create_cntr_id = cro_config.get("create_cntr_id")
        self.cro_status = cro_config.get("cro_status")
        self.row0_pin = cro_config.get("row0_pin")

    def create_cro(self) -> None:
        path = self.gate_pickup_data_path
        df = self.gate_pickup_df
        self.cro_no_list = []

        try:
            if not self.properties.visible(self.cro_cntr_id, timeout=1):
                logger.info("Opening CRO module")
                self.module_view(self.module)
            if not self.properties.visible(self.create_cntr_id, timeout=1):
                logger.info("Resetting CRO form")
                self.actions.click(self.reset)

            df_filtered = df[df["pin"].isna() & df["cntr_id"].notna()]
            if df_filtered.empty:
                raise_with_log("No containers available for CRO creation")

            for cntr_id in df_filtered["cntr_id"]:
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

            df_filtered["cro_no"] = self.cro_no_list
            df_filtered.to_csv(path, index=False)
        except Exception as e:
            logger.error(f"CRO creation failed: {e}")
            raise

    def generate_cro(self) -> None:
        try:
            now = datetime.now()
            self.cro_no = now.strftime("%d%m%H%M%S")
            logger.debug(f"Generated CRO number: {self.cro_no}")
        except Exception as e:
            raise_with_log(f"Failed to generate CRO number: {e}")

    def get_pin(self) -> None:
        self.pin_list = []
        df = self.gate_pickup_df
        path = self.gate_pickup_data_path

        df_filtered = df[df["pin"].isna() & df["cntr_id"].notna()]
        if df_filtered.empty:
            raise_with_log("No containers available for PIN retrieval")

        try:
            logger.info("Fetching pins for CRO")
            self.actions.click(self.reset)
            self.actions.click(self.cro_status)
            send_keys_with_log("active")
            for cntr_id in df_filtered["cntr_id"]:
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

            df_filtered["pin"] = self.pin_list
            df_filtered.to_csv(path, index=False)
        except Exception as e:
            raise_with_log(f"Get pin failed: {e}")

if __name__ == "__main__":
    try:
        cro = CROMaintenance()
        cro.create_cro()
        cro.get_pin()
    except Exception as e:
        raise_with_log(f"CROMaintenance failed: {e}")