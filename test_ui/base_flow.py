from helper.utils import wait_for_window
from main import BaseDriver
from pywinauto.keyboard import send_keys

class BaseFlow(BaseDriver):

    def __init__(self):
        super().__init__()
        self.df = self.df

        self.title = self.config["nGen"]["title"]
        self.home = self.config["nGen"]["home_btn"]

        self.inv_menu = self.config["nGen"]["inv_menu"]
        self.sp_menu = self.config["nGen"]["sp_menu"]
        self.ioc_menu = self.config['nGen']['ioc_menu']
        self.gate_menu = self.config['nGen']['gate_menu']
        self.mv_menu = self.config['nGen']['mv_menu']

        self.cntr_id = self.config_j["cntr_id"]
        self.status = self.config_j["status"]
        self.size = self.config_j["size"]
        self.type = self.config_j["type"]
        self.owner = self.config_j["owner"]
        self.block = self.config_j["block"]
        self.stack = self.config_j["stack"]
        self.lane = self.config_j["lane"]
        self.material = self.config_j["material"]
        self.max_gross_wt = self.config_j["max_gross_wt"]
        self.line = self.config_j["line"]
        self.vessel = self.config_j["vessel"]
        self.voyage = self.config_j["voyage"]
        self.pol = self.config_j["POL"]
        self.gross_wt = self.config_j["gross_wt"]
        self.bay = self.config_j["bay"]
        self.row = self.config_j['row']
        self.tier = self.config_j['tier']

        self.bol = self.config_j["cro"]["bol"]
        self.cro_no = ""
        self.date = "01012026"
        self.time = "0000"
        self.agent = "TEST"

    def module_view(self, module=None):
        self.click(self.title)
        self.click(self.home)

        if module == "HR":
            self.click(self.inv_menu)
            send_keys('{F2}')
            send_keys('{F4}')

        elif module == "DC":
            self.click(self.sp_menu)
            send_keys("{F2}")

        elif module == "CRO":
            self.click(self.ioc_menu)
            send_keys('{F1}')
            send_keys('{F7}')

        elif module == "BOL":
            self.click(self.ioc_menu)
            send_keys('{F1}')
            send_keys('{F2}')

        elif module == "CD":
            self.click(self.inv_menu)
            send_keys("{F2}")
            send_keys("{F1}")

        elif module == "GT":
            self.click(self.gate_menu)
            send_keys("{F1}")
            send_keys("{F1}")
            if wait_for_window('Select Working Terminal', 1):
                send_keys('{ENTER}')

        elif module == "QM":
            self.click(self.mv_menu)
            send_keys("{F3}")

