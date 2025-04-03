from main import BaseDriver

class CntrBase(BaseDriver):

    def __init__(self):
        super().__init__()

        self.title = self.config["nGen"]["title"]
        self.home = self.config["nGen"]["home_btn"]

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