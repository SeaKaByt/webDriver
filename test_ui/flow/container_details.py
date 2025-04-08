import time

from pywinauto.keyboard import send_keys
from helper.utils import send_keys_tab, next_loc, wait_for_window, get_match_windows
from test_ui.base_flow import BaseFlow

class ContainerDetails(BaseFlow):
    module = "CD"

    def __init__(self):
        super().__init__()
        self.cd_cntr_id = self.config["cd"]["cntr_id"]
        self.cd_owner = self.config["cd"]["owner"]
        self.cd_voyage = self.config["cd"]["voyage"]
        self.cd_pol = self.config["cd"]["pol"]
        self.cd_gross_wt = self.config["cd"]["gross_wt"]
        self.cd_status = self.config["cd"]["status"]
        self.cd_yard = self.config['cd']['yard']

        self.create_yes = self.config["cd"]["create_yes_btn"]
        self.create_confirm = self.config["cd"]["create_confirm_btn"]
        self.cancel = self.config["cd"]["cancel_btn"]
        self.confirm_yes = self.config["cd"]["confirm_yes_btn"]
        self.ags4999 = self.config["cd"]["ags4999"]

    def create_cntr(self):
        if not self.visible(self.cd_cntr_id, 1):
            self.click(self.title)
            self.module_view(self.module)
        self.common_details()

    def common_details(self):
        self.click(self.cd_cntr_id)
        send_keys('^a')
        send_keys(self.cntr_id)
        send_keys('{ENTER}')
        if wait_for_window('Create Container'):
            self.click(self.create_yes)
            self.click(self.create_confirm)
        self.click(self.cd_status)
        send_keys(self.status)
        send_keys(self.size)
        send_keys(self.type)
        self.click(self.cd_owner)
        send_keys_tab(self.owner)
        send_keys('{TAB}')
        send_keys(self.block)
        send_keys_tab(self.stack)
        send_keys(self.lane)
        self.voyage_details() if self.status == 'if' else None
        send_keys('{ENTER}')

        time.sleep(0.5)
        if get_match_windows('User Error ags4999'):
            self.lane = f'{int(self.lane) + 1}'
            self.click(self.ags4999)
            self.click(self.cd_yard)
            send_keys('{TAB}')
            send_keys('{TAB}')
            send_keys(self.lane)
            send_keys('{ENTER}')

        if self.editable(self.cd_cntr_id):
            d = next_loc(self.cntr_id, self.stack, self.lane, self.get_tier(), self.json_path)
            for k, v in d.items():
                setattr(self, k, v)

        print('=== Done ===')

    def voyage_details(self):
        self.click(self.cd_voyage)
        send_keys('^a')
        send_keys_tab(self.line)
        send_keys(self.vessel)
        send_keys(self.voyage)
        self.click(self.cd_pol)
        send_keys(self.pol)
        self.click(self.cd_gross_wt)
        send_keys(self.gross_wt)

    def get_tier(self):
        v = self.text_value(self.cd_yard)
        self.tier = v.split()[-1].split('/')[-1]
        return self.tier

    def test(self):
        pass

if __name__ == '__main__':
    # python -m test_ui.flow.container_details
    cd = ContainerDetails()
    for i in range(1):
        cd.create_cntr()
    # cd.test()
