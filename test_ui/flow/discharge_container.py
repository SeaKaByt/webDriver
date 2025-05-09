import csv
import sys
from pathlib import Path

from helper.io_utils import read_csv
from helper.sys_utils import raise_with_log
from helper.win_utils import send_keys_with_log, wait_for_window
from test_ui.base_flow import BaseFlow
from pywinauto.keyboard import send_keys

from test_ui.flow.voyage_plan import Voyage


class DischargeContainer(Voyage):
    module = "DC"

    def __init__(self):
        super().__init__()
        dc_config = self.config["dc"]
        self.dc_voyage = dc_config["voyage"]
        self.search_btn = dc_config["search_btn"]
        self.data_confirmed_btn = dc_config["data_confirmed_btn"]
        self.confirm_ok_btn = dc_config["confirm_ok_btn"]
        self.mono_plan_add = dc_config["mono_plan_add"]
#         self.cntr_btn = self.config['dc']['cntr_btn']
#         self.cntr_panel = self.config['dc']['cntr_panel']
#         self.create_btn = self.config['dc']['create_btn']
#         self.dc_bay = self.config['dc']['bay']
#         self.add_next = self.config['dc']['add_next_btn']
#         self.warning_ok = self.config['dc']['warning_ok_btn']
#         self.dc_pol = self.config['dc']['pol']
#
    def search_voyage(self):
        if not self.properties.visible(self.dc_voyage, 1):
            self.module_view(self.module)

        self.actions.click(self.dc_voyage)
        send_keys("^a")
        send_keys_with_log(self.line, True)
        send_keys_with_log(self.vessel)
        send_keys_with_log(self.voyage)
        self.actions.click(self.search_btn)

    def data_confirmed(self):
        if self.properties.enabled(self.data_confirmed_btn):
            self.actions.click(self.data_confirmed_btn)
            wait_for_window("confirm")
            self.actions.click(self.confirm_ok_btn)
        else:
            raise_with_log("Data Confirmed button is not enabled.")

    def drag_release(self):
        self.actions.click(self.mono_plan_add)
        self.actions.drag_release(self.plan_section, 50, 50, 680, 370)

    def mono_add(self) -> None:
        path =  Path("data/dc_data.csv")
        with open(path, 'r') as file:
            reader = csv.reader(file)
            header = next(reader)
            for row_num, row in enumerate(reader, start=1):
                if row['ContainerNum']:
                    print(f"Row {row_num}: {row["ContainerNum"]}")

#     def create_cntr(self):
#         if not self.visible(self.cntr_panel, 1):
#             self.click(self.title)
#             self.module_view(self.module)
#             if not self.visible(self.cntr_panel, 1):
#                 self.search_voyage()
#
#         if self.visible(self.create_btn, 1):
#             self.click(self.create_btn)
#         # send_keys('{ENTER}')
#         self.common_details()
#         print('=== Done ===')
#
#     def common_details(self):
#         self.click(self.dc_bay)
#         send_keys_tab(self.bay)
#         send_keys("^a")
#         send_keys(self.row)
#         send_keys(self.tier)
#         send_keys_tab(self.cntr_id)
#         send_keys_tab(self.owner)
#         send_keys(self.status)
#         send_keys(self.size)
#         send_keys(self.type)
#         send_keys(self.gross_wt)
#         send_keys("{TAB}")
#         send_keys(self.pol)
#         if self.text_value(self.dc_pol) != self.pol.upper():
#             print(f"Values {self.text_value(self.dc_pol)} do not match {self.pol}. Exiting the program.")
#             sys.exit(1)
#
#         self.click(self.add_next)
#
#         if get_match_windows('User Error'):
#             print(f"Warning message: {self.text_value('User Error')}")
#             sys.exit(1)
#
#         if self.visible(self.warning_ok, 1):
#             self.click(self.warning_ok)
#
#         d = update_next_stowage(self.cntr_id, self.bay, self.row, self.tier, self.json_path)
#         for k, v in d.items():
#             setattr(self, k, v)
#
#     def test(self):
#         pass
#
if __name__ == '__main__':
    # python -m test_ui.flow.discharge_container
    dc = DischargeContainer()
    # dc.search_voyage()
    # dc.data_confirmed()
    dc.mono_add()