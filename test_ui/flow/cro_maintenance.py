import sys
from datetime import datetime
from helper.decorators import logger
from helper.utils import send_keys_tab, wait_for_window, _send_keys
from test_ui.base_flow import BaseFlow

class CROMaintenance(BaseFlow):
    module = "CRO"
    pin_list = []

    def __init__(self):
        super().__init__()
        self.reset = self.config['cro']['reset']
        self.create = self.config['cro']['create']
        self.cro_cntr_id = self.config['cro']['cro_cntr_id']
        self.cro_cro_no = self.config['cro']['cro_cro_no']
        self.create_cntr_id = self.config['cro']['create_cntr_id']
        self.cro_status = self.config['cro']['cro_status']
        self.row0_pin = self.config['cro']['row0_pin']

    def create_cro(self):
        if not self.properties.visible(self.cro_cntr_id, 1):
            self.module_view(self.module)
        if not self.properties.visible(self.create_cntr_id, 1):
            self.actions.click(self.reset)
        for cntr_id in self.df['cntr_id']:
            self.actions.click(self.create)
            self.actions.click(self.create_cntr_id)
            send_keys_tab(cntr_id)
            send_keys_tab(self.bol)
            self.generate_cro()
            send_keys_tab(self.cro_no)
            send_keys_tab(self.owner)
            _send_keys(self.date)
            _send_keys(self.time)
            send_keys_tab(self.agent)
            _send_keys('{TAB}')
            _send_keys(self.date)
            _send_keys('{ENTER}')
            if wait_for_window('User Error', 1):
                sys.exit(1)
            wait_for_window('User Information')
            _send_keys('{ENTER}')

        # self.df['cro_no'] = self.cro_no_list
        # print(self.df)
        # self.df.to_excel(self.data_path, index=False)

    def generate_cro(self):
        now = datetime.now()

        self.cro_no = now.strftime("%d%m%H%M%S")
        # self.cro_no_list.append(self.cro_no)

    def get_pin(self):
        self.actions.click(self.reset)
        self.actions.click(self.cro_status)
        _send_keys('active')
        for cntr_id in self.df['cntr_id']:
            self.actions.click(self.cro_cntr_id)
            _send_keys('^a')
            _send_keys(cntr_id)
            _send_keys('{ENTER}')
            pin = self.properties.text_value(self.row0_pin)
            self.pin_list.append(int(pin))
            if wait_for_window('User Information', 1):
                sys.exit(1)

        self.df['pin'] = self.pin_list
        logger.info(f"Dataframe: {self.df}")
        self.df.to_excel(self.data_path, index=False)

    def test(self):
        pass

if __name__ == "__main__":
    # python -m test_ui.flow.cro_maintenance
    cro = CROMaintenance()
    cro.create_cro()
    cro.get_pin()