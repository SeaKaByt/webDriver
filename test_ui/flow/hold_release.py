from helper.utils import send_keys_tab, _send_keys
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
        self.actions.click(self.release_hold_condition)
        _send_keys('dt')
        self.actions.click(self.declaration)
        send_keys_tab('automation')
        _send_keys(self.date)
        self.actions.click(self.select_all)
        self.actions.click(self.release_batch)

    def search_cntr(self):
        if not self.properties.visible(self.search_hold_condition, 1):
            self.module_view(self.module)
            self.actions.click(self.release_tab)
            self.actions.click(self.search_tab)
        _send_keys('%r')
        self.actions.click(self.search_hold_condition)
        _send_keys('dt')
        self.actions.click(self.hr_bol)
        _send_keys(self.bol.upper())
        _send_keys('%s')

if __name__ == "__main__":
    # python -m test_ui.flow.hold_release
    hr = HoldRelease()
    hr.release_hold()
