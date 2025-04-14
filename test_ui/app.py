import sys
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv
from pywinauto import Application
from helper.logger import logger
from helper.win_utils import send_keys_with_log, wait_for_window, window_exists
from test_ui.base_flow import BaseFlow
from test_ui.win import WinAppHandler

load_dotenv()

class ApplicationLauncher(BaseFlow, WinAppHandler):
    """Launches and logs into nGen and Guider applications."""
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize ApplicationLauncher with config and pywinauto app.

        Args:
            config_path: Optional path to YAML config file.
        """
        super().__init__(config_path=config_path)  # Initialize BaseFlow
        WinAppHandler.__init__(self, app=Application(backend="uia"))  # Initialize WinAppHandler
        try:
            self.username = self.config["nGen"]["username"]
            self.password = self.config["nGen"]["password"]
            self.app_ngen = self.config["app"]["ngen"]
            self.app_guider = self.config["app"]["guider"]
            self.jal_path = self.config["nGen"]["jal_path"]
            self.ngen_login = self.config["nGen"]["ngen_login"]
            self.window_titles = self.config.get("windows", {
                "ngen": "nGen",
                "guider": "Guider",
                "launcher": "Application Launcher",
                "ngen_login": "Login",
                "guider_login": "Guider Logon"
            })
        except KeyError as e:
            logger.error(f"Missing config key: {e}")
            raise ValueError(f"Invalid config: missing {e}")

    def _login(self, app_name: str, login_window: str, app_xpath: str, login_field: Optional[str] = None) -> None:
        """
        Generic login helper for applications.

        Args:
            app_name: Name of the main application window.
            login_window: Name of the login window.
            app_xpath: XPath to launch the application.
            login_field: Optional XPath for the login field.
        """
        try:
            if not wait_for_window(self.window_titles[app_name], timeout=1):
                if not wait_for_window(self.window_titles[login_window], timeout=1):
                    logger.info(f"Launching {app_name} via {app_xpath}")
                    self.actions.click(app_xpath)
                if not wait_for_window(self.window_titles[login_window], timeout=10):
                    logger.error(f"Login window {login_window} not found")
                    raise RuntimeError(f"Failed to open {login_window}")
                if login_field:
                    logger.info(f"Clicking login field: {login_field}")
                    self.actions.click(login_field)
                self.send_credentials(self.username, self.password)
            logger.info(f"Successfully logged into {app_name}")
        except Exception as e:
            logger.error(f"Failed to login to {app_name}: {e}")
            raise

    def login_ngen(self) -> None:
        """Log into the nGen application."""
        try:
            if not wait_for_window(self.window_titles["ngen"], timeout=1):
                if not wait_for_window(self.window_titles["launcher"], timeout=1):
                    logger.info(f"Launching Application Launcher: {self.jal_path}")
                    self.launch(self.jal_path)
                    wait_for_window(self.window_titles["launcher"], timeout=10)
                self._login("ngen", "ngen_login", self.app_ngen, self.ngen_login)
        except Exception as e:
            logger.error(f"nGen login failed: {e}")
            raise

    def login_guider(self) -> None:
        """Log into the Guider application."""
        try:
            self._login("guider", "guider_login", self.app_guider)
        except Exception as e:
            logger.error(f"Guider login failed: {e}")
            raise

    def full_load(self) -> None:
        """Execute full login sequence for nGen and Guider."""
        logger.info("Starting full application load")
        try:
            self.login_ngen()
            window_exists(self.window_titles["ngen"], timeout=15)
            self.login_guider()
            window_exists(self.window_titles["guider"], timeout=15)
            logger.info("Full load completed successfully")
        except Exception as e:
            logger.error(f"Full load failed: {e}")
            raise
        finally:
            self.cleanup()

    def send_credentials(self, username: str, password: str) -> None:
        """Send username and password to login window."""
        try:
            logger.info("Sending credentials")
            send_keys_with_log(username, with_tab=True)
            send_keys_with_log(password)
            send_keys_with_log("{ENTER}")
        except Exception as e:
            logger.error(f"Failed to send credentials: {e}")
            raise

    def cleanup(self) -> None:
        """Clean up resources, including Selenium driver and pywinauto app."""
        logger.info("Cleaning up ApplicationLauncher")
        super().cleanup()  # Call BaseFlow cleanup
        if hasattr(self, "app") and self.app:
            try:
                self.app.kill()
                logger.info("Application killed successfully")
            except Exception as e:
                logger.warning(f"Failed to kill application: {e}")
            self.app = None

if __name__ == "__main__":
    try:
        app = ApplicationLauncher()
        app.full_load()
    except Exception as e:
        logger.error(f"Application failed: {e}")
        sys.exit(1)