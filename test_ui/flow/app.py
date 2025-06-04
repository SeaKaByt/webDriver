import allure

from typing import Optional
from dotenv import load_dotenv
from pywinauto import Application
from helper.logger import logger
from helper.win_utils import send_keys_wlog, wait_for_window, focus_window
from test_ui.flow_config import BaseFlow

load_dotenv()

class ApplicationLauncher(BaseFlow):
    """
    Unified application launcher for nGen and Guider applications.
    Handles launching, login, and comprehensive error handling with Allure integration.
    """
    def __init__(self, external_driver=None):
        super().__init__(external_driver=external_driver, app=Application(backend="uia"))
        self.lanc = self.config["launcher"]

    @allure.step("Login to nGen section")
    def login_ngen(self) -> None:
        logger.info("Starting nGen login process")
        if not wait_for_window("nGen", timeout=1):
            self.actions.click(self.lanc["ngen"])

        if wait_for_window("Login", timeout=30):
            self.send_credentials(self.ng["username"], self.ng["password"])

        assert wait_for_window("nGen", timeout=10)

    @allure.step("Login to Guider section")
    def login_guider(self) -> None:
        logger.info("Starting Guider login process")
        focus_window("Application")

        if not wait_for_window("Guider", timeout=1):
            self.actions.click(self.lanc["guider"])

        if wait_for_window("Guider Logon", timeout=30):
            self.send_credentials(self.ng["username"], self.ng["password"])

        assert True

    @allure.step("Initiate launcher section")
    def initiate_launcher(self):
        if not wait_for_window("Application Launcher"):
            logger.info("Initiating application launcher")
            self.launch(self.ng["jal_path"])

        assert wait_for_window("Application Launcher", timeout=10)

    def close_applications(self):
        """Close applications and clean up"""
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()
            logger.info("Applications closed successfully")

    @staticmethod
    def send_credentials(username: str, password: str) -> None:
        """Send username and password to login window."""
        logger.info("Sending credentials")
        send_keys_wlog(username, field_length=99)
        send_keys_wlog(password)
        send_keys_wlog("{ENTER}")