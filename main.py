import os
import selenium.webdriver.support.expected_conditions as EC
from helper.utils import read_yaml, read_json, read_excel
from helper.logger import logger
from helper.decorators import debug_out_line
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.options import ArgOptions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common import WebDriverException, TimeoutException
from dotenv import load_dotenv

load_dotenv()

class BaseDriver:
    def __init__(self):
        self.driver = None
        self.app = None
        self.bu = os.environ.get("TEST_BU", "AQCT")
        self.env = os.environ.get("TEST_ENV", "FAT")
        self.yaml_path = f"config/{self.env.lower()}/{self.bu}.yaml"
        self.json_path = "interface/container_details.json"
        self.data_path = "data.xlsx"
        self.config = read_yaml(self.yaml_path)
        self.config_j = read_json(self.json_path)
        self.df = read_excel(self.data_path)
        self.default_options = {
            "browserName": "Ranorex",
            "rx:app": r"D:\jal\java\jre-1.8.0_411\bin\javaw.exe",
            "rx:args": "",
            "rx:force": True,
            "rx:whitelist": ["nGen *", "Application Launcher *"],
        }
        self.url = "http://127.0.0.1:7993"
        self.driver = self._initialize_driver()
        self.actions = ElementActions(self.driver)
        self.properties = ElementProperties(self.driver)

    @debug_out_line
    def _initialize_driver(self):
            options = ArgOptions()
            for k, v in self.default_options.items():
                options.set_capability(k, v)
            driver = webdriver.Remote(command_executor=self.url, options=options)
            # Set implicit wait
            driver.implicitly_wait(10)
            return driver

    def cleanup(self):
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Driver quit successfully")
            except Exception as e:
                logger.warning(f"Failed to quit driver: {e}")
            self.driver = None

class ElementActions:
    def __init__(self, driver):
        self.driver = driver

    def find(self, xpath,  timeout=10):
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            return self.driver.find_element(By.XPATH, xpath)
        except (WebDriverException, TimeoutException) as e:
            logger.exception(f"Element not found: {xpath} after {timeout} seconds")
            raise

    def click(self, xpath,  timeout=10):
        self.find(xpath, timeout).click()
        logger.info(f"Clicked on element: {xpath}")

class ElementProperties():
    def __init__(self, driver):
        self.driver = driver

    def visible(self, xpath, timeout=10):
        try:
            self.driver.implicitly_wait(timeout)
            element = self.driver.find_element(By.XPATH, xpath)
            return element.get_dom_attribute("visible") == "True"
        except Exception as e:
            logger.exception(f"Visibility check failed for {xpath}: {e}")
            return False

    def editable(self, xpath, timeout=10):
        self.driver.implicitly_wait(timeout)
        element = self.driver.find_element(By.XPATH, xpath)
        logger.info("Checking if element is editable")
        return element.get_dom_attribute("editable")

    def text_value(self, xpath):
        element = self.driver.find_element(By.XPATH, xpath)
        logger.info("Getting text value of element")
        return element.text