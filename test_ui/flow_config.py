import os
from typing import Dict, Any, Optional
from pathlib import Path

from helper.io_utils import read_csv
from helper.win_utils import wait_for_window, send_keys_wlog, focus_window
from helper.logger import logger
from driver.base_driver import BaseDriver
from pywinauto.keyboard import send_keys


class BaseFlow(BaseDriver):
    """Base class for UI automation flows, extending BaseDriver with Windows app handling."""

    def __init__(self, external_driver=None, app=None):
        super().__init__(external_driver=external_driver)  # Pass external driver to BaseDriver
        self.ng = self.config["nGen"]
        self.menu = self.ng["menu"]
        
        # Windows app handling (formerly WinAppHandler functionality)
        self.app = app
        if self.app:
            logger.debug(f"Initialized with app: {self.app}")
        
        # Load nGen config
        self.title = self.ng["title"]
        self.home = self.ng["home"]
        self.inv = self.menu["inventory"]
        self.sp = self.menu["shipPlan"]
        self.ioc = self.menu["IOC"]
        self.gate = self.menu["gatehouse"]
        self.mc = self.menu["movementControl"]
        self.mVoy = self.menu["voyage"]

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
        self.voy = self.config_j.get("voyage")
        self.pol = self.config_j.get("POL")
        self.gross_wt = self.config_j.get("gross_wt")
        self.bay = self.config_j.get("bay")
        self.row = self.config_j.get("row")
        self.tier = self.config_j.get("tier")
        self.bol = self.config_j.get("bol")
        self.blk = self.config_j.get("blk")

        # For gate grounding
        self.booking_no = self.config.get("bm", "booking_no")

        # Other attributes
        self.cro_no = ""
        self.date = self.config_j.get("date", "01012026")  # From config or default
        self.time = self.config_j.get("time", "0000")
        self.agent = self.config_j.get("agent", "TEST")
        self.seal_ind = "y"
        self.oog_ind = "n"
        self.full_voyage = "NVD-TSHM04-V01"
        self.qc = "OQ1"

    def launch(self, app_path):
        """Launch a Windows application (formerly WinAppHandler functionality)."""
        if not self.app:
            logger.error("No app instance available for launching")
            raise RuntimeError("App instance not initialized")
        
        logger.info(f"Launching {app_path}")
        self.app.start(app_path, timeout=5, wait_for_idle=False, work_dir=os.path.dirname(app_path))

    def module_view(self, module: Optional[str] = None) -> None:
        try:
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
                    (self.actions.click, (self.mVoy,)),
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
        except Exception as e:
            logger.error(f"Failed to navigate to module {module}: {e}")
            raise

    @staticmethod
    def handle_gate_terminal() -> None:
        """Handle gate terminal selection window."""
        try:
            if wait_for_window("Select Working Terminal", timeout=1):
                logger.info("Selecting working terminal")
                send_keys_wlog("{ENTER}")
        except Exception as e:
            logger.error(f"Failed to handle gate terminal: {e}")
            raise

    @staticmethod
    def get_loading_data():
        p = Path("data/container_data.csv")
        df = read_csv(p)
        yield df, p

    @staticmethod
    def get_discharge_data():
        p = Path("data/vessel_discharge_data.csv")
        df = read_csv(p)
        yield df, p
        
    @staticmethod
    def get_gate_pickup_data():
        p = Path("data/gate_pickup_data.csv")
        df = read_csv(p)
        yield df, p

    @staticmethod
    def get_gate_ground_data():
        p = Path("data/gate_ground_data.csv")
        df = read_csv(p)
        yield df, p

    @staticmethod
    def update_column(df, cntr_id, column: str, value) -> None:
        mask = df["cntr_id"] == cntr_id
        if mask.any():
            df.loc[mask, column] = value
            logger.info(f"Updated {column} for {cntr_id} to {value}")
        else:
            raise Exception(f"Cannot update {column} for {cntr_id}")