from pywinauto import mouse
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
from helper.logger import logger
from helper.sys_utils import raise_with_log
from helper.win_utils import send_keys_with_log

class ElementActions:
    def __init__(self, driver):
        self.driver = driver

    def find(self, xpath, timeout=10):
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            element = self.driver.find_element(By.XPATH, xpath)
            logger.info(f"Element found: {xpath}")
            return element
        except (WebDriverException, TimeoutException) as e:
            logger.error(f"Element not found: {xpath} after {timeout} seconds")
            raise

    def click(self, xpath, timeout=10):
        element = self.find(xpath, timeout)
        try:
            element.click()
            logger.info(f"Clicked on element: {xpath}")
        except Exception as e:
            logger.error(f"Failed to click on element: {xpath} - {e}")
            raise

    def set_text(self, xpath, text, timeout=10):
        try:
            self.click(xpath, timeout)
            send_keys_with_log(text)
        except Exception as e:
            logger.error(f"Failed to set text for element: {xpath} - {e}")
            raise

    def right_click(self, xpath, timeout=10):
        element = self.find(xpath, timeout)
        try:
            location = element.location
            x = location['x']
            y = location['y']

            screen_x =  int(x+10)
            screen_y = int(y+10)

            mouse.right_click(coords=(screen_x, screen_y))

            logger.info(f"Context clicked on element: {xpath}")
        except Exception as e:
            raise_with_log(f"Failed to right-click on element: {xpath} - {e}")