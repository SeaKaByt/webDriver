from typing import Dict, Any, Optional
from pathlib import Path
from helper.win_utils import wait_for_window
from helper.logger import logger
from drivers.base_driver import BaseDriver
from pywinauto.keyboard import send_keys


class BaseFlow(BaseDriver):
    """Base class for UI automation flows, extending BaseDriver."""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize BaseFlow with optional config path.

        Args:
            config_path: Optional path to YAML config file.
        """
        super().__init__()  # Initialize BaseDriver
        try:
            # Load nGen config
            ngen_config = self.config.get("nGen", {})
            self.title = ngen_config.get("title")
            self.home = ngen_config.get("home_btn")
            self.inv_menu = ngen_config.get("inv_menu")
            self.sp_menu = ngen_config.get("sp_menu")
            self.ioc_menu = ngen_config.get("ioc_menu")
            self.gate_menu = ngen_config.get("gate_menu")
            self.mv_menu = ngen_config.get("mv_menu")

            # Load JSON config for container details
            self.cntr_id = self.config_j.get("cntr_id")
            self.status = self.config_j.get("status")
            self.size = self.config_j.get("size")
            self.type = self.config_j.get("type")
            self.owner = self.config_j.get("owner")
            self.block = self.config_j.get("block")
            self.stack = self.config_j.get("stack")
            self.lane = self.config_j.get("lane")
            self.material = self.config_j.get("material")
            self.max_gross_wt = self.config_j.get("max_gross_wt")
            self.line = self.config_j.get("line")
            self.vessel = self.config_j.get("vessel")
            self.voyage = self.config_j.get("voyage")
            self.pol = self.config_j.get("POL")
            self.gross_wt = self.config_j.get("gross_wt")
            self.bay = self.config_j.get("bay")
            self.row = self.config_j.get("row")
            self.tier = self.config_j.get("tier")
            self.bol = self.config_j.get("cro", {}).get("bol")

            # Other attributes
            self.cro_no = ""
            self.date = self.config_j.get("date", "01012026")  # From config or default
            self.time = self.config_j.get("time", "0000")
            self.agent = self.config_j.get("agent", "TEST")

            # Validate required configs
            required = [self.title, self.home, self.cntr_id]
            if any(x is None for x in required):
                logger.error("Missing required config keys: title, home_btn, or cntr_id")
                raise ValueError("Invalid configuration")
        except KeyError as e:
            logger.error(f"Config key error: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize BaseFlow: {e}")
            raise

    def module_view(self, module: Optional[str] = None) -> None:
        """
        Navigate to a specific UI module.

        Args:
            module: Module identifier (e.g., 'HR', 'DC', 'CRO').
        """
        try:
            logger.info(f"Navigating to module: {module or 'default'}")
            self.actions.click(self.title)
            self.actions.click(self.home)

            module_actions = {
                "HR": [
                    (self.actions.click, (self.inv_menu,)),
                    (send_keys, ("{F2}",)),
                    (send_keys, ("{F4}",))
                ],
                "DC": [
                    (self.actions.click, (self.sp_menu,)),
                    (send_keys, ("{F2}",))
                ],
                "CRO": [
                    (self.actions.click, (self.ioc_menu,)),
                    (send_keys, ("{F1}",)),
                    (send_keys, ("{F7}",))
                ],
                "BOL": [
                    (self.actions.click, (self.ioc_menu,)),
                    (send_keys, ("{F1}",)),
                    (send_keys, ("{F2}",))
                ],
                "CD": [
                    (self.actions.click, (self.inv_menu,)),
                    (send_keys, ("{F2}",)),
                    (send_keys, ("{F1}",))
                ],
                "GT": [
                    (self.actions.click, (self.gate_menu,)),
                    (send_keys, ("{F1}",)),
                    (send_keys, ("{F1}",)),
                    (self._handle_gate_terminal, ())
                ],
                "QM": [
                    (self.actions.click, (self.mv_menu,)),
                    (send_keys, ("{F3}",))
                ]
            }

            if module in module_actions:
                for action, args in module_actions[module]:
                    logger.debug(f"Executing action: {action.__name__} with args {args}")
                    action(*args)
            else:
                logger.warning(f"Unknown module: {module}")
        except Exception as e:
            logger.error(f"Failed to navigate to module {module}: {e}")
            raise

    def _handle_gate_terminal(self) -> None:
        """Handle gate terminal selection window."""
        try:
            if wait_for_window("Select Working Terminal", timeout=1):
                logger.info("Selecting working terminal")
                send_keys("{ENTER}")
        except Exception as e:
            logger.error(f"Failed to handle gate terminal: {e}")
            raise