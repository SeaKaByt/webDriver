import time
from pathlib import Path
from helper.io_utils import read_excel, read_csv
from helper.logger import logger
from helper.sys_utils import raise_with_log
from helper.win_utils import send_keys_with_log, wait_for_window
from pywinauto.keyboard import send_keys
from test_ui.flow.voyage_plan import Voyage

class DischargeContainer(Voyage):
    module = "DC"

    def __init__(self):
        super().__init__()
        dc_config = self.config["dc"]
        self.dc_voyage = dc_config["voyage"]
        self.search_btn = dc_config["search_btn"]
        self.data_confirmed_btn = dc_config["data_confirmed_btn"]
        self.confirm_ok_btn = dc_config["confirm_ok_btn"]
        self.edit_plan_add = dc_config["edit_plan_add"]
        self.dc_voyage = dc_config["dc_voyage"]
        self.result_table = dc_config["result_table"]

    def search_voyage(self):
        if not self.properties.visible(self.dc_voyage, 1):
            self.module_view(self.module)

        self.actions.click(self.dc_voyage)
        send_keys("^a")
        send_keys_with_log(self.line, True)
        send_keys_with_log(self.vessel)
        send_keys_with_log(self.voyage)
        self.actions.click(self.search_btn)

    def data_confirmed(self):
        if self.properties.enabled(self.data_confirmed_btn):
            self.actions.click(self.data_confirmed_btn)
            wait_for_window("confirm")
            self.actions.click(self.confirm_ok_btn)
        else:
            raise_with_log("Data Confirmed button is not enabled.")

    def drag_release(self):
        self.actions.click(self.edit_plan_add)
        self.actions.drag_release(self.plan_section, 50, 50, 680, 370)

    def edit_add(self) -> None:
        path =  Path("data/vessel_discharge_data.csv")
        df = read_csv(path)

        if not wait_for_window("Voyage", timeout=1):
            self.open_voyage_plan()
            time.sleep(10)

        self.actions.click(self.refresh_btn)
        self.actions.click(self.voyage_qc)
        send_keys_with_log("^a")
        send_keys_with_log(self.qc)
        send_keys_with_log("{ENTER}")
        self.set_display_scale()

        if self.properties.item_text(self.qc_methods) == "Load":
            self.actions.click(self.qc_methods)

        if self.properties.text_value(self.qc_methods) != "Disc":
            raise_with_log("QC method is not Disc")

        df_filtered = df[df['planned'].isna() & df['ContainerNum'].notna()]
        if df_filtered.empty:
            raise_with_log("No unplanned containers found")
        grouped = df_filtered.groupby('Bay')

        for bay, group in grouped:
            logger.info(f"Processing bay: {bay}")
            self.setup_bay(bay)
            self.edit_plan_drag_release()
            if wait_for_window(".*(User Error|Host Error).*", timeout=1):
                raise_with_log("User Error window appeared")

        if not wait_for_window(".*(User Error|Host Error).*", timeout=1):
            df.loc[df['ContainerNum'].isin(df_filtered['ContainerNum']), 'planned'] = "Yes"
            df.to_csv(path, index=False)

    def edit_plan_drag_release(self) -> None:
        self.actions.click(self.edit_plan_add)
        self.actions.drag_release(self.plan_section, 50, 50, 680, 370)

    def data_confirm(self) -> None:
        if not self.properties.visible(self.data_confirmed_btn):
            self.module_view(self.module)

        send_keys_with_log("%r")
        self.actions.click(self.dc_voyage)
        send_keys_with_log("^a")
        send_keys_with_log(self.line, True)
        send_keys_with_log(self.vessel)
        send_keys_with_log(self.voyage)
        send_keys_with_log("%s")

        if not self.properties.visible(self.result_table):
            raise_with_log("Result table is not visible.")
        else:
            send_keys_with_log("%t")

        if wait_for_window("confirm"):
            send_keys_with_log("{ENTER}")
        else:
            raise_with_log("Confirm window not found")

if __name__ == '__main__':
    # python -m test_ui.flow.discharge_container
    dc = DischargeContainer()
    dc.data_confirm()
    dc.edit_add()
    dc.order_out_all()