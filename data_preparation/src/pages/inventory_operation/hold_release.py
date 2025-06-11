import logging

from src.core.driver import BaseDriver
from src.common.menu import Menu
from helper.win_utils import sendkeys, find_window, focus_window
from helper.logger import logger

class HoldRelease(BaseDriver):
    module = "HR"

    def __init__(self, external_driver=None):
        super().__init__(external_driver=external_driver)
        self.hr = self.config["hr"]
        self.tab = self.hr["tab"]
        self.rr = self.hr["release"]["release"]
        self.rs = self.hr["release"]["search"]

        self.line = "NVD"
        self.vessel = "TSHM04"
        self.voyage = "V01"
        self.declaration = "automation"
        self.date = "01012026"

    def search_cntr(self, hold_condition) -> None:
        if not self.properties.visible(self.rs["hold"], timeout=1):
            logger.info("Opening HR module")
            Menu.to_module(self.module, self)

        self.actions.click(self.tab["release"])
        self.actions.click(self.tab["search"])

        if not self.properties.selected(self.tab["search"]):
            logging.error("Search tab is not selected")
            raise

        sendkeys("%r")

        self.actions.click(self.rs["hold"])
        sendkeys(hold_condition)

        self.actions.click(self.rs["voyage"])
        sendkeys("^a")
        sendkeys(self.line, field_length=4)
        sendkeys(self.vessel, field_length=6)
        sendkeys(self.voyage)

        sendkeys("%s")

    def release_hold(self, hold_condition: str, hold_condition2: str = None) -> None:
        import time

        focus_window("nGen")

        logger.info(f"Releasing hold condition: {hold_condition}, {hold_condition2}")
        self.search_cntr(hold_condition)

        time.sleep(0.5)
        if find_window(".*inv0693$"):
            logger.warning("inv0693 window found, no record found!")
            sendkeys("{ENTER}")
            return

        if self.properties.visible(self.rr["hold"]):
            self.actions.click(self.rr["hold"])
        else:
            logger.error("Hold release condition not found in the UI")
            raise

        sendkeys(hold_condition)
        if hold_condition2 is not None:
            sendkeys(f", {hold_condition2}")

        self.actions.click(self.rr["declaration"])
        sendkeys(self.declaration, with_tab=True)
        self.actions.click(self.rr["declaration_date"])
        sendkeys(self.date)
        self.actions.click(self.hr["select_all"])
        time.sleep(0.5)
        if find_window(".*inv0799$"):
            logger.warning("inv0799 window found")
            raise
        sendkeys("%b")

    def click(self):
        self.actions.click(self.home)

def main():
    h = HoldRelease()
    h.actions.click(h.rr["declaration"])

if __name__ == "__main__":
    main()