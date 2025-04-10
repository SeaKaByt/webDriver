import sys
import time
from test_ui.base_flow import BaseFlow
from helper.utils import wait_for_window
from pywinauto.keyboard import send_keys
from helper.logger import logger

class QMon(BaseFlow):
    module = 'QM'

    def __init__(self):
        super().__init__()

        self.fcl_tab = self.config['qm']['fcl_tab']
        self.row0_cntr_id = self.config['qm']['row0_cntr_id']
        self.bk_confirm_btn = self.config['qm']['bk_confirm_btn']
        self.fcl_tractor = self.config['qm']['fcl_tractor']
        self.new_search = self.config['qm']['new_search']

    def search_tractor(self):
        if not self.visible(self.fcl_tab, 1):
            self.module_view(self.module)

    def backup_confirm(self):
        self.search_tractor()
        self.click(self.fcl_tab)
        for tractor in self.df['tractor']:
            self.click(self.fcl_tractor)
            send_keys(tractor)
            send_keys('{ENTER}')
            self.click(self.row0_cntr_id)
            send_keys('{F2}')
            self.click(self.bk_confirm_btn)
            wait_for_window('Backup')
            send_keys('{ENTER}')
            time.sleep(1)
            self.click(self.new_search)
            if wait_for_window('User Error', 1):
                sys.exit(1)
            if not self.visible(self.fcl_tractor):
                sys.exit(1)

    def test(self):
        for tractor in self.df['tractor']:
            print(tractor)

if __name__ == "__main__":
    # python -m test_ui.flow.queue_monitor
    qm = QMon()
    # qm.backup_confirm()
    qm.test()