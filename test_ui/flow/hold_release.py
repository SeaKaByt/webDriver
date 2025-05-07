import argparse
from typing import Optional
from pathlib import Path
from helper.sys_utils import raise_with_log
from test_ui.base_flow import BaseFlow
from helper.win_utils import send_keys_with_log
from helper.logger import logger

class HoldRelease(BaseFlow):
    module = "HR"

    def __init__(self, config_path: Optional[Path] = None):
        super().__init__(config_path=config_path)
        try:
            hr_config = self.config.get("hr", {})
            self.release_tab = hr_config.get("release_tab")
            self.search_hold_condition = hr_config.get("search_hold_condition")
            self.release_hold_condition = hr_config.get("release_hold_condition")
            self.hr_bol = hr_config.get("bol")
            self.declaration = hr_config.get("declaration")
            self.select_all = hr_config.get("select_all")
            self.release_batch = hr_config.get("release_batch")
            self.search_tab = hr_config.get("search_tab")
            # Define attributes
            self.bol = hr_config.get("bol_value")
            self.hold_condition = hr_config.get("hold_condition", "dt")
            self.declaration_value = hr_config.get("declaration_value", "automation")
            # Validate config
            required = [self.release_tab, self.search_hold_condition, self.release_hold_condition]
            if any(x is None for x in required):
                logger.error("Missing HR config keys")
                raise ValueError("Invalid HR configuration")
        except KeyError as e:
            logger.error(f"Config missing key: {e}")
            raise ValueError(f"Invalid config: {e}")

    def search_cntr(self) -> None:
        try:
            if not self.properties.visible(self.search_hold_condition, timeout=1):
                logger.info("Opening HR module")
                self.module_view(self.module)
                self.actions.click(self.release_tab)
                self.actions.click(self.search_tab)
            send_keys_with_log("%r")
            self.actions.click(self.search_hold_condition)
            send_keys_with_log(self.hold_condition)
            self.actions.click(self.hr_bol)
            send_keys_with_log(self.bol.upper())
            send_keys_with_log("%s")
        except Exception as e:
            logger.error(f"Search container failed: {e}")
            raise

    def release_hold(self) -> None:
        try:
            logger.info(f"Releasing hold for BOL: {self.bol}")
            self.search_cntr()
            self.actions.click(self.release_hold_condition)
            send_keys_with_log(self.hold_condition)
            self.actions.click(self.declaration)
            send_keys_with_log(self.declaration_value, with_tab=True)
            send_keys_with_log(self.date)
            self.actions.click(self.select_all)
            self.actions.click(self.release_batch)
        except Exception as e:
            raise_with_log(f"Release hold failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hold Release Automation")
    parser.add_argument("method", choices=["release_hold"], default="release_hold", help="Method to execute")
    args = parser.parse_args()

    try:
        hr = HoldRelease()
        if args.method == "release_hold":
            hr.release_hold()
    except Exception as e:
        raise_with_log(f"Error in HoldRelease: {e}")