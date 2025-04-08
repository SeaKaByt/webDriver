import sys
import time

from helper.field_utils import send_keys_tab
from helper.utils import wait_for_window
from test_ui.base_flow import BaseFlow
from pywinauto.keyboard import send_keys


class BolMaintenance(BaseFlow):
    module = "BOL"

    def __init__(self):
        super().__init__()

        self.bol_line = self.config['bol']['line']
        self.add_cntr_btn = self.config['bol']['add_cntr_btn']
        self.add_next = self.config['bol']['add_next']
        self.confirm_yes = self.config['bol']['confirm_yes']
        self.create_cntr_id = self.config['bol']['create_cntr_id']
        self.create_cancel = self.config['bol']['create_cancel']
        self.details_line = self.config['bol']['details_line']

    def search_bol(self):
        self.click(self.bol_line)
        send_keys('^a')
        send_keys_tab(self.line)
        send_keys(self.bol)
        send_keys('{ENTER}')

    def create_bol(self):
        if not self.visible(self.bol_line):
            self.module_view(self.module)
        self.search_bol()
        if wait_for_window('User Error ioc5618', 1):
            send_keys('{ENTER}')
            send_keys('%a')
            if self.editable(self.details_line) == 'True':
                send_keys_tab(self.line)
                send_keys_tab(self.bol)
                send_keys_tab('automation')
                send_keys('{TAB}')
                send_keys_tab('automation')
                send_keys('{TAB}')
                send_keys_tab('automation')
                send_keys('{TAB}')
                send_keys_tab(self.line)
                send_keys(self.vessel)
                send_keys_tab(self.voyage)
                for _ in range(3):
                    send_keys('{TAB}')
                send_keys('test')
                send_keys('{ENTER}')
            else:
                sys.exit(1)

    def add_cntr(self):
        self.click(self.add_cntr_btn)
        wait_for_window('Create Bill of lading container')

        for cntr_id in self.df['cntr_id']:
            self.click(self.create_cntr_id)
            send_keys(cntr_id)
            self.click(self.add_next)
            wait_for_window('Confirm')
            self.click(self.confirm_yes)
            time.sleep(1)

        self.click(self.create_cancel)

    def test(self):
        pass

if __name__ == "__main__":
    # python -m test_ui.flow.bol_maintenance
    bol = BolMaintenance()
    # bol.module_view()
    # bol.search_bol()
    # bol.add_cntr()
    bol.test()
    # bol.create_bol()