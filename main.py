import os
import selenium.webdriver.support.expected_conditions as EC
from helper.utils import read_yaml, read_json, read_excel
from helper.logger import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.options import ArgOptions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common import WebDriverException, TimeoutException, NoSuchElementException
from dotenv import load_dotenv

load_dotenv()

class BaseDriver:
    driver = None
    bu = os.environ.get("TEST_BU", "AQCT")
    env = os.environ.get("TEST_ENV", "FAT")
    yaml_path =  f"config/{env.lower()}/{bu}.yaml"
    json_path = "interface/container_details.json"
    data_path = "data.xlsx"

    config = read_yaml(yaml_path)
    config_j = read_json(json_path)
    df = read_excel(data_path)

    default_options = {
        "browserName": "Ranorex",
        "rx:app": r"D:\jal\java\jre-1.8.0_411\bin\javaw.exe",
        "rx:args": "",
        "rx:force": True,
        "rx:whitelist": ["nGen *", "Application Launcher *"],
    }

    def __init__(self):
        self.url = "http://127.0.0.1:7993"
        self.driver = None
        self.connect()

    def connect(self):
        if self.driver is None:
            options = ArgOptions()
            for k, v in self.default_options.items():
                options.set_capability(k, v)

            self.driver = webdriver.Remote(command_executor=self.url, options=options)
            self.driver.implicitly_wait(10)

    def wait_for_element(self, xpath,  timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
        except KeyboardInterrupt:
            print("Caught KeyboardInterrupt! Entering breakpoint...")
            # breakpoint()
        except (WebDriverException, TimeoutException) as e:
            logger.exception(f"Element not found: {xpath} after {timeout} seconds")

    def find(self, xpath,  timeout=10):
        self.wait_for_element(xpath,  timeout)
        element = self.driver.find_element(By.XPATH, xpath)
        logger.info(f"Found element on xpath: {xpath}")
        return element

    def click(self, xpath,  timeout=10):
        self.find(xpath,  timeout).click()
        logger.info(f"Clicked on element: {xpath}")

    # def continue_on_error(self, xpath, timeout=10):
    #     try:
    #         self.driver.implicitly_wait(timeout)
    #         wait = WebDriverWait(self.driver, timeout) # ignored_exceptions=[NoSuchElementException]
    #         element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    #         print(f"Found {element}")
    #         element.click()
    #     except Exception as e:
    #         print(f"Element not found: {xpath}")
    #         return False

    def visible(self, xpath, timeout=10):
        try:
            self.driver.implicitly_wait(timeout)
            element = self.driver.find_element(By.XPATH, xpath)
            element = element.get_dom_attribute("visible")
            if element == "True":
                logger.info("Element is visible")
                return True
            else:
                logger.info("Element is not visible")
                return False
        except NoSuchElementException:
            logger.info("Element not found")
            return False
        except Exception as e:
            logger.exception(f"Error occurred: {e}")
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

if __name__ == '__main__':
    driver = BaseDriver()
