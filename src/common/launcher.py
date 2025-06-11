import os
import allure

from dotenv import load_dotenv
from pywinauto import Application
from helper.logger import logger
from helper.win_utils import sendkeys, wait_for_window, focus_window, find_window
from src.core.driver import BaseDriver

load_dotenv(override=True)

class ApplicationLauncher(BaseDriver):
    def __init__(self, external_driver=None):
        super().__init__(external_driver=external_driver)
        self.app = Application(backend="uia")
        self.lanc = self.config["launcher"]

        self.username = os.getenv("USER")
        self.password = os.getenv("PASSWORD")

    @allure.step("nGen section")
    def login_ngen(self) -> None:
        logger.info("Starting nGen login process")
        if find_window("nGen"):
            return
        else:
            focus_window("Application Launcher")
            self.actions.click(self.lanc["ngen"])
    
        if wait_for_window("Login", timeout=30):
            self.send_credentials(self.username, self.password)

    @allure.step("Guider section")
    def login_guider(self) -> None:
        logger.info("Starting Guider login process")
        if find_window("Guider"):
            return
        else:
            focus_window("Application Launcher")
            self.actions.click(self.lanc["guider"])

        if wait_for_window("Guider Logon", timeout=30):
            self.send_credentials(self.username, self.password)

    @allure.step("Launcher section")
    def initiate_launcher(self):
        p = self.config["nGen"]["jal_path"]

        if find_window("Application Launcher"):
            return
        else:
            logger.info(f"Launching {p}")
            self.app.start(p, timeout=5, wait_for_idle=False, work_dir=os.path.dirname(p))

    @staticmethod
    def send_credentials(username: str, password: str) -> None:
        logger.info("Sending credentials")
        sendkeys(username, with_tab=True)
        sendkeys(password)
        sendkeys("{ENTER}")

if __name__ == "__main__":
    print("hello")
    logger.debug("hello")