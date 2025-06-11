from selenium.webdriver.common.by import By
from helper.logger import logger

class ElementProperties:
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
            is_editable = element.get_dom_attribute("editable") == "True"
            logger.info(f"Element editability for {xpath}: {is_editable}")
            return is_editable
        except Exception as e:
            logger.error(f"Editability check failed for {xpath}: {e}")
            return False
        finally:
            self.driver.implicitly_wait(10)  # Reset implicit wait to default

    def enabled(self, xpath: str, timeout: int = 10) -> bool:
        try:
            self.driver.implicitly_wait(timeout)
            element = self.driver.find_element(By.XPATH, xpath)
            is_enabled = element.get_dom_attribute("enabled") == "True"
            logger.info(f"Element editability for {xpath}: {is_enabled}")
            return is_enabled
        except Exception as e:
            logger.error(f"Enabled check failed for {xpath}: {e}")
            return False

    def selected(self, xpath: str, timeout: int = 10) -> bool:
        try:
            self.driver.implicitly_wait(timeout)
            element = self.driver.find_element(By.XPATH, xpath)
            is_selected = element.get_dom_attribute("selected") == "True"
            logger.info(f"Element selected state for {xpath}: {is_selected}")
            return is_selected
        except Exception as e:
            logger.error(f"Selected check failed for {xpath}: {e}")
            return False

    def get_row_index(self, xpath: str, timeout: int = 10) -> int | None:
        try:
            self.driver.implicitly_wait(timeout)
            element = self.driver.find_element(By.XPATH, xpath)
            row_index = element.get_dom_attribute("rowIndex")
            return row_index
        except Exception as e:
            return None

    def item_text(self, xpath: str, timeout: int = 10) -> str:
        self.driver.implicitly_wait(timeout)
        element = self.driver.find_element(By.XPATH, xpath)
        text = element.get_dom_attribute("selectedItemText")
        return text

    def text_value(self, xpath: str) -> str:
        element = self.driver.find_element(By.XPATH, xpath)
        text = element.text
        logger.info(f"Text value for {xpath}: {text}")
        return text