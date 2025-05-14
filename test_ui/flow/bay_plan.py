from helper.sys_utils import raise_with_log
from helper.win_utils import wait_for_window, send_keys_with_log
from test_ui.base_flow import BaseFlow


class BayPlan(BaseFlow):
    def __init__(self):
        super().__init__()

        bay_plan_config = self.config["bay_plan"]
        self.bp_voyage = bay_plan_config["bp_voyage"]
        self.bp_table_row_0 = bay_plan_config["bp_table_row_0"]


    def upload_bay_plan(self):
        if not self.properties.visible(self.bp_voyage):
            self.module_view("BP")
        send_keys_with_log("%r")
        send_keys_with_log("%i")
        if wait_for_window("Inbound Bay Plan", 30):
            self.actions.click(self.bp_table_row_0)
            send_keys_with_log("{ENTER}")
            send_keys_with_log("%u")
        else:
            raise_with_log("Inbound Bay Plan window not found")

if __name__ == "__main__":
    bp = BayPlan()
    bp.upload_bay_plan()


