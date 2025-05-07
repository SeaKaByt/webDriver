from helper.sys_utils import raise_with_log
from helper.win_utils import wait_for_window, send_keys_with_log
from test_ui.base_flow import BaseFlow


class CWP(BaseFlow):
    def __init__(self):
        super().__init__()

        guider_config = self.config["guider"]
        self.title = guider_config["title"]
        self.cwp_plan_btn = guider_config["cwp_plan_btn"]
        self.cwp_voyage = guider_config["cwp_voyage"]
        self.open_module_btn = guider_config["open_module_btn"]

        cwp_config = self.config["cwp"]
        self.cwp_view = cwp_config["cwp_view"]
        self.control_menu = cwp_config["control_menu"]

    def open_cwp_plan(self):
        self.actions.click(self.title)
        self.actions.click(self.cwp_plan_btn)
        if wait_for_window("Open CWP"):
            self.actions.click(self.cwp_voyage)
            send_keys_with_log(f"{self.full_voyage}")
            send_keys_with_log("{ENTER}")
        else:
            raise_with_log("Open CWP window not found")
        self.actions.click(self.open_module_btn)

    def release_cwp(self):
        self.actions.drag_release(self.cwp_view, 0, 0, 580, 420)
        self.actions.click(self.control_menu)
        for _ in range(2):
            send_keys_with_log("{VK_DOWN}")
        send_keys_with_log("{VK_RIGHT}")
        send_keys_with_log("{VK_DOWN}")
        send_keys_with_log("{ENTER}")

        if wait_for_window(".*(Release CWP|CWP Released).*"):
            send_keys_with_log("{ENTER}")
        else:
            raise_with_log("Release CWP window not found")

if __name__ == "__main__":
    cwp = CWP()
    cwp.open_cwp_plan()
    cwp.release_cwp()
