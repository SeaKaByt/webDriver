import sys
import argparse
import pandas as pd
from test_ui.base_flow import BaseFlow
from helper.utils import send_keys_tab, next_loc, wait_for_window, _send_keys

class ContainerDetails(BaseFlow):
    module = "CD"
    cntr_list = []
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

    def create_cntr(self, count):
        if not self.properties.visible(self.cd_cntr_id, 1):
            self.module_view(self.module)
        for i in range(count):
            self.common_details()
        self.save_as_excel()

    def common_details(self):
        self.cntr_list.append(self.cntr_id)
        self.actions.click(self.cd_cntr_id)
        _send_keys('^a')
        _send_keys(self.cntr_id)
        _send_keys('{ENTER}')
        if wait_for_window('Create Container', 5):
            self.actions.click(self.create_yes)
            self.actions.click(self.create_confirm)
        else:
            sys.exit(1)
        self.actions.click(self.cd_status)
        _send_keys(self.status)
        _send_keys(self.size)
        _send_keys(self.type)
        self.actions.click(self.cd_owner)
        send_keys_tab(self.owner)
        _send_keys('{TAB}')
        _send_keys(self.block)
        send_keys_tab(self.stack)
        _send_keys(self.lane)
        self.voyage_details() if self.status == 'if' else None
        _send_keys('{ENTER}')

        if wait_for_window('User Error ags4999', 1):
            self.lane = f'{int(self.lane) + 1}'
            self.actions.click(self.ags4999)
            self.actions.click(self.cd_yard)
            _send_keys('{TAB}')
            _send_keys('{TAB}')
            _send_keys(self.lane)
            _send_keys('{ENTER}')

        if self.properties.editable(self.cd_cntr_id):
            d = next_loc(self.cntr_id, self.stack, self.lane, self.get_tier(), self.json_path)
            for k, v in d.items():
                setattr(self, k, v)
        else:
            sys.exit(1)

    def voyage_details(self):
        self.actions.click(self.cd_voyage)
        _send_keys('^a')
        send_keys_tab(self.line)
        _send_keys(self.vessel)
        _send_keys(self.voyage)
        self.actions.click(self.cd_pol)
        _send_keys(self.pol)
        self.actions.click(self.cd_gross_wt)
        _send_keys(self.gross_wt)

    def get_tier(self):
        v = self.properties.text_value(self.cd_yard)
        self.tier = v.split()[-1].split('/')[-1]
        return self.tier

    def save_as_excel(self):
        data = pd.DataFrame({"cntr_id": self.cntr_list[::-1]})
        self.df = pd.concat([data, self.df])
        self.df.to_excel(self.data_path, index=False)

    def test(self):
        pass

if __name__ == '__main__':
    # python -m test_ui.flow.container_details
    parser = argparse.ArgumentParser(description='Create containers')
    parser.add_argument("count", type=int, nargs="?", default=None, help="Number of containers to create")
    parser.add_argument("--test", action="store_true", help="Run test code")
    args = parser.parse_args()

    cd = ContainerDetails()
    if args.test:
        cd.test()
    elif args.count is not None:
        cd.create_cntr(args.count)
