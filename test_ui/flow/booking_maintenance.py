import sys
import time
from pathlib import Path
from typing import Optional
from helper.logger import logger
from helper.win_utils import send_keys_with_log, wait_for_window
from test_ui.base_flow import BaseFlow

class BookingMaintenance(BaseFlow):
    module = "BM"

    def __init__(self):
        super().__init__()
        self.bm_config = self.config["bm"]
        self.laden_return_config = self.bm_config["laden_return"]

    def add_return_cntr(self) -> None:
        df, p = next(self.get_gate_ground_data())
        if not self.properties.visible(self.bm_config["principal_line"]):
            self.module_view(self.module)

        # Clean and validate the DataFrame
        df["status"] = df["status"].astype(str).str.strip()
        df["size"] = df["size"].astype(str).str.strip()
        df_filtered = df[df["mvt"] != "C"]

        for status, group in df_filtered.groupby("status"):
            logger.info(f"Processing status group: {status}")
            self.actions.click(self.bm_config["principal_line"])
            send_keys_with_log("^a")
            send_keys_with_log(self.line, with_tab=True)
            booking_no = self.bm_config["booking_no_list"][0 if status == "XF" else 1]
            send_keys_with_log(booking_no)
            send_keys_with_log("{ENTER}")
            send_keys_with_log("%b")

            if not wait_for_window("Booking Request"):
                logger.error("Booking Request window not found")
                raise RuntimeError("Booking Request window not found")

            for size, subgroup in group.groupby("size"):
                logger.info(f"Processing Status: {status}, Size: {size}, Subgroup size: {len(subgroup)}")
                sequence_map = {
                    ("XF", "20"): self.bm_config["request_sequence_2822"],
                    ("XF", "40"): self.bm_config["request_sequence_2862"],
                    ("EM", "20"): self.bm_config["request_sequence_2843"],
                    ("EM", "40"): self.bm_config["request_sequence_2882"],
                }
                request_sequence = sequence_map.get((status, size))
                if request_sequence is None:
                    raise ValueError(f"Invalid status/size combination: {status}/{size}")

                self.actions.click(request_sequence)
                self.actions.click(request_sequence)
                if not self.properties.selected(request_sequence):
                    raise RuntimeError(f"Failed to select request_sequence for status: {status}, size: {size}")

                self.actions.click(self.bm_config["return_cntr"])
                if not wait_for_window("Laden Return"):
                    logger.error("Laden window not found")
                    raise RuntimeError("Laden window not found")

                self.actions.click(self.bm_config["laden_return_cntr_0"])
                self.actions.click(self.laden_return_config["copy"])

                for _, row in subgroup.iterrows():
                    logger.info(f"Processing row: {row}")
                    self.actions.click(self.laden_return_config["new_cntr"])
                    send_keys_with_log("^a")
                    send_keys_with_log(row["cntr_id"])
                    self.actions.click(self.laden_return_config["add_next"])
                    if wait_for_window(".*ioc2617$", 1):
                        logger.info("ioc2617 window found")
                        send_keys_with_log("{ENTER}")

                self.actions.click(self.bm_config["add_next_cancel_btn"])
                self.actions.click(self.bm_config["laden_save_btn"])
                if wait_for_window("Confirm"):
                    send_keys_with_log("{TAB}")
                    send_keys_with_log("{ENTER}")
                else:
                    logger.error("Confirm window not found")
                    raise RuntimeError("Confirm window not found")
                if wait_for_window(".*ioc5643$", 1):
                    logger.info("ioc5643 window found")
                    send_keys_with_log("{ENTER}")
                self.actions.click(self.bm_config["return_cntr_close"])

            self.actions.click(self.bm_config["request_record_close_btn"])

if __name__ == "__main__":
    bm = BookingMaintenance()
    bm.add_return_cntr()