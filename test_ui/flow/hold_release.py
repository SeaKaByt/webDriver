import argparse
from helper.sys_utils import raise_with_log
from test_ui.base_flow import BaseFlow
from helper.win_utils import send_keys_with_log, wait_for_window
from helper.logger import logger

class HoldRelease(BaseFlow):
    module = "HR"

    def __init__(self):
        super().__init__()
        hr_config = self.config.get("hr", {})
        self.release_tab = hr_config.get("release_tab")
        self.result_table = hr_config.get("result_table")
        self.search_hold_condition = hr_config.get("search_hold_condition")
        self.release_hold_condition = hr_config.get("release_hold_condition")
        self.hr_bol = hr_config.get("bol")
        self.declaration = hr_config.get("declaration")
        self.select_all = hr_config.get("select_all")
        self.release_batch = hr_config.get("release_batch")
        self.search_tab = hr_config.get("search_tab")
        self.hr_voyage = hr_config.get("hr_voyage")
        # Define attributes
        self.bol = hr_config.get("bol_value")
        self.hold_condition = hr_config.get("hold_condition")
        self.declaration_value = hr_config.get("declaration_value", "automation")

    def search_cntr(self, hold_condition) -> None:
        if not self.properties.visible(self.result_table):
            logger.info("Opening HR module")
            self.module_view(self.module)
            self.actions.click(self.release_tab)
            self.actions.click(self.search_tab)
        send_keys_with_log("%r")
        self.actions.click(self.search_hold_condition)
        send_keys_with_log(hold_condition)
        self.actions.click(self.hr_voyage)
        send_keys_with_log("^a")
        send_keys_with_log(self.line, with_tab=True)
        send_keys_with_log(self.vessel)
        send_keys_with_log(self.voyage)
        send_keys_with_log("%s")

    def release_hold(self, hold_condition: str, hold_condition2: str) -> None:
        logger.info(f"Releasing hold for BOL: {self.bol}")
        self.search_cntr(hold_condition)
        if wait_for_window(".*inv0693$", 1):
            logger.warning("inv0693 window found, no record found!")
            send_keys_with_log("{ENTER}")
            return
        self.actions.click(self.release_hold_condition)
        send_keys_with_log(hold_condition)
        if hold_condition2 != "None":
            send_keys_with_log(",")
            send_keys_with_log(hold_condition2)
        self.actions.click(self.declaration)
        send_keys_with_log(self.declaration_value, with_tab=True)
        send_keys_with_log(self.date)
        self.actions.click(self.select_all)
        if not wait_for_window(".*inv0799$", 1):
            # self.actions.click(self.release_batch)
            send_keys_with_log("%b")
        else:
            raise_with_log("User error: inv0799 window found")
        self.driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hold Release Automation")
    parser.add_argument("method", choices=["release_hold"], default="release_hold", help="Method to execute")
    parser.add_argument("--hc1", type=str, required=True, help="First hold condition to use (e.g., 'dt', 'cc', 'mv')", default=None)
    parser.add_argument("--hc2", type=str, default=None, help="Second hold condition")
    args = parser.parse_args()

    try:
        hr = HoldRelease()
        if args.method == "release_hold":
            hr.release_hold(hold_condition=args.hc1, hold_condition2=args.hc2)
    except Exception as e:
        raise_with_log(f"Error in HoldRelease: {e}")