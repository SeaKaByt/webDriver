import os
from driver.element_actions import ElementActions
from driver.element_properties import ElementProperties
from helper.io_utils import read_yaml, read_json, read_csv
from helper.logger import logger
from helper.decorators import debug_out_line
from selenium import webdriver
from selenium.webdriver.common.options import ArgOptions
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class BaseDriver:
    def __init__(self):
        self.driver = None
        self.bu = os.environ.get("TEST_BU", "AQCT")
        self.env = os.environ.get("TEST_ENV", "FAT")
        self.yaml_path = Path(f"config/{self.env}/{self.bu}.yaml")
        self.json_data_path = Path("data/data.json")
        self.config = read_yaml(self.yaml_path)
        self.config_j = read_json(self.json_data_path)
        self.url = os.environ.get("WEBDRIVER_URL", "http://127.0.0.1:7993")
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
                logger.warning(f"Failed to quit driver: {e}")
            self.driver = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()