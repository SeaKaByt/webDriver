from pathlib import Path
from helper.io_utils import read_csv
from helper.logger import logger
from helper.win_utils import send_keys_with_log, wait_for_window
from test_ui.flow.voyage import Voyage

class DischargeContainer(Voyage):
    module = "DC"

    def __init__(self):
        super().__init__()
        self.dc_config = self.config["dc"]

    def search_voyage(self):
        if not self.properties.visible(self.dc_config["voyage"], timeout=1):
            self.module_view(self.module)

        self.actions.click(self.dc_config["voyage"])
        send_keys_with_log("^a")
        send_keys_with_log(self.line, with_tab=True)
        send_keys_with_log(self.vessel)
        send_keys_with_log(self.voyage)
        self.actions.click(self.dc_config["search_btn"])

    def data_confirmed(self):
        if self.properties.enabled(self.dc_config["data_confirmed_btn"]):
            self.actions.click(self.dc_config["data_confirmed_btn"])
            if wait_for_window("confirm"):
                self.actions.click(self.dc_config["confirm_ok_btn"])
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
        if not self.properties.visible(self.dc_config["data_confirmed_btn"]):
            self.module_view(self.module)

        send_keys_with_log("%r")
        self.actions.click(self.dc_config["voyage"])
        send_keys_with_log("^a")
        send_keys_with_log(self.line, with_tab=True)
        send_keys_with_log(self.vessel)
        send_keys_with_log(self.voyage)
        send_keys_with_log("%s")

        if not self.properties.visible(self.dc_config["result_table"]):
            raise Exception("Result table is not visible")
        send_keys_with_log("%t")

        if wait_for_window("confirm"):
            send_keys_with_log("{ENTER}")
        else:
            raise Exception("Confirm window not found")

    def voyage_discharge_actions(self):
        self.data_confirmed()
        self.open_voyage_plan()
        self.setup_voyage("Load", "Disc")
        self.edit_add()
        self.order_out_all()

if __name__ == "__main__":
    dc = DischargeContainer()
    dc.voyage_discharge_actions()