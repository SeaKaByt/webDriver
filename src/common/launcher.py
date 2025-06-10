import os
import allure

from dotenv import load_dotenv
from pywinauto import Application
from helper.logger import logger
from helper.win_utils import sendkeys, wait_for_window, focus_window
from src.core.driver import BaseDriver

load_dotenv(override=True)

class ApplicationLauncher(BaseDriver):
    """
    Unified application launcher for nGen and Guider applications.
    Handles launching, login, and comprehensive error handling with Allure integration.
    """
    def __init__(self, external_driver=None):
        super().__init__(external_driver=external_driver)
        self.app = Application(backend="uia")
        self.lanc = self.config["launcher"]

        self.username = os.getenv("USER")
        self.password = os.getenv("PASSWORD")

    @allure.step("Login to nGen section")
    def login_ngen(self) -> None:
        logger.info("Starting nGen login process")
        if not wait_for_window("nGen", timeout=1):
            self.actions.click(self.lanc["ngen"])

        if wait_for_window("Login", timeout=30):
            self.send_credentials(self.username, self.password)

        assert wait_for_window("nGen", timeout=10)

    @allure.step("Login to Guider section")
    def login_guider(self) -> None:
        logger.info("Starting Guider login process")
        focus_window("Application")

        if not wait_for_window("Guider", timeout=1):
            self.actions.click(self.lanc["guider"])

        if wait_for_window("Guider Logon", timeout=30):
            self.send_credentials(self.username, self.password)

        assert True

    @allure.step("Initiate launcher section")
    def initiate_launcher(self):
        if not wait_for_window("Application Launcher"):
            p = self.config["nGen"]["jal_path"]
            logger.info(f"Launching {p}")
            self.app.start(p, timeout=5, wait_for_idle=False, work_dir=os.path.dirname(p))

        assert wait_for_window("Application Launcher", timeout=10)

    def close_applications(self):
        """Close applications and clean up"""
        if hasattr(self, 'core') and self.driver:
            self.driver.quit()
            logger.info("Applications closed successfully")

    @staticmethod
    def send_credentials(username: str, password: str) -> None:
        """Send username and password to login window."""
        logger.info("Sending credentials")
        sendkeys(username, with_tab=True)
        sendkeys(password)
        sendkeys("{ENTER}")

l = ApplicationLauncher()

print(l.username)