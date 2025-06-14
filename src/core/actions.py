import pyautogui
from pywinauto import mouse
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
from helper.logger import logger
from helper.win_utils import sendkeys

class ElementActions:
    def __init__(self, driver):
        self.driver = driver

    def find(self, xpath, timeout=10):
        try:
            self.driver.implicitly_wait(timeout)
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            element = self.driver.find_element(By.XPATH, xpath)
            logger.info(f"Element found: {xpath}")
            return element
        except (WebDriverException, TimeoutException) as e:
            logger.warning(f"Element not found: {xpath} after {timeout} seconds")
            return None
        finally:
            self.driver.implicitly_wait(10)  # Reset implicit wait to default

    def click(self, xpath, timeout=10):
        element = self.find(xpath, timeout)
        try:
            element.click()
            logger.info(f"Clicked on element: {xpath}")
        except Exception as e:
            raise Exception(f"Failed to click on element: {xpath} - {e}")

    def set_text(self, xpath, text, timeout=10):
        try:
            self.click(xpath, timeout)
            sendkeys(text)
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

            logger.info(f"Right clicked on element: {xpath}")
        except Exception as e:
            raise Exception(f"Failed to right-click on element: {xpath} - {e}")

    def drag_release(self, xpath, offset_x, offset_y, target_x, target_y, timeout=10):
        element = self.find(xpath, timeout)
        try:
            location = element.location

            x = location['x']
            y = location['y']

            screen_x =  int(x + offset_x)
            screen_y = int(y + offset_y)

            pyautogui.moveTo(screen_x, screen_y)
            pyautogui.mouseDown()
            pyautogui.moveTo(screen_x + target_x, screen_y + target_y, duration=1)
            pyautogui.mouseUp()

            logger.info(f"Dragged element: {xpath}")
        except Exception as e:
            logger.error(f"Failed to drag element: {xpath} - {e}")
            raise