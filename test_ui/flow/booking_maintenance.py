import sys
from pathlib import Path
from typing import Optional
from helper.decorators import logger
from helper.win_utils import send_keys_with_log, wait_for_window
from test_ui.base_flow import BaseFlow

class BookingMaintenance(BaseFlow):
    module = "BM"

    def __init__(self, config_path: Optional[Path] = None, csv_path: Path = Path("gate_ground_data.csv")):
        super().__init__(config_path=config_path)
        try:
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
        except KeyError as e:
            logger.error(f"Config missing key: {e}")
            raise ValueError(f"Invalid config: missing {e}")

    def add_return_cntr(self) -> None:
        if not self.properties.visible(self.principal_line, timeout=1):
            self.module_view(self.module)

        grouped = self.gate_ground_df.groupby(self.gate_ground_df["status"].str.upper())

        for status, group in grouped:
            logger.info(f"Processing status: {status}")
            self.actions.click(self.principal_line)
            send_keys_with_log("^a")
            send_keys_with_log(self.line, with_tab=True)
            if status == "XF":
                send_keys_with_log(self.booking_no_list[0])
            if status == "EM":
                send_keys_with_log(self.booking_no_list[1])
            send_keys_with_log("{ENTER}")
            if wait_for_window("User Error", timeout=1):
                logger.error("User Error encountered")
                sys.exit(1)
            send_keys_with_log("%b")
            if not wait_for_window("Booking Request", timeout=5):
                logger.error("Booking Request window not found")
                sys.exit(1)
            self.actions.click(self.booking_request_record_0)
            send_keys_with_log("%r")
            if not wait_for_window("Laden", timeout=1):
                logger.error("Laden window not found")
                sys.exit(1)

            self.actions.click(self.laden_return_cntr_0)
            send_keys_with_log("%y")

            for _, row in group.iterrows():
                logger.info(f"Processing row: {row}")
                send_keys_with_log(row["cntr_id"])
                self.actions.click(self.add_next_btn)
            self.actions.click(self.add_next_cancel_btn)
            self.actions.click(self.laden_save_btn)
            if wait_for_window("Confirm", timeout=10):
                send_keys_with_log("{TAB}")
                send_keys_with_log("{ENTER}")
            else:
                logger.error("Confirm window not found")
                sys.exit(1)
            self.actions.click(self.return_cntr_close)
            self.actions.click(self.request_record_close_btn)

if __name__ ==  "__main__":
    # python -m test_ui.flow.booking_maintenance
    bm = BookingMaintenance()
    bm.add_return_cntr()

