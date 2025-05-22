import argparse
from pandas.errors import EmptyDataError
from test_ui.base_flow import BaseFlow
from helper.win_utils import wait_for_window, send_keys_with_log
from helper.logger import logger

class BolMaintenance(BaseFlow):
    module = "BOL"

    def __init__(self):
        super().__init__()
        self.bol_config = self.config["bol"]

    def bol_actions(self):
        df, p = next(self.get_gate_pickup_data())
        self.add_cntr(df, p)

    def search_bol(self) -> None:
        logger.info(f"Searching BOL: {self.bol}")
        self.actions.click(self.bol_config["line"])
        send_keys_with_log("^a")
        send_keys_with_log(self.line, with_tab=True)
        send_keys_with_log(self.bol)
        send_keys_with_log("{ENTER}")

    def create_bol(self) -> None:
        if not self.properties.visible(self.bol_config["line"], timeout=1):
            logger.info("Opening BOL module")
            self.module_view(self.module)
        self.search_bol()
        if wait_for_window("User Error ioc5618", timeout=1):
            logger.info("Handling User Error ioc5618")
            send_keys_with_log("{ENTER}")
            send_keys_with_log("%a")
            if not self.properties.editable(self.bol_config["details_line"]):
                logger.error("details_line not editable")
                raise RuntimeError("BOL creation failed: details_line not editable")
            send_keys_with_log(self.line, with_tab=True)
            send_keys_with_log(self.bol, with_tab=True)
            send_keys_with_log(self.line, with_tab=True)
            send_keys_with_log(self.vessel)
            send_keys_with_log(self.voyage, with_tab=True)
            for _ in range(3):
                send_keys_with_log("{TAB}")
            send_keys_with_log("{ENTER}")

    def add_cntr(self, df, p) -> None:
        if not self.properties.visible(self.bol_config["add_cntr_btn"], timeout=1):
            logger.info("Opening BOL module")
            self.module_view(self.module)

        self.search_bol()
        self.actions.click(self.bol_config["add_cntr_btn"])
        if not wait_for_window("Create Bill of lading container", timeout=5):
            raise RuntimeError("Create Bill of lading container window not found")

        df_filtered = df[df["bol"].isna() & df["cntr_id"].notna()]
        if df_filtered.empty:
            raise EmptyDataError("No containers without BOL were found")

        for cntr_id in df_filtered["cntr_id"]:
            logger.info(f"Adding container: {cntr_id}")
            self.actions.click(self.bol_config["create_cntr_id"])
            send_keys_with_log(cntr_id)
            self.actions.click(self.bol_config["add_next"])
            if not wait_for_window("Confirm", timeout=5):
                logger.error("Confirm window not found")
                raise RuntimeError("Confirm window not found")
            self.actions.click(self.bol_config["confirm_yes"])
            if wait_for_window(".*ioc4665$", timeout=1):
                logger.warning("Container under bill of lading")
                send_keys_with_log("{ENTER}")
            self.update_column(df, cntr_id, "bol", self.bol)
            df.to_csv(p, index=False)
        self.actions.click(self.bol_config["create_cancel"])

    @staticmethod
    def update_column(df, cntr_id, column: str, value) -> None:
        mask = df["cntr_id"] == cntr_id
        if mask.any():
            df.loc[mask, column] = value
            logger.info(f"Updated {column} for {cntr_id} to {value}")
        else:
            raise Exception(f"Cannot update {column} for {cntr_id}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BOL Maintenance Automation")
    parser.add_argument("method", choices=["create_bol", "add_cntr"], help="Method to execute (create_bol or add_cntr)")
    args = parser.parse_args()

    try:
        bol = BolMaintenance()
        if args.method == "create_bol":
            bol.create_bol()
        elif args.method == "add_cntr":
            bol.bol_actions()
    except Exception as e:
        raise Exception(f"BolMaintenance failed: {e}")