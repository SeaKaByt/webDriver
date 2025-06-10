from typing import Dict, Any, Callable, List, Tuple
from helper.win_utils import sendkeys, focus_window, find_window
from helper.logger import logger
from helper.io_utils import read_yaml
from helper.paths import ProjectPaths
import os

class MenuConfig:
    """Simple configuration loader without driver dependencies."""
    
    _config = None
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Load and cache configuration."""
        if cls._config is None:
            cls._load_config()
        return cls._config
    
    @classmethod
    def _load_config(cls):
        """Load configuration from environment."""
        bu = os.getenv("TEST_BU")
        env = os.getenv("TEST_ENV")
        yaml_path = ProjectPaths.CONFIG / f"{env}" / f"{bu}.yaml"
        cls._config = read_yaml(yaml_path)

class MenuNavigator:
    """Clean menu navigation utility with no driver dependencies."""
    
    # Module navigation mappings - pure data, no business logic
    MODULE_ACTIONS = {
        "HR": [
            ("click", "inventory"),
            ("sendkeys", "{F2}"),
            ("sendkeys", "{F4}")
        ],
        "DC": [
            ("click", "shipPlan"),
            ("sendkeys", "{F2}")
        ],
        "CRO": [
            ("click", "IOC"),
            ("sendkeys", "{F1}"),
            ("sendkeys", "{F7}")
        ],
        "BOL": [
            ("click", "IOC"),
            ("sendkeys", "{F1}"),
            ("sendkeys", "{F2}")
        ],
        "CD": [
            ("click", "inventory"),
            ("sendkeys", "{F2}"),
            ("sendkeys", "{F1}")
        ],
        "GT": [
            ("click", "gatehouse"),
            ("sendkeys", "{F1}"),
            ("sendkeys", "{F1}"),
            ("special", "gate_terminal")
        ],
        "QM": [
            ("click", "movementControl"),
            ("sendkeys", "{F3}")
        ],
        "BM": [
            ("click", "IOC"),
            ("sendkeys", "{F1}"),
            ("sendkeys", "{F1}")
        ],
        "BP": [
            ("click", "shipPlan"),
            ("sendkeys", "{F3}")
        ],
        "VS": [
            ("click", "voyage"),
            ("sendkeys", "{F6}")
        ],
        "TC": [
            ("click", "gatehouse"),
            ("sendkeys", "{F3}"),
            ("sendkeys", "{F1}")
        ]
    }
    
    def __init__(self):
        self.config = MenuConfig.get_config()
        self.menu_elements = self.config["nGen"]["menu"]
        self.home_element = self.config["nGen"]["home"]
    
    def navigate_to_module(self, module: str, driver) -> None:
        """Navigate to specified module using provided driver."""
        logger.info(f"Navigating to module: {module}")
        
        if module not in self.MODULE_ACTIONS:
            raise ValueError(f"Unknown module: {module}. Available: {list(self.MODULE_ACTIONS.keys())}")
        
        # Always start from home
        driver.actions.click(self.home_element)
        
        # Execute module-specific actions
        actions = self.MODULE_ACTIONS[module]
        for action_type, action_value in actions:
            self._execute_action(action_type, action_value, driver)
    
    def _execute_action(self, action_type: str, action_value: str, driver) -> None:
        """Execute a single navigation action."""
        if action_type == "click":
            element_xpath = self.menu_elements[action_value]
            driver.actions.click(element_xpath)
        elif action_type == "sendkeys":
            sendkeys(action_value)
        elif action_type == "special":
            if action_value == "gate_terminal":
                self._handle_gate_terminal()
        else:
            raise ValueError(f"Unknown action type: {action_type}")
    
    @staticmethod
    def _handle_gate_terminal() -> None:
        """Handle gate terminal selection window."""
        import time
        time.sleep(0.5)
        if find_window("Select Working Terminal"):
            logger.info("Selecting working terminal")
            sendkeys("{ENTER}")

# Simple static wrapper for backward compatibility
class Menu:
    """Clean static interface for menu navigation."""
    
    _navigator = None
    
    @classmethod
    def _get_navigator(cls) -> MenuNavigator:
        """Lazy initialization of navigator."""
        if cls._navigator is None:
            cls._navigator = MenuNavigator()
        return cls._navigator
    
    @staticmethod
    def to_module(module: str, driver) -> None:
        """Navigate to the specified module."""
        navigator = Menu._get_navigator()
        navigator.navigate_to_module(module, driver)
    
    @staticmethod
    def handle_gate_terminal() -> None:
        """Handle gate terminal selection window."""
        MenuNavigator._handle_gate_terminal()
    
    @staticmethod
    def get_available_modules() -> List[str]:
        """Get list of available modules."""
        return list(MenuNavigator.MODULE_ACTIONS.keys())
    
    @staticmethod
    def get_module_actions(module: str) -> List[Tuple[str, str]]:
        """Get the action sequence for a specific module."""
        if module not in MenuNavigator.MODULE_ACTIONS:
            raise ValueError(f"Unknown module: {module}")
        return MenuNavigator.MODULE_ACTIONS[module] 