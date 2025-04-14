import os
from helper.logger import logger

class WinAppHandler:
    def __init__(self, app=None):
        self.app = app
        logger.debug(self.app)

    def launch(self, app_path):
        logger.info(f"Launching {app_path}")
        self.app.start(app_path, timeout=5, wait_for_idle=False, work_dir=os.path.dirname(app_path))