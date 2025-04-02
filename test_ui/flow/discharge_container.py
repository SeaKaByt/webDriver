import time

from helper.field_utils import send_keys_tab
from helper.function_shortcut import enter_to_function_view
from helper.utils import update_json, wait_for_window

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

    def search_voyage(self):
        if not self.visible(self.dc_voyage, 1):
            self.click(self.title)
            enter_to_function_view(module=self.module)
        self.click(self.dc_voyage)
        send_keys("^a")
        send_keys_tab(self.line)
        send_keys(self.vessel)
        send_keys(self.voyage)
        self.click(self.search_btn)
        if wait_for_window('User Information', 1.5):
            send_keys("{ENTER}")
        self.click(self.cntr_btn)
        send_keys('%a')

    def create_cntr(self):
        if not self.visible(self.cntr_panel, 1):
            self.search_voyage()
            self.click(self.create_btn)
        self.common_details()
        print('=== Done ===')

    def common_details(self):
        time.sleep(0.2)
        self.click(self.dc_bay)
        time.sleep(0.2)
        send_keys_tab(self.bay)
        time.sleep(0.2)
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
        self.next_details()

    def next_details(self, next_update=None):
        bay_l = self.bay[-1]
        bay_n = int(self.bay[:-1])

        print("=== Generating next cntr ===")
        cntr_id = int(self.cntr_id[4:])
        self.cntr_id = f"test{cntr_id + 1:06}"

        if int(self.row) == 12 and int(self.tier) == 98:
            bay_l = "D" if bay_l == "H" else "H"
            bay_n += 2 if bay_l == "D" else 0
        self.bay = f"{bay_n:02d}{bay_l}"

        if int(self.tier) == 98 and self.row == "12":
            self.tier = "82"
        elif self.row == "12":
            self.tier = f"{int(self.tier) + 2}"

        self.row = "01" if int(self.row) == 12 else f"{int(self.row) + 1:02d}"

        update_data = {
            'cntr_id': self.cntr_id,
            'bay': self.bay,
            'row': self.row,
            'tier': self.tier
        }

        for k, v in update_data.items():
            print(f"{k}: {v}")
            update_json(self.json_path, [k], v)
        print("=== JSON Updated ===")

    def test(self):
        pass

if __name__ == '__main__':
    # python -m test_ui.flow.discharge_container
    dc = DischargeContainer()
    # dc.search_voyage()
    for _ in range(2):
        # dc.create_cntr()
        dc.next_details()
    # dc.test()