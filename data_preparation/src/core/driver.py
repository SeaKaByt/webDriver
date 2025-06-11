import os

from helper.paths import ProjectPaths
from src.core.actions import ElementActions
from src.core.properties import ElementProperties
from helper.io_utils import read_yaml, read_json
from helper.logger import logger
from helper.decorators import debug_out_line
from selenium import webdriver
from selenium.webdriver.common.options import ArgOptions
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class BaseDriver:
    def __init__(self, external_driver=None):
        self.driver = None
        self.bu = os.getenv("TEST_BU")
        self.env = os.getenv("TEST_ENV")
        self.url = os.getenv("WEBDRIVER_URL")

        self.yaml_path = ProjectPaths.CONFIG / f"{self.env}" / f"{self.bu}.yaml"
        self.config = read_yaml(self.yaml_path)
        
        self.home = self.config["nGen"]["home"]

        # Use external core if provided, otherwise create own core
        if external_driver:
            self.driver = external_driver
            logger.info(f"Using external core: {external_driver}")
        else:
            self.driver = self._initialize_driver()
            
        self.actions = ElementActions(self.driver)
        self.properties = ElementProperties(self.driver)

    @debug_out_line
    def _initialize_driver(self):
        default_options = {
            "browserName": "Ranorex",
            "rx:app": os.environ.get("RX_APP_PATH", "javaw.exe"),
            "rx:args": "",
            "rx:force": True,
            "rx:whitelist": ["nGen *", "Application Launcher *"],
        }
        options = ArgOptions()
        for k, v in default_options.items():
            options.set_capability(k, v)
        driver = webdriver.Remote(command_executor=self.url, options=options)
        """Set implicit wait"""
        driver.implicitly_wait(10)
        return driver

    def cleanup(self):
        if self.driver and hasattr(self.driver, 'quit'):
            try:
                self.driver.quit()
                logger.info("Driver quit successfully")
            except Exception as e:
                logger.warning(f"Failed to quit core: {e}")
            self.driver = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()