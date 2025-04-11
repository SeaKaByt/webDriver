from main import BaseDriver
from helper.logger import logger
from helper.utils import get_match_windows, wait_for_window, send_keys_tab, window_exists, _send_keys
from pywinauto import Application
from dotenv import load_dotenv
from test_ui.win import WinAppHandler

load_dotenv()

class ApplicationLauncher(BaseDriver, WinAppHandler):
    def __init__(self):
        print("Initializing ApplicationLauncher")
        super().__init__()
        self.app = Application(backend="uia")
        WinAppHandler.__init__(self, app=self.app)
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
                self.send_credentials(self.username, self.password)
        except Exception as e:
            logger.error(f"Failed to login to {app_window}: {e}")
            raise

    def login_ngen(self):
        if not get_match_windows("nGen"):
            if not get_match_windows("Application Launcher"):
                self.launch(self.jal_path)
                wait_for_window("Application Launcher")
            self._login("nGen", "Login", self.app_ngen)

    def login_guider(self):
        self._login("Guider", "Guider Logon", self.app_guider)

    def full_load(self):
        logger.info("Starting full load")
        self.login_ngen()
        window_exists("nGen")
        self.login_guider()
        window_exists("Guider")
        logger.debug(self.app)
        self.cleanup()
        logger.debug(self.app)

    def cleanup(self):
        super().cleanup()
        if self.app:
            try:
                self.app.kill()
                logger.info("Application killed successfully")
            except Exception as e:
                logger.warning(f"Failed to kill application: {e}")
            self.app = None

if __name__ == "__main__":
    app = ApplicationLauncher()
    app.full_load()