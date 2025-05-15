import sys
import time
from pathlib import Path
from typing import Optional
from helper.decorators import logger
from helper.win_utils import send_keys_with_log, wait_for_window
from test_ui.base_flow import BaseFlow

class BookingMaintenance(BaseFlow):
    module = "BM"

    def __init__(self, config_path: Optional[Path] = None, csv_path: Path = Path("gate_ground_data.csv")):
        super().__init__(config_path=config_path)
        bm_config = self.config.get("bm", {})
        self.booking_no_list = bm_config.get("booking_no_list")
        self.booking_record_0 = bm_config.get("booking_record_0")
        self.booking_request_record_0 = bm_config.get("booking_request_record_0")
        self.return_cntr_close = bm_config.get("return_cntr_close")
        self.return_details_close = bm_config.get("return_details_close")
        self.principal_line = bm_config.get("principal_line")
        self.laden_title = bm_config.get("laden_title")
        self.laden_return_cntr_0 = bm_config.get("laden_return_cntr_0")
        self.laden_return_warning = bm_config.get("laden_return_warning")
        self.add_next_cancel_btn = bm_config.get("add_next_cancel_btn")
        self.add_next_btn = bm_config.get("add_next_btn")
        self.request_record_close_btn = bm_config.get("request_record_close_btn")
        self.laden_save_btn = bm_config.get("laden_save_btn")
        self.request_sequence_2862 = bm_config.get("request_sequence_2862")
        self.request_sequence_2822 = bm_config.get("request_sequence_2822")
        self.request_sequence_2843 = bm_config.get("request_sequence_2843")
        self.request_sequence_2882 = bm_config.get("request_sequence_2882")

    def add_return_cntr(self) -> None:
        if not self.properties.visible(self.principal_line):
            self.module_view(self.module)

        # Clean and validate the DataFrame
        self.gate_ground_df["status"] = self.gate_ground_df["status"].astype(str).str.strip()
        self.gate_ground_df["size"] = self.gate_ground_df["size"].astype(str).str.strip()
        grouped = self.gate_ground_df.groupby("status")

        for status, group in grouped:
            logger.info(f"Processing status group: {status}")
            self.actions.click(self.principal_line)
            send_keys_with_log("^a")
            send_keys_with_log(self.line, with_tab=True)
            if status == "XF":
                send_keys_with_log(self.booking_no_list[0])
            elif status == "EM":
                send_keys_with_log(self.booking_no_list[1])
            else:
                logger.warning(f"Unknown status: {status}")
            send_keys_with_log("{ENTER}")
            send_keys_with_log("%b")

            if wait_for_window("Booking Request"):
                logger.info("Booking Request window found")
            else:
                logger.error("Booking Request window not found")
                raise RuntimeError

            size_grouped = group.groupby("size")
            logger.info(f"Size groups for status {status}: {list(size_grouped.groups.keys())}")

            # Group the current status group by size
            for size, subgroup in size_grouped:
                logger.info(f"Processing Status: {status}, Size: {size}, Subgroup size: {len(subgroup)}")

                if status == "XF":
                    logger.info("Status is XF, checking size")
                    if size == "20":
                        self.actions.click(self.request_sequence_2822)
                    elif size == "40":
                        self.actions.click(self.request_sequence_2862)
                elif status == "EM":
                    logger.info("Status is EM, checking size")
                    if size == "20":
                        self.actions.click(self.request_sequence_2843)
                    elif size == "40":
                        self.actions.click(self.request_sequence_2882)

                time.sleep(1)
                send_keys_with_log("%r")
                if wait_for_window("Laden Return"):
                    logger.info("Laden window found")
                    self.actions.click(self.laden_return_cntr_0)
                    send_keys_with_log("%y")
                else:
                    logger.error("Laden window not found")
                    raise RuntimeError

                for _, row in subgroup.iterrows():
                    logger.info(f"Processing row: {row}")
                    send_keys_with_log(row["cntr_id"])
                    self.actions.click(self.add_next_btn)
                    if wait_for_window(".*ioc2617$", 1):
                        logger.info("ioc2617 window found")
                        send_keys_with_log("{ENTER}")

                self.actions.click(self.add_next_cancel_btn)
                self.actions.click(self.laden_save_btn)
                if wait_for_window("Confirm"):
                    send_keys_with_log("{TAB}")
                    send_keys_with_log("{ENTER}")
                else:
                    logger.error("Confirm window not found")
                    raise RuntimeError
                self.actions.click(self.return_cntr_close)

            # Close the Booking Request window for the current status
            self.actions.click(self.request_record_close_btn)

if __name__ ==  "__main__":
    # python -m test_ui.flow.booking_maintenance
    bm = BookingMaintenance()
    bm.add_return_cntr()
