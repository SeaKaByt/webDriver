from pywinauto.keyboard import send_keys
from helper.utils import send_keys_tab
from test_ui.base_flow import BaseFlow

class HoldRelease(BaseFlow):
    module = "HR"

    def __init__(self):
        super().__init__()

        self.release_tab = self.config["hr"]["release_tab"]
        self.search_hold_condition = self.config["hr"]["search_hold_condition"]
        self.release_hold_condition = self.config["hr"]["release_hold_condition"]
        self.hr_bol = self.config["hr"]["bol"]
        self.declaration = self.config["hr"]["declaration"]
        self.select_all = self.config["hr"]["select_all"]
        self.release_batch = self.config["hr"]["release_batch"]
        self.search_tab = self.config["hr"]["search_tab"]

    def release_hold(self):
        self.search_cntr()
        self.click(self.release_hold_condition)
        send_keys('dt')
        self.click(self.declaration)
        send_keys_tab('automation')
        send_keys(self.date)
        self.click(self.select_all)
        self.click(self.release_batch)

    def search_cntr(self):
        if not self.visible(self.search_hold_condition, 1):
            self.module_view(self.module)
            self.click(self.release_tab)
            self.click(self.search_tab)
        send_keys('%r')
        self.click(self.search_hold_condition)
        send_keys('dt')
        self.click(self.hr_bol)
        send_keys(self.bol.upper())
        send_keys('%s')

if __name__ == "__main__":
    # python -m test_ui.flow.hold_release
    hr = HoldRelease()
    hr.release_hold()
