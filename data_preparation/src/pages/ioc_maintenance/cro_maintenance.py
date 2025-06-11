from datetime import datetime
from helper.logger import logger
from helper.win_utils import wait_for_window, sendkeys
from src.core.driver import BaseDriver
from src.common.menu import Menu
from helper.paths import ProjectPaths

class CROMaintenance(BaseDriver):
    MODULE = "CRO"

    def __init__(self, external_driver=None):
        super().__init__(external_driver=external_driver)
        self.cro_config = self.config["cro"]

        self.bol = "BL01"
        self.owner = "NVD"
        self.date = "01012026"
        self.time = "0000"
        self.agent = "TEST"

    def cro_actions(self):
        df, p = next(ProjectPaths.get_gate_pickup_data())
        self.create_cro(df, p)
        self.get_pin(df, p)

    def create_cro(self, df, p) -> None:
        if not self.properties.visible(self.cro_config["cro_cntr_id"], timeout=1):
            logger.info("Opening CRO module")
            Menu.to_module(self.MODULE, self)

        if not self.properties.visible(self.cro_config["create_cntr_id"], timeout=1):
            logger.info("Resetting CRO form")
            self.actions.click(self.cro_config["reset"])

        df_filtered = df[df["mvt"].isna() & df["cntr_id"].notna() & df["cro_no"].isna()]
        if df_filtered.empty:
            logger.warning("No containers to create CRO for")
            return

        for cntr_id in df_filtered["cntr_id"]:
            logger.info(f"Creating CRO for cntr_id: {cntr_id}")
            self.actions.click(self.cro_config["create"])
            self.actions.click(self.cro_config["create_cntr_id"])
            sendkeys(cntr_id, with_tab=True)
            sendkeys(self.bol, with_tab=True)

            cro_no = self.generate_cro()
            sendkeys(cro_no, with_tab=True)

            sendkeys(self.owner, with_tab=True)
            sendkeys(self.date)
            sendkeys(self.time)
            sendkeys(self.agent, with_tab=True)
            sendkeys("{TAB}")
            sendkeys(self.date)
            sendkeys("{ENTER}")

            if wait_for_window("User Error", timeout=1):
                logger.error("User Error in CRO creation")
                raise RuntimeError("User Error detected")

            if not wait_for_window("User Information", timeout=5):
                logger.error("User Information window not found")
                raise RuntimeError("User Information window not found")

            sendkeys("{ENTER}")
            self.update_column(df, cntr_id, "cro_no", cro_no)
            df.to_csv(p, index=False)

    @staticmethod
    def update_column(df, cntr_id, column: str, value) -> None:
        mask = df["cntr_id"] == cntr_id
        if mask.any():
            df.loc[mask, column] = value
            logger.info(f"Updated {column} for {cntr_id} to {value}")
        else:
            raise Exception(f"Cannot update {column} for {cntr_id}")

    @staticmethod
    def generate_cro() -> str:
        now = datetime.now()
        cro_no = now.strftime("%d%m%H%M%S")
        logger.debug(f"Generated CRO number: {cro_no}")
        return cro_no

    def get_pin(self, df, p) -> None:
        cro_status = "active"

        df_filtered = df[df["pin"].isna() & df["cntr_id"].notna() & df["mvt"].isna()]
        if df_filtered.empty:
            logger.warning("No containers to fetch pins for")
            return

        logger.info("Fetching pins for CRO")
        
        # Ensure we're in the CRO module before trying to reset
        if not self.properties.visible(self.cro_config["cro_cntr_id"], timeout=1):
            logger.info("Opening CRO module")
            Menu.to_module(self.MODULE, self)
        
        self.actions.click(self.cro_config["reset"])
        self.actions.click(self.cro_config["cro_status"])
        sendkeys(cro_status)
        for cntr_id in df_filtered["cntr_id"]:
            logger.info(f"Fetching pin for cntr_id: {cntr_id}")
            self.actions.click(self.cro_config["cro_cntr_id"])
            sendkeys("^a")
            sendkeys(cntr_id)
            sendkeys("{ENTER}")
            pin = self.properties.text_value(self.cro_config["row0_pin"])
            self.update_column(df, cntr_id, "pin", pin)
            df.to_csv(p, index=False)

if __name__ == "__main__":
    c = CROMaintenance()
    c.cro_actions()