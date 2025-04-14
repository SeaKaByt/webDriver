from selenium.webdriver.common.by import By
from helper.logger import logger

class ElementProperties():
    def __init__(self, driver):
        self.driver = driver

    def visible(self, xpath: str, timeout: int = 10) -> bool:
        try:
            self.driver.implicitly_wait(timeout)
            element = self.driver.find_element(By.XPATH, xpath)
            is_visible = element.get_dom_attribute("visible") == "True"
            logger.info(f"Element visibility for {xpath}: {is_visible}")
            return is_visible
        except Exception as e:
            logger.error(f"Visibility check failed for {xpath}: {e}")
            return False
        finally:
            self.driver.implicitly_wait(10)  # Reset implicit wait to default

    def editable(self, xpath: str, timeout: int = 10) -> bool:
        try:
            self.driver.implicitly_wait(timeout)
            element = self.driver.find_element(By.XPATH, xpath)
            is_editable = element.get_dom_attribute("editable")
            logger.info(f"Element editability for {xpath}: {is_editable}")
            return is_editable
        except Exception as e:
            logger.error(f"Editability check failed for {xpath}: {e}")
            return False
        finally:
            self.driver.implicitly_wait(10)  # Reset implicit wait to default

    def text_value(self, xpath: str) -> str:
        try:
            element = self.driver.find_element(By.XPATH, xpath)
            text = element.text
            logger.info(f"Text value for {xpath}: {text}")
            return text
        except Exception as e:
            logger.error(f"Failed to get text value for {xpath}: {e}")
            return ""