import sys
from helper.utils import wait_for_window, send_keys_tab, _send_keys
from test_ui.base_flow import BaseFlow

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
        self.actions.click(self.bol_line)
        _send_keys('^a')
        send_keys_tab(self.line)
        _send_keys(self.bol)
        _send_keys('{ENTER}')

    def create_bol(self):
        if not self.properties.visible(self.bol_line):
            self.module_view(self.module)
        self.search_bol()
        if wait_for_window('User Error ioc5618', 1):
            _send_keys('{ENTER}')
            _send_keys('%a')
            if self.properties.editable(self.details_line) == 'True':
                send_keys_tab(self.line)
                send_keys_tab(self.bol)
                send_keys_tab('automation')
                _send_keys('{TAB}')
                send_keys_tab('automation')
                _send_keys('{TAB}')
                send_keys_tab('automation')
                _send_keys('{TAB}')
                send_keys_tab(self.line)
                _send_keys(self.vessel)
                send_keys_tab(self.voyage)
                for _ in range(3):
                    _send_keys('{TAB}')
                _send_keys('test')
                _send_keys('{ENTER}')
            else:
                sys.exit(1)

    def add_cntr(self):
        if not self.properties.visible(self.add_cntr_btn, 1):
            self.module_view(self.module)
        self.search_bol()
        self.actions.click(self.add_cntr_btn)
        if not wait_for_window('Create Bill of lading container'):
            sys.exit(1)

        for cntr_id in self.df['cntr_id']:
            self.actions.click(self.create_cntr_id)
            _send_keys(cntr_id)
            self.actions.click(self.add_next)
            wait_for_window('Confirm')
            self.actions.click(self.confirm_yes)
            if wait_for_window('User Error', 1):
                sys.exit(1)

        self.actions.click(self.create_cancel)

    def test(self):
        self.module_view(self.module)

if __name__ == "__main__":
    # python -m test_ui.flow.bol_maintenance
    bol = BolMaintenance()
    # bol.module_view()
    # bol.search_bol()
    bol.add_cntr()
    # bol.test()
    # bol.create_bol()