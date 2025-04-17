import sys
from typing import Optional
from pathlib import Path
from test_ui.base_flow import BaseFlow
from helper.win_utils import wait_for_window, send_keys_with_log
from helper.logger import logger

class QMon(BaseFlow):
    """Handles QM module for backup confirmation of tractor transactions."""
    module = "QM"

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize QMon with config and UI settings.

        Args:
            config_path: Optional path to YAML config file.
        """
        super().__init__(config_path=config_path)
        try:
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
            # Validate config
            required = [self.fcl_tab, self.row0_cntr_id, self.bk_confirm_btn]
            if any(x is None for x in required):
                logger.error("Missing QM config keys: fcl_tab, row0_cntr_id, or bk_confirm_btn")
                raise ValueError("Invalid QM configuration")
            # Validate DataFrame
            if "tractor" not in self.df.columns:
                logger.error("data.csv missing 'tractor' column")
                raise ValueError("Invalid DataFrame: missing tractor column")
        except KeyError as e:
            logger.error(f"Config missing key: {e}")
            raise ValueError(f"Invalid config: {e}")

    def search_tractor(self) -> None:
        """Navigate to QM module if FCL tab is not visible."""
        try:
            if not self.properties.visible(self.fcl_tab, timeout=1):
                logger.info("Opening QM module")
                self.module_view(self.module)
        except Exception as e:
            logger.error(f"Failed to search tractor: {e}")
            raise

    def backup_confirm(self) -> None:
        """Confirm backup for each tractor in DataFrame."""
        try:
            self.search_tractor()
            self.actions.click(self.fcl_tab)

            for _, row in self.df.interrows():
                logger.info(f"Confirming backup for tractor: {row["tractor"]}")
                self.actions.click(self.fcl_tractor)
                send_keys_with_log("^a")
                send_keys_with_log(row["tractor"])
                send_keys_with_log("{ENTER}")

                self.actions.click(self.movement_row_0)
                send_keys_with_log("{F2}")
                self.actions.click(self.bk_confirm_btn)

                if wait_for_window("Backup Confirm"):
                    send_keys_with_log("{ENTER}")
                else:
                    logger.error("Backup window not found")
                    raise RuntimeError("Backup window not found")

                self.actions.click(self.new_search)
                if wait_for_window("User Error", timeout=1):
                    logger.error("User Error detected")
                    raise RuntimeError("User Error in backup confirmation")
                if not self.properties.visible(self.fcl_tractor, timeout=2):
                    logger.error("FCL tab not found after search")
                    raise RuntimeError("FCL tab not found")
        except Exception as e:
            logger.error(f"Backup confirmation failed: {e}")
            raise

    def twin_backup_confirm(self) -> None:
        grouped = self.gate_ground_df.groupby(self.gate_ground_df["tractor"])

        if not self.properties.visible(self.fcl_tractor, timeout=1):
            self.module_view(self.module)

        self.actions.click(self.fcl_tab)
        self.actions.click(self.fcl_tractor)

        for tractor, group in grouped:
            logger.info(f"Processing tractor: {tractor}")
            send_keys_with_log(tractor)
            send_keys_with_log("{ENTER}")
            for idx, row in group.iterrows():
                logger.info(f"Processing row: {row}")

                if idx % 2 == 0:
                    self.actions.click(self.movement_row_0, 2)
                else:
                    self.actions.click(self.movement_row_1, 2)

                send_keys_with_log("{F2}")
                self.actions.click(self.bk_confirm_btn)

                if wait_for_window("Backup Confirm"):
                    send_keys_with_log("{ENTER}")
                else:
                    logger.error("Backup window not found")
                    raise RuntimeError("Backup window not found")

                if not wait_for_window("Backup Confirm"):
                    continue

            self.actions.click(self.new_search)

if __name__ == "__main__":
    # python -m test_ui.flow.queue_monitor
    try:
        qmon = QMon()
        # qmon.backup_confirm()
        qmon.twin_backup_confirm()
    except Exception as e:
        logger.error(f"QMon failed: {e}")
        sys.exit(1)