from helper.logger import logger
from helper.win_utils import wait_for_window, send_keys_wlog, focus_window
from src.pages_config import BaseFlow

class CWP(BaseFlow):
    def __init__(self, external_driver=None):
        super().__init__(external_driver=external_driver)
        gui = self.config["guider"]
        self.cwp = gui["cwp"]

        self.line = "NVD"
        self.vessel = "TSHM04"
        self.voyage = "V01"


    def open_cwp_plan(self):
        focus_window("Guider")
        self.actions.click(self.cwp["cwp_plan"])
        if wait_for_window("Open CWP"):
            self.actions.click(self.cwp["voyage"])
            send_keys_wlog(f"{self.line}-{self.vessel}-{self.voyage}")
            self.actions.click(self.cwp["open"])
            self.actions.click(self.cwp["open"])
        else:
            logger.error("Open CWP window not found")
            raise

    def release_cwp(self):
        if not wait_for_window("CWP", timeout=1):
            self.open_cwp_plan()

        focus_window("CWP")

        self.actions.click(self.cwp["refresh"])

        self.actions.click(self.cwp["row"])
        send_keys_wlog("^a")

        self.actions.click(self.cwp["control"])
        for _ in range(2):
            send_keys_wlog("{VK_DOWN}")
        send_keys_wlog("{VK_RIGHT}")
        send_keys_wlog("{VK_DOWN}")
        send_keys_wlog("{ENTER}")

        if wait_for_window(".*(Release CWP|CWP Released).*"):
            send_keys_wlog("{ENTER}")
        else:
            logger.error("Release CWP window not found")
            raise

if __name__ == "__main__":
    cwp = CWP()
