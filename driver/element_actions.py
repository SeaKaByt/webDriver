import pyautogui
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
from helper.logger import logger

class ElementActions:
    def __init__(self, driver):
        self.driver = driver

    def find(self, xpath,  option=None, timeout=10):
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            element = self.driver.find_element(By.XPATH, xpath)
            logger.info(f"Element found: {xpath}")
            return element
        except (WebDriverException, TimeoutException) as e:
            logger.error(f"Element not found: {xpath} after {timeout} seconds")
            raise

    def click(self, xpath,  option=None, timeout=10):
        element = self.find(xpath, option, timeout)
        try:
            element.click()
            logger.info(f"Clicked on element: {xpath}")
        except Exception as e:
            logger.error(f"Failed to click on element: {xpath} - {e}")
            raise