from pathlib import Path
from helper.io_utils import read_csv
from helper.logger import logger
from helper.win_utils import send_keys_wlog, wait_for_window, focus_window, find_window
from test_ui.flow.voyage import Voyage

class DischargeContainer(Voyage):
    module = "DC"

    def __init__(self, external_driver=None):
        super().__init__(external_driver=external_driver)
        self.line = "NVD"
        self.vessel = "TSHM04"
        self.voyage = "V01"

        self.dc = self.config["dc"]
        self.sc = self.dc["schedule"]

    def search_voyage(self):
        if not self.properties.visible(self.dc["voyage"], timeout=1):
            self.module_view(self.module)

        self.actions.click(self.dc["voyage"])
        send_keys_wlog("^a")
        send_keys_wlog(self.line, with_tab=True)
        send_keys_wlog(self.vessel)
        send_keys_wlog(self.voy)
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
        path = Path("data/vessel_discharge_data.csv")
        df = read_csv(path)

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
            self.module_view(self.module)

        send_keys_wlog("%r")
        self.actions.click(self.dc["voyage"])
        send_keys_wlog("^a")
        send_keys_wlog(self.line, field_length=4)
        send_keys_wlog(self.vessel, field_length=6)
        send_keys_wlog(self.voyage)
        send_keys_wlog("%s")

        if self.properties.visible(self.dc["data_confirmed"]):
            send_keys_wlog("%t")
        else:
            logger.error("Confirm button is not visible")
            raise

        if wait_for_window("confirm"):
            send_keys_wlog("{ENTER}")
        else:
            raise Exception("Confirm window not found")

    def actions_chains(self):
        self.open_voyage_plan()
        self.setup_voyage("Disc")
        self.edit_add()
        self.order_out_all()

    def reset_voyage(self):
        import time
        module = "VS"

        if not self.properties.visible(self.sc["voyage"], timeout=1):
            self.module_view(module)

        send_keys_wlog("%r")

        self.actions.click(self.sc["voyage"])
        send_keys_wlog("^a")
        send_keys_wlog(self.line, field_length=4)
        send_keys_wlog(self.vessel, field_length=6)
        send_keys_wlog(self.voy)

        self.actions.click(self.sc["start"])
        send_keys_wlog("^a")
        send_keys_wlog("{DEL}")

        self.actions.click(self.sc["end"])
        send_keys_wlog("^a")
        send_keys_wlog("{DEL}")

        send_keys_wlog("%s")

        self.actions.click(self.sc["row"])
        send_keys_wlog("%l")
        send_keys_wlog("{F1}")

        time.sleep(0.7)
        if find_window("Confirm"):
            send_keys_wlog("{ENTER}")
        else:
            logger.error("Confirm window not found after reset voyage")
            raise

        time.sleep(0.5)
        if find_window(".*sp0516$"):
            send_keys_wlog("{ENTER}")

if __name__ == "__main__":
    dc = DischargeContainer()
    dc.reset_voyage()