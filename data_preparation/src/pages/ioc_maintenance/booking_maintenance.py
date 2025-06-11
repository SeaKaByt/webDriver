import time

from helper.logger import logger
from helper.win_utils import sendkeys, wait_for_window, find_window, focus_window
from src.core.driver import BaseDriver
from helper.paths import ProjectPaths
from src.common.menu import Menu

class BookingMaintenance(BaseDriver):
    MODULE = "BM"

    def __init__(self, external_driver=None):
        super().__init__(external_driver=external_driver)
        self.bm_config = self.config["bm"]
        self.laden_return_config = self.bm_config["laden_return"]

        self.line = "NVD"
        self.booking_list = ["BK01", "BK02"]

    def add_return_cntr(self) -> None:
        focus_window("nGen")
        
        df, p = next(ProjectPaths.get_gate_ground_data())
        if not self.properties.visible(self.bm_config["principal_line"]):
            Menu.to_module(self.MODULE, self)

        # Clean and validate the DataFrame
        df["status"] = df["status"].astype(str).str.strip()
        df["size"] = df["size"].astype(str).str.strip()
        df_filtered = df[df["mvt"] != "C"]

        for status, group in df_filtered.groupby("status"):
            logger.info(f"Processing status group: {status}")
            self.actions.click(self.bm_config["principal_line"])
            sendkeys("^a")
            sendkeys(self.line, with_tab=True)
            booking_no = self.booking_list[0 if status == "XF" else 1]
            sendkeys(booking_no)
            sendkeys("{ENTER}")
            sendkeys("%b")

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
                    sendkeys("^a")
                    sendkeys(row["cntr_id"])
                    if self.properties.text_value(self.laden_return_config["new_cntr"]) != row["cntr_id"]:
                        logger.error(f"Container {row['cntr_id']} not found")
                        raise

                    self.actions.click(self.laden_return_config["add_next"])
                    if wait_for_window("User Error", 1):
                        logger.info("User Error window is found")
                        sendkeys("{ENTER}")

                self.actions.click(self.bm_config["add_next_cancel_btn"])
                self.actions.click(self.bm_config["laden_save_btn"])

                if wait_for_window("Confirm"):
                    sendkeys("{TAB}")
                    sendkeys("{ENTER}")
                else:
                    logger.error("Confirm window not found")
                    raise RuntimeError("Confirm window not found")

                if wait_for_window(".*ioc5643$", 1):
                    logger.info("ioc5643 window found")
                    sendkeys("{ENTER}")

                if find_window("User Error"):
                    logger.error("User Error window is found")
                    raise

                self.actions.click(self.bm_config["return_cntr_close"])

            self.actions.click(self.bm_config["request_record_close_btn"])

if __name__ == "__main__":
    bm = BookingMaintenance()
    if find_window("User Error"):
        print('t')
    else:
        print('f')