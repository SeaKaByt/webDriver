import os
from helper.logger import logger
from helper.utils import send_keys_tab, _send_keys

class WinAppHandler:
    def __init__(self, app=None):
        self.app = app
        logger.debug(self.app)

    def launch(self, app_path):
        logger.info(f"Launching {app_path}")
        self.app.start(app_path, timeout=5, wait_for_idle=False, work_dir=os.path.dirname(app_path))

    def send_credentials(self, username, password):
        send_keys_tab(username)
        _send_keys(password)
        _send_keys("{ENTER}")