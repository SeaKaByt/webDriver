import sys
import time

from scripts.regsetup import description

from helper.decorators import logger
from test_ui.flow.queue_monitor import QMon
from test_ui.base_flow import BaseFlow
from helper.utils import wait_for_window, send_keys_tab, _send_keys

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
        # self.module_view(self.module)

    def create_pickup(self):
        self.get_tractor()
        if not self.properties.visible(self.search_tractor, 1):
            self.module_view(self.module)

        for i in range(self.df['cntr_id'].count()):
            self.actions.click(self.search_tractor)
            _send_keys(self.df['tractor'][i])
            _send_keys('{ENTER}')
            _send_keys('%1')
            wait_for_window('Create')
            self.actions.click(self.create_pin)
            _send_keys(str(self.df['pin'][i]))
            self.actions.click(self.create_driver)
            _send_keys(self.df['tractor'][i])
            _send_keys('{ENTER}')
            wait_for_window('Confirmation')
            _send_keys('{ENTER}')
            wait_for_window('Insufficient')
            send_keys_tab(self.username)
            _send_keys(self.password)
            _send_keys('{ENTER}')
            time.sleep(1)
            _send_keys('{ENTER}')
            if wait_for_window('Confirmation'):
                _send_keys('{ENTER}')
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
        logger.info(f"Dataframe: {self.df}")
        self.df.to_excel(self.data_path, index=False)

    def release_print_cwp(self):
        self.actions.click(self.row0_cntr_id)
        _send_keys('%3')
        time.sleep(1)
        _send_keys('%7')
        wait_for_window('Print')
        _send_keys('dummy')
        _send_keys('{ENTER}')
        if not wait_for_window('User Information'):
            logger.warning("User Information window not found")
            sys.exit(1)
        _send_keys('{ENTER}')

    def confirm_pickup(self):
        if not self.properties.visible(self.search_tractor, 1):
            self.module_view(self.module)

        for tractor in self.df['tractor']:
            self.actions.click(self.search_tractor)
            _send_keys(tractor)
            _send_keys('{ENTER}')
            _send_keys('%4')
            if wait_for_window('Confirm', 5):
                _send_keys('{TAB}')
                _send_keys('{ENTER}')
                wait_for_window('Exit Gate')
                _send_keys('2000')
                self.actions.click(self.inspection_seal)
                _send_keys('yfn')
                _send_keys('{ENTER}')
            elif not wait_for_window('Gate Confirm', 1):
                sys.exit(1)
            self.actions.click(self.manual_confirm_btn)
            wait_for_window('Gate Confirm')
            # self.actions.click(self.printer_id)
            # _send_keys('dummy')
            _send_keys('{ENTER}')
            time.sleep(1)

    def test(self):
        pass

if __name__ == "__main__":
    # python -m test_ui.flow.gate_transaction
    # parser = argparse.ArgumentParser(description='Gate Transaction')

    gt = GateTransaction()
    gt.create_pickup()
    gt.confirm_pickup()
