import time

from helper.logger import logger
from helper.win_utils import wait_for_window, send_keys_wlog, focus_window, find_window
from src.pages_config import BaseFlow

class BayPlan(BaseFlow):
    def __init__(self, external_driver=None):
        super().__init__(external_driver=external_driver)
        self.edi = self.config["EDI"]

    def upload_bay_plan(self):
        focus_window("nGen")

        if not self.properties.visible(self.edi["Inbound"]):
            self.module_view("BP")

        self.actions.click(self.edi["Inbound"])
        send_keys_wlog("%r")
        send_keys_wlog("%i")
        if wait_for_window("Inbound Bay Plan"):
            self.actions.click(self.edi["row"])
            send_keys_wlog("{ENTER}")
            send_keys_wlog("%u")
        else:
            raise RuntimeError("Inbound Bay Plan window not found")

        time.sleep(0.5)
        if find_window("User Error",):
            logger.error("User Error window appeared")
            raise

if __name__ == "__main__":
    bp = BayPlan()
    bp.upload_bay_plan()


