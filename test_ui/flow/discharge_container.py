import time
import sys

from helper.field_utils import send_keys_tab
from helper.function_shortcut import enter_to_function_view
from helper.utils import update_json, wait_for_window, update_next_stowage, get_match_windows

from pywinauto.keyboard import send_keys

from test_ui.container_interface import CntrBase

class DischargeContainer(CntrBase):
    module = "DC"

    def __init__(self):
        super().__init__()
        self.dc_voyage = self.config["dc"]["voyage"]
        self.search_btn = self.config["dc"]["search_btn"]
        self.cntr_btn = self.config['dc']['cntr_btn']
        self.cntr_panel = self.config['dc']['cntr_panel']
        self.create_btn = self.config['dc']['create_btn']
        self.dc_bay = self.config['dc']['bay']
        self.add_next = self.config['dc']['add_next_btn']
        self.warning_ok = self.config['dc']['warning_ok_btn']
        self.dc_pol = self.config['dc']['pol']

        self.sp_menu = self.config["nGen"]["sp_menu"]

    def search_voyage(self):
        if not self.visible(self.dc_voyage, 1):
            self.click(self.title)
            self.module_view()
        self.click(self.dc_voyage)
        send_keys("^a")
        send_keys_tab(self.line)
        send_keys(self.vessel)
        send_keys(self.voyage)
        self.click(self.search_btn)
        if wait_for_window('User Information', 1.5):
            send_keys("{ENTER}")
        self.click(self.cntr_btn)
        # send_keys('%a')

    def create_cntr(self):
        if not self.visible(self.cntr_panel, 1):
            self.click(self.title)
            self.module_view()
            if not self.visible(self.cntr_panel, 1):
                self.search_voyage()

        if self.visible(self.create_btn, 1):
            self.click(self.create_btn)
        # send_keys('{ENTER}')
        self.common_details()
        print('=== Done ===')

    def common_details(self):
        self.click(self.dc_bay)
        send_keys_tab(self.bay)
        send_keys("^a")
        send_keys(self.row)
        send_keys(self.tier)
        send_keys_tab(self.cntr_id)
        send_keys_tab(self.owner)
        send_keys(self.status)
        send_keys(self.size)
        send_keys(self.type)
        send_keys(self.gross_wt)
        send_keys("{TAB}")
        send_keys(self.pol)
        if self.text_value(self.dc_pol) != self.pol.upper():
            print(f"Values {self.text_value(self.dc_pol)} do not match {self.pol}. Exiting the program.")
            sys.exit(1)

        self.click(self.add_next)

        if get_match_windows('User Error'):
            print(f"Warning message: {self.text_value('User Error')}")
            sys.exit(1)

        if self.visible(self.warning_ok, 1):
            self.click(self.warning_ok)

        d = update_next_stowage(self.cntr_id, self.bay, self.row, self.tier, self.json_path)
        for k, v in d.items():
            setattr(self, k, v)

    def module_view(self):
        self.click(self.home)
        self.click(self.sp_menu)
        send_keys("{F2}")

    def test(self):
        if get_match_windows('User Error'):
            print('True')
            sys.exit(1)
        print('keep going')
        # self.click(self.create_btn)

if __name__ == '__main__':
    # python -m test_ui.flow.discharge_container
    dc = DischargeContainer()
    # dc.search_voyage()
    for _ in range(3):
        dc.create_cntr()
        # dc.test()
    # dc.test()
    # dc.create_cntr()