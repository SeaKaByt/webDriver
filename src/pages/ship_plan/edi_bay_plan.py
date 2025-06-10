import time

from helper.logger import logger
from helper.win_utils import wait_for_window, sendkeys, focus_window, find_window
from src.core.driver import BaseDriver
from src.common.menu import Menu

class BayPlan(BaseDriver):
    MODULE = "BP"

    def __init__(self, external_driver=None):
        super().__init__(external_driver=external_driver)
        self.edi = self.config["EDI"]

    def upload_bay_plan(self):
        focus_window("nGen")

        if not self.properties.visible(self.edi["Inbound"]):
            Menu.to_module(self.MODULE, self)

        self.actions.click(self.edi["Inbound"])
        sendkeys("%r")
        sendkeys("%i")
        if wait_for_window("Inbound Bay Plan"):
            self.actions.click(self.edi["row"])
            sendkeys("{ENTER}")
            sendkeys("%u")
        else:
            raise RuntimeError("Inbound Bay Plan window not found")

        time.sleep(0.5)
        if find_window("User Error",):
            logger.error("User Error window appeared")
            raise