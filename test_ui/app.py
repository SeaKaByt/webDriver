import os
from main import BaseDriver
from helper.logger import logger
from helper.utils import get_match_windows, wait_for_window, send_keys_tab, window_exists, send_keys
from pywinauto import Application
from dotenv import load_dotenv

load_dotenv()

class WinAppHandler:
    def __init__(self):
        self.app = Application()

    def launch(self, app_path):
        try:
            logger.info(f"Launching {app_path}")
            self.app.start(app_path, timeout=5, wait_for_idle=False, work_dir=os.path.dirname(app_path))
        except Exception as e:
            logger.error(f"Launch failed: {e}")
            raise

    def send_credentials(self, username, password):
        send_keys_tab(username)
        send_keys(password)
        send_keys("{ENTER}")

class ApplicationLauncher(BaseDriver):
    def __init__(self):
        super().__init__()
        self.win_app = WinAppHandler()
        self.username = self.config["nGen"]["username"]
        self.password = self.config["nGen"]["password"]
        self.app_ngen = self.config["app"]["ngen"]
        self.app_guider = self.config["app"]["guider"]
        self.jal_path = self.config["nGen"]["jal_path"]

    def _login(self, app_window, login_window, app_xpath):
        """Generic login helper for nGen and Guider"""
        try:
            if not get_match_windows(app_window):
                if not get_match_windows(login_window):
                    self.actions.click(app_xpath)
                wait_for_window(login_window)
                self.win_app.send_credentials(self.username, self.password)
        except Exception as e:
            logger.error(f"Failed to login to {app_window}: {e}")
            raise

    def login_ngen(self):
        if not get_match_windows("nGen"):
            if not get_match_windows("Application Launcher"):
                self.win_app.launch(self.jal_path)
                wait_for_window("Application Launcher")
            self._login("nGen", "Logon", self.app_ngen)

    def login_guider(self):
        self._login("Guider", "Guider Logon", self.app_guider)

    def full_load(self):
        logger.info("Starting full load")
        self.login_ngen()
        window_exists("nGen")
        self.login_guider()
        window_exists("Guider")
        self.cleanup()

if __name__ == "__main__":
    app = ApplicationLauncher()
    print("Starting full load")
    app.full_load()