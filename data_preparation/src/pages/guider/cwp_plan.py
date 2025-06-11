from helper.logger import logger
from helper.win_utils import wait_for_window, sendkeys, focus_window
from src.core.driver import BaseDriver


class CWP(BaseDriver):
    def __init__(self, external_driver=None):
        super().__init__(external_driver=external_driver)
        self.gui = self.config["guider"]
        self.cwp = self.gui["cwp"]

        self.line = "NVD"
        self.vessel = "TSHM04"
        self.voyage = "V01"

    def open_cwp_plan(self):
        focus_window("Guider")
        
        self.actions.click(self.cwp["cwp_plan"])
        if wait_for_window("Open CWP"):
            self.actions.click(self.cwp["voyage"])
            sendkeys(f"{self.line}-{self.vessel}-{self.voyage}")
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
        sendkeys("^a")

        self.actions.click(self.cwp["control"])
        for _ in range(2):
            sendkeys("{VK_DOWN}")
        sendkeys("{VK_RIGHT}")
        sendkeys("{VK_DOWN}")
        sendkeys("{ENTER}")

        if wait_for_window(".*(Release CWP|CWP Released).*"):
            sendkeys("{ENTER}")
        else:
            logger.error("Release CWP window not found")
            raise

if __name__ == "__main__":
    cwp = CWP()
