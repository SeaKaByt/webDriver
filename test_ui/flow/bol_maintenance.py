import argparse
import sys
from typing import Optional
from pathlib import Path
from helper.sys_utils import raise_with_log
from test_ui.base_flow import BaseFlow
from helper.win_utils import wait_for_window, send_keys_with_log
from helper.logger import logger

class BolMaintenance(BaseFlow):
    """Handles BOL module for creating and managing bills of lading."""
    module = "BOL"

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize BolMaintenance with config and UI settings.

        Args:
            config_path: Optional path to YAML config file.
        """
        super().__init__(config_path=config_path)
        bol_config = self.config.get("bol", {})
        self.bol_line = bol_config.get("line")
        self.add_cntr_btn = bol_config.get("add_cntr_btn")
        self.add_next = bol_config.get("add_next")
        self.confirm_yes = bol_config.get("confirm_yes")
        self.create_cntr_id = bol_config.get("create_cntr_id")
        self.create_cancel = bol_config.get("create_cancel")
        self.details_line = bol_config.get("details_line")
        # Define attributes
        self.line = bol_config.get("line_value", "LINE1")
        self.bol = bol_config.get("bol_value", "BOL001")
        self.vessel = bol_config.get("vessel", "VESSEL1")
        self.voyage = bol_config.get("voyage", "VOY001")
        self.default_field = bol_config.get("default_field", "automation")
        self.test_field = bol_config.get("test_field", "test")

    def search_bol(self) -> None:
        """Search for a bill of lading."""
        try:
            logger.info(f"Searching BOL: {self.bol}")
            self.actions.click(self.bol_line)
            send_keys_with_log("^a")
            send_keys_with_log(self.line, with_tab=True)
            send_keys_with_log(self.bol)
            send_keys_with_log("{ENTER}")
        except Exception as e:
            logger.error(f"Search BOL failed: {e}")
            raise

    def create_bol(self) -> None:
        """Create a new bill of lading."""
        try:
            if not self.properties.visible(self.bol_line, timeout=1):
                logger.info("Opening BOL module")
                self.module_view(self.module)
            self.search_bol()
            if wait_for_window("User Error ioc5618", timeout=1):
                logger.info("Handling User Error ioc5618")
                send_keys_with_log("{ENTER}")
                send_keys_with_log("%a")
                if not self.properties.editable(self.details_line):
                    logger.error("details_line not editable")
                    raise RuntimeError("BOL creation failed: details_line not editable")
                send_keys_with_log(self.line, with_tab=True)
                send_keys_with_log(self.bol, with_tab=True)
                send_keys_with_log(self.default_field, with_tab=True)
                send_keys_with_log(self.default_field, with_tab=True)
                send_keys_with_log(self.default_field, with_tab=True)
                send_keys_with_log(self.line, with_tab=True)
                send_keys_with_log(self.vessel)
                send_keys_with_log(self.voyage, with_tab=True)
                for _ in range(3):
                    send_keys_with_log("{TAB}")
                send_keys_with_log(self.test_field)
                send_keys_with_log("{ENTER}")
        except Exception as e:
            logger.error(f"Create BOL failed: {e}")
            raise

    def add_cntr(self) -> None:
        path = self.gate_pickup_data_path
        df = self.gate_pickup_df

        if not self.properties.visible(self.add_cntr_btn, timeout=1):
            logger.info("Opening BOL module")
            self.module_view(self.module)
        self.search_bol()
        self.actions.click(self.add_cntr_btn)
        if not wait_for_window("Create Bill of lading container", timeout=5):
            raise_with_log("Create Bill of lading container window not found")

        df_filtered = df[df['bol'].isna() & df['cntr_id'].notna()]
        if df_filtered.empty:
            raise_with_log("No containers without BOL were found")

        for cntr_id in df["cntr_id"]:
            logger.info(f"Adding container: {cntr_id}")
            self.actions.click(self.create_cntr_id)
            send_keys_with_log(cntr_id)
            self.actions.click(self.add_next)
            if not wait_for_window("Confirm", timeout=5):
                logger.error("Confirm window not found")
                raise RuntimeError("Confirm window not found")
            self.actions.click(self.confirm_yes)
            if wait_for_window("User Error", timeout=1):
                logger.error(f"User Error for cntr_id: {cntr_id}")
                raise RuntimeError("User Error in container addition")

        self.actions.click(self.create_cancel)
        logger.info("Completed adding containers")
        df.loc[df['cntr_id'].isin(df_filtered['cntr_id']), 'bol'] = self.bol
        df.to_csv(path, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BOL Maintenance Automation")
    parser.add_argument("method", choices=["create_bol", "add_cntr"], help="Method to execute (create_bol or add_cntr)")
    args = parser.parse_args()

    try:
        bol = BolMaintenance()
        if args.method == "create_bol":
            bol.create_bol()
        elif args.method == "add_cntr":
            bol.add_cntr()
    except Exception as e:
        logger.error(f"BolMaintenance failed: {e}")
        sys.exit(1)