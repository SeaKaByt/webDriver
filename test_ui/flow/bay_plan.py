from helper.logger import logger
from helper.sys_utils import raise_with_log
from helper.win_utils import wait_for_window, send_keys_wlog
from test_ui.flow_config import BaseFlow


class BayPlan(BaseFlow):
    def __init__(self, external_driver=None):
        super().__init__(external_driver=external_driver)

        bay_plan_config = self.config["bay_plan"]
        self.bp_voyage = bay_plan_config["bp_voyage"]
        self.bp_table_row_0 = bay_plan_config["bp_table_row_0"]


    def upload_bay_plan(self):
        if not self.properties.visible(self.bp_voyage):
            self.module_view("BP")
        send_keys_wlog("%r")
        send_keys_wlog("%i")
        if wait_for_window("Inbound Bay Plan", 30):
            self.actions.click(self.bp_table_row_0)
            send_keys_wlog("{ENTER}")
            send_keys_wlog("%u")
        else:
            raise RuntimeError("Inbound Bay Plan window not found")

        if wait_for_window("User Error"):
            logger.error("User Error window appeared")
            raise


if __name__ == "__main__":
    bp = BayPlan()
    bp.upload_bay_plan()


