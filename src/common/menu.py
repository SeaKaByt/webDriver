from typing import Optional
from helper.win_utils import send_keys_wlog, focus_window, find_window
from helper.logger import logger
from src.core.driver import BaseDriver

class Menu:
    """Efficient navigator class using static methods with config caching."""
    
    _config_cache = None
    _ng_cache = None
    _menu_cache = None
    
    @classmethod
    def _get_config(cls):
        """Cache and return configuration to avoid repeated loading."""
        if cls._config_cache is None:
            driver = BaseDriver()
            cls._config_cache = driver.config
            cls._menu_cache = cls._config_cache["nGen"]["menu"]
        return cls._config_cache, cls._menu_cache
    
    @classmethod
    def _get_elements(cls):
        """Get commonly used UI elements."""
        config, menu = cls._get_config()
        
        return {
            'inv': menu["inventory"],
            'sp': menu["shipPlan"],
            'ioc': menu["IOC"],
            'gate': menu["gatehouse"],
            'mc': menu["movementControl"],
            'voy': menu["voyage"]
        }
    
    @staticmethod
    def to_module(module: str) -> None:
        """Navigate to the specified module."""
        logger.info(f"Navigating to module: {module}")
        
        elements = Menu._get_elements()
        
        # Get BaseDriver actions (we need this for clicking)
        driver = BaseDriver()
        actions = driver.actions
        
        actions.click(driver.home)

        module_actions = {
            "HR": [
                (actions.click, (elements['inv'],)),
                (send_keys_wlog, ("{F2}",)),
                (send_keys_wlog, ("{F4}",))
            ],
            "DC": [
                (actions.click, (elements['sp'],)),
                (send_keys_wlog, ("{F2}",))
            ],
            "CRO": [
                (actions.click, (elements['ioc'],)),
                (send_keys_wlog, ("{F1}",)),
                (send_keys_wlog, ("{F7}",))
            ],
            "BOL": [
                (actions.click, (elements['ioc'],)),
                (send_keys_wlog, ("{F1}",)),
                (send_keys_wlog, ("{F2}",))
            ],
            "CD": [
                (actions.click, (elements['inv'],)),
                (send_keys_wlog, ("{F2}",)),
                (send_keys_wlog, ("{F1}",))
            ],
            "GT": [
                (actions.click, (elements['gate'],)),
                (send_keys_wlog, ("{F1}",)),
                (send_keys_wlog, ("{F1}",)),
                (Menu.handle_gate_terminal, ())
            ],
            "QM": [
                (actions.click, (elements['mc'],)),
                (send_keys_wlog, ("{F3}",))
            ],
            "BM": [
                (actions.click, (elements['ioc'],)),
                (send_keys_wlog, ("{F1}",)),
                (send_keys_wlog, ("{F1}",))
            ],
            "BP": [
                (actions.click, (elements['sp'],)),
                (send_keys_wlog, ("{F3}",))
            ],
            "VS": [
                (actions.click, (elements['voy'],)),
                (send_keys_wlog, ("{F6}",))
            ],
            "TC": [
                (actions.click, (elements['gate'],)),
                (send_keys_wlog, ("{F3}",),),
                (send_keys_wlog, ("{F1}",))
            ]
        }

        if module in module_actions:
            for action, args in module_actions[module]:
                logger.debug(f"Executing action: {action.__name__} with args {args}")
                action(*args)
        else:
            logger.warning(f"Unknown module: {module}")
            raise ValueError(f"Unknown module: {module}")

    @staticmethod
    def handle_gate_terminal() -> None:
        """Handle gate terminal selection window."""
        import time
        
        time.sleep(0.5)
        if find_window("Select Working Terminal"):
            logger.info("Selecting working terminal")
            send_keys_wlog("{ENTER}")


