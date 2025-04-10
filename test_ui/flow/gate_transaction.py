import sys
import time
from test_ui.base_flow import BaseFlow
from helper.utils import wait_for_window, send_keys_tab
from pywinauto.keyboard import send_keys

class GateTransaction(BaseFlow):
    module = 'GT'
    tractor_list = []

    def __init__(self):
        super().__init__()

        self.username = self.config["nGen"]["username"]
        self.password = self.config["nGen"]["password"]

        self.search_tractor = self.config['gt']['search_tractor']
        self.create_pin = self.config['gt']['create_pin']
        self.create_driver = self.config['gt']['create_driver']
        self.row0_cntr_id = self.config['gt']['row0_cntr_id']
        self.inspection_seal = self.config['gt']['inspection_seal']
        self.manual_confirm_btn = self.config['gt']['manual_confirm_btn']
        self.printer_id = self.config['gt']['printer_id']

    def create_pickup(self):
        self.get_tractor()
        if not self.visible(self.search_tractor, 1):
            self.module_view(self.module)

        for i in range(self.df['cntr_id'].count()):
            self.click(self.search_tractor)
            send_keys(self.df['tractor'][i])
            send_keys('{ENTER}')
            send_keys('%1')
            wait_for_window('Create')
            self.click(self.create_pin)
            send_keys(str(self.df['pin'][i]))
            self.click(self.create_driver)
            send_keys(self.df['tractor'][i])
            send_keys('{ENTER}')
            wait_for_window('Confirmation')
            send_keys('{ENTER}')
            wait_for_window('Insufficient')
            send_keys_tab(self.username)
            send_keys(self.password)
            send_keys('{ENTER}')
            time.sleep(1)
            send_keys('{ENTER}')
            if wait_for_window('Confirmation'):
                send_keys('{ENTER}')
                time.sleep(1)
            else:
                sys.exit(1)
            self.release_print_cwp()

    def get_tractor(self):
        ids = self.df['cntr_id'].count()
        tractor_list = [f'OXT{i:02d}' for i in range(1, ids + 1)]

        # for i in range(ids):
        #     index = i // 2
        #     _tractor_list.append(tractor_list[index])

        self.df['tractor'] = tractor_list
        self.df.to_excel(self.data_path, index=False)

    def release_print_cwp(self):
        self.click(self.row0_cntr_id)
        send_keys('%3')
        time.sleep(1)
        send_keys('%7')
        wait_for_window('Print')
        send_keys('dummy')
        send_keys('{ENTER}')
        wait_for_window('User Information')
        send_keys('{ENTER}')

    def confirm_pickup(self):
        if not self.visible(self.search_tractor, 1):
            self.module_view(self.module)

        for tractor in self.df['tractor']:
            self.click(self.search_tractor)
            send_keys(tractor)
            send_keys('{ENTER}')
            send_keys('%4')
            if wait_for_window('Confirm', 2):
                send_keys('{TAB}')
                send_keys('{ENTER}')
                wait_for_window('Exit Gate')
                send_keys('2000')
                self.click(self.inspection_seal)
                send_keys('yfn')
                send_keys('{ENTER}')
            elif not wait_for_window('Gate Confirm', 1):
                sys.exit(1)
            self.click(self.manual_confirm_btn)
            wait_for_window('Gate Confirm')
            # self.click(self.printer_id)
            # send_keys('dummy')
            send_keys('{ENTER}')
            time.sleep(1)

    def test(self):
        if wait_for_window('Confirm', 1):
            print('Found Confirm')
        elif not wait_for_window('Gate Confirm', 1):
            print('Not Found Confirm')

if __name__ == "__main__":
    # python -m test_ui.flow.gate_transaction
    gt = GateTransaction()
    # gt.create_pickup()
    # gt.release_print_cwp()
    gt.confirm_pickup()
    # gt.test()
