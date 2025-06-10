import time

from helper.logger import logger
from helper.paths import ProjectPaths
from helper.win_utils import sendkeys, wait_for_window, focus_window, find_window
from src.pages.guider.voyage import Voyage
from src.common.menu import Menu

class DischargeContainer(Voyage):
    MODULE = "DC"

    def __init__(self, external_driver=None):
        super().__init__(external_driver=external_driver)
        self.dc = self.config["dc"]
        self.sc = self.dc["schedule"]

        self.line = "NVD"
        self.vessel = "TSHM04"
        self.voyage = "V01"

    def search_voyage(self):
        if not self.properties.visible(self.dc["voyage"], timeout=1):
            Menu.to_module(self.MODULE, self)

        self.actions.click(self.dc["voyage"])
        sendkeys("^a")
        sendkeys(self.line, field_length=4)
        sendkeys(self.vessel, field_length=6)
        sendkeys(self.voyage)
        self.actions.click(self.dc["search_btn"])

        if self.properties.enabled(self.dc["data_confirmed_btn"]):
            self.actions.click(self.dc["data_confirmed_btn"])
            if wait_for_window("confirm"):
                self.actions.click(self.dc["confirm_ok_btn"])
            else:
                raise Exception("Confirm window not found")
        else:
            raise Exception("Data Confirmed button is not enabled")

    def edit_add(self) -> None:
        df, path = next(ProjectPaths.get_discharge_data())

        df_filtered = df[df["planned"].isna() & df["ContainerNum"].notna()]
        if df_filtered.empty:
            raise Exception("No unplanned containers found")

        for bay, group in df_filtered.groupby("Bay"):
            logger.info(f"Processing bay: {bay}")
            self.setup_bay(bay)
            self.panel_drag_release("edit_plan_add")
            if wait_for_window(".*(User Error|Host Error).*", timeout=1):
                raise Exception("User Error window appeared")

        if not wait_for_window(".*(User Error|Host Error).*", timeout=1):
            df.loc[df["ContainerNum"].isin(df_filtered["ContainerNum"]), "planned"] = "Yes"
            df.to_csv(path, index=False)

    def data_confirm(self) -> None:
        focus_window("nGen")
        if not self.properties.visible(self.dc["data_confirmed"]):
            Menu.to_module(self.MODULE, self)

        sendkeys("%r")
        self.actions.click(self.dc["voyage"])
        sendkeys("^a")
        sendkeys(self.line, field_length=4)
        sendkeys(self.vessel, field_length=6)
        sendkeys(self.voyage)
        sendkeys("%s")

        if self.properties.visible(self.dc["data_confirmed"]):
            sendkeys("%t")
        else:
            logger.error("Confirm button is not visible")
            raise

        if wait_for_window("confirm"):
            sendkeys("{ENTER}")
        else:
            raise Exception("Confirm window not found")

    def actions_chains(self):
        self.open_voyage_plan()
        self.setup_voyage("Disc")
        self.edit_add()
        self.order_out_all()

    def reset_voyage(self):
        focus_window("nGen")

        module = "VS"
        if not self.properties.visible(self.sc["voyage"], timeout=1):
            Menu.to_module(module, self)

        sendkeys("%r")

        self.actions.click(self.sc["voyage"])
        sendkeys("^a")
        sendkeys(self.line, field_length=4)
        sendkeys(self.vessel, field_length=6)
        sendkeys(self.voyage)

        self.actions.click(self.sc["start"])
        sendkeys("^a")
        sendkeys("{DEL}")

        self.actions.click(self.sc["end"])
        sendkeys("^a")
        sendkeys("{DEL}")

        sendkeys("%s")

        self.actions.click(self.sc["row"])
        sendkeys("%l")
        sendkeys("{F1}")

        time.sleep(1) # more time for the window to appear
        if find_window("Confirm"):
            sendkeys("{ENTER}")
        else:
            logger.error("Confirm window not found after reset voyage")
            raise

        time.sleep(0.5)
        if find_window(".*sp0516$"):
            sendkeys("{ENTER}")

if __name__ == "__main__":
    dc = DischargeContainer()
    dc.reset_voyage()