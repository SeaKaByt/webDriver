from typing import Optional
from helper.win_utils import send_keys_wlog, focus_window, find_window
from helper.logger import logger
from src.core.driver import BaseDriver

class BaseFlow(BaseDriver):
    """Base class for UI automation flows, extending BaseDriver with Windows app handling."""

    def __init__(self, external_driver=None, app=None):
        super().__init__(external_driver=external_driver)  # Pass external core to BaseDriver
        self.app = app  # Store the app instance if provided
        
        # Validate configuration is loaded
        if not hasattr(self, 'config') or not self.config:
            raise RuntimeError("Configuration not loaded. Check that TEST_BU and TEST_ENV environment variables are set correctly.")
        
        # Validate nGen configuration exists
        if "nGen" not in self.config:
            raise RuntimeError(f"nGen configuration not found in config. Available keys: {list(self.config.keys())}")
        
        self.ng = self.config["nGen"]
        
        # Validate required nGen keys
        required_keys = ["menu", "title", "home", "jal_path"]
        missing_keys = [key for key in required_keys if key not in self.ng]
        if missing_keys:
            raise RuntimeError(f"Missing required nGen configuration keys: {missing_keys}")
        
        self.menu = self.ng["menu"]
        
        # Load nGen config
        self.title = self.ng["title"]
        self.home = self.ng["home"]
        self.inv = self.menu["inventory"]
        self.sp = self.menu["shipPlan"]
        self.ioc = self.menu["IOC"]
        self.gate = self.menu["gatehouse"]
        self.mc = self.menu["movementControl"]
        self.voy = self.menu["voyage"]

    def module_view(self, module: Optional[str] = None) -> None:
        logger.info(f"Navigating to module: {module or 'default'}")
        focus_window("nGen")
        self.actions.click(self.home)

        module_actions = {
            "HR": [
                (self.actions.click, (self.inv,)),
                (send_keys_wlog, ("{F2}",)),
                (send_keys_wlog, ("{F4}",))
            ],
            "DC": [
                (self.actions.click, (self.sp,)),
                (send_keys_wlog, ("{F2}",))
            ],
            "CRO": [
                (self.actions.click, (self.ioc,)),
                (send_keys_wlog, ("{F1}",)),
                (send_keys_wlog, ("{F7}",))
            ],
            "BOL": [
                (self.actions.click, (self.ioc,)),
                (send_keys_wlog, ("{F1}",)),
                (send_keys_wlog, ("{F2}",))
            ],
            "CD": [
                (self.actions.click, (self.inv,)),
                (send_keys_wlog, ("{F2}",)),
                (send_keys_wlog, ("{F1}",))
            ],
            "GT": [
                (self.actions.click, (self.gate,)),
                (send_keys_wlog, ("{F1}",)),
                (send_keys_wlog, ("{F1}",)),
                (self.handle_gate_terminal, ())
            ],
            "QM": [
                (self.actions.click, (self.mc,)),
                (send_keys_wlog, ("{F3}",))
            ],
            "BM": [
                (self.actions.click, (self.ioc,)),
                (send_keys_wlog, ("{F1}",)),
                (send_keys_wlog, ("{F1}",))
            ],
            "BP": [
                (self.actions.click, (self.sp,)),
                (send_keys_wlog, ("{F3}",))
            ],
            "VS": [
                (self.actions.click, (self.voy,)),
                (send_keys_wlog, ("{F6}",))
            ],
            "TC": [
                (self.actions.click, (self.gate,)),
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
            raise

    @staticmethod
    def handle_gate_terminal() -> None:
        import time

        time.sleep(0.5)
        if find_window("Select Working Terminal"):
            logger.info("Selecting working terminal")
            send_keys_wlog("{ENTER}")



