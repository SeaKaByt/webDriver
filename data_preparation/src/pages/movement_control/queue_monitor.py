import pandas as pd

from src.core.driver import BaseDriver
from helper.win_utils import wait_for_window, sendkeys
from helper.logger import logger
from src.common.menu import Menu

class QMon(BaseDriver):
    """Handles QM module for backup confirmation of tractor transactions."""
    MODULE = "QM"

    def __init__(self, external_driver=None):
        super().__init__(external_driver=external_driver)
        qm_config = self.config.get("qm", {})
        self.fcl_tab = qm_config.get("fcl_tab")
        self.row0_cntr_id = qm_config.get("row0_cntr_id")
        self.bk_confirm_btn = qm_config.get("bk_confirm_btn")
        self.fcl_tractor = qm_config.get("fcl_tractor")
        self.new_search = qm_config.get("new_search")
        self.tab_page_1 = qm_config.get("tab_page_1")
        self.tab_page_2 = qm_config.get("tab_page_2")
        self.movement_row_0 = qm_config.get("movement_row_0")
        self.movement_row_1 = qm_config.get("movement_row_1")

    def search_tractor(self) -> None:
        """Navigate to QM module if FCL tab is not visible."""
        try:
            if not self.properties.visible(self.fcl_tab, timeout=1):
                logger.info("Opening QM module")
                Menu.to_module(self.MODULE, self)
        except Exception as e:
            logger.error(f"Failed to search tractor: {e}")
            raise

    def backup_confirm(self, df: pd.DataFrame) -> None:
        """Confirm backup for each tractor in DataFrame."""
        # Validate DataFrame
        if "tractor" not in df.columns:
            logger.error("gate_pickup_data.csv missing 'tractor' column")
            raise ValueError("Invalid DataFrame: missing tractor column")

        try:
            # Ensure FCL tab is visible
            if not self.properties.visible(self.fcl_tractor, timeout=1):
                Menu.to_module(self.MODULE, self)

            # Group DataFrame by tractor
            grouped = df.groupby(df["tractor"])
            for tractor, group in grouped:
                logger.info(f"Processing tractor: {tractor}")
                # Search for tractor
                self.actions.click(self.fcl_tab)
                if not self.properties.visible(self.fcl_tractor, timeout=1):
                    logger.error("FCL tab not found after search")
                    raise RuntimeError("FCL tab not found")
                self.actions.click(self.fcl_tractor)
                sendkeys("^a")
                sendkeys(str(tractor))
                sendkeys("{ENTER}")

                # Process each row in the group based on group size
                group_size = len(group)
                for idx, row in enumerate(group.itertuples(), start=0):
                    logger.info(f"Processing row {idx} for tractor {tractor}")
                    if group_size == 1:
                        # Single scenario: click movement_row_0 once
                        self.actions.click(self.movement_row_0)
                    elif group_size == 2:
                        # Twin scenario: click movement rows
                        if idx == 0:
                            self.actions.click(self.movement_row_0)
                        elif idx == 1:
                            self.actions.click(self.movement_row_1)
                        else:
                            logger.error(f"Unexpected group size {group_size} for tractor {tractor}")
                            raise ValueError("Group size should be 1 or 2")

                    # Perform confirmation steps
                    sendkeys("{F2}")
                    self.actions.click(self.bk_confirm_btn)

                    # Handle a Backup Confirm window
                    if wait_for_window("Backup Confirm"):
                        sendkeys("{ENTER}")
                    else:
                        logger.error("Backup window not found")
                        raise RuntimeError("Backup window not found")

                # Reset search after processing the group
                self.actions.click(self.new_search)
                if wait_for_window("User Error", timeout=1):
                    logger.error("User Error detected")
                    raise RuntimeError("User Error in backup confirmation")

        except Exception as e:
            logger.error(f"Backup confirmation failed: {e}")
            raise