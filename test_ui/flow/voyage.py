import argparse
import time
from pathlib import Path
from helper.logger import logger
from helper.io_utils import read_csv
from helper.win_utils import send_keys_wlog, wait_for_window, focus_window, find_window
from test_ui.flow_config import BaseFlow

class Voyage(BaseFlow):
    def __init__(self, external_driver=None):
        super().__init__(external_driver=external_driver)
        focus_window("Guider")
        self.guider = self.config["guider"]
        self.vp = self.guider["voyage_plan"]
        self.voyage = self.guider["voyage"]
        self.filter = self.voyage["filter"]
        self.list = self.voyage["list"]
        self.mask = self.voyage["mask_view"]


    def order_out_all(self):
        self.actions.right_click(self.voyage["qc_tree"])
        for _ in range(5):
            send_keys_wlog("{VK_DOWN}")
        send_keys_wlog("{VK_RIGHT}")
        send_keys_wlog("{ENTER}")
        time.sleep(0.5)
        if find_window("Order-Out"):
            logger.error("Order-Out window appeared unexpectedly")
            raise

    def set_display_scale(self):
        self.actions.right_click(self.voyage["plan_section"])
        for _ in range(2):
            send_keys_wlog("{VK_DOWN}")
        send_keys_wlog("{ENTER}")
        send_keys_wlog("^a")
        send_keys_wlog("65")
        send_keys_wlog("{ENTER}")

    def panel_drag_release(self, function: str):
        self.actions.click(self.voyage[function])
        self.actions.drag_release(self.voyage["plan_section"], 50, 50, 680, 370)

    def open_voyage_plan(self):
        if not find_window("Voyage"):
            self.actions.click(self.vp["open_plan"])
            if wait_for_window("Open Voyage Plan"):
                self.actions.click(self.vp["voyage"])
                send_keys_wlog(f"{self.full_voyage}")
                send_keys_wlog("{ENTER}")
                self.actions.click(self.vp["open"])
            else:
                raise Exception("Open Voyage Plan window not found")

    @staticmethod
    def next_bay(size: int, bay: str) -> str | None:
        logger.info(f"size: {size}, bay: {bay}")
        bay_number = int(bay[:2])
        bay_suffix = bay[2]
        maximum_bay = 75

        if size == 20:
            bay_number += 2 if bay_number % 2 == 0 else 1
        elif size == 40:
            if bay_number % 4 == 0:
                bay_number += 2
            elif bay_number % 4 == 1:
                bay_number += 1
            elif bay_number % 4 == 3:
                bay_number += 3
            else:
                bay_number += 4
        else:
            raise ValueError(f"Invalid size: {size}")

        if bay_number > maximum_bay:
            return None

        new_bay = f"{bay_number:02d}{bay_suffix}"
        logger.info(f"New bay: {new_bay}")
        return new_bay

    @staticmethod
    def update_bay(df, cntr_id, new_bay):
        mask = df["cntr_id"] == cntr_id
        if mask.any():
            df.loc[mask, "bay"] = new_bay
        else:
            raise ValueError(f"Container ID {cntr_id} not found in DataFrame")

    @staticmethod
    def update_planned(df, cntr_id):
        mask = df["cntr_id"] == cntr_id
        if mask.any():
            df.loc[mask, "planned"] = "Yes"
        else:
            raise ValueError(f"Container ID {cntr_id} not found in DataFrame")

    def setup_bay(self, bay):
        self.actions.click(self.voyage["bay"])
        send_keys_wlog("^a")
        send_keys_wlog(bay)
        send_keys_wlog("{ENTER}")

    def check_mask_view(self):
        element = self.actions.find(self.mask["view"])
        if element.size['height'] > 500:
            self.actions.click(self.mask["minimize"])
            logger.info("Mask view minimized")

    def setup_qc(self):
        self.actions.click(self.voyage["qc"])
        send_keys_wlog("^a")
        send_keys_wlog(self.qc)
        send_keys_wlog("{ENTER}")

    def add_cntr(self) -> None:
        p = Path("data/vessel_loading_data.csv")
        df = read_csv(p)

        if not wait_for_window("Voyage", timeout=1):
            self.open_voyage_plan()
            time.sleep(10)

        self.check_mask_view()
        self.actions.click(self.voyage["option_list"])
        self.actions.click(self.voyage["refresh"])
        self.set_display_scale()
        self.setup_qc()

        if self.properties.item_text(self.voyage["qc_methods"]) == "Disc":
            self.actions.click(self.voyage["qc_methods"])

        if self.properties.item_text(self.voyage["qc_methods"]) != "Load":
            raise ValueError("QC method is not Load")

        self.actions.click(self.voyage["search_list"])

        for bay, group in df.groupby("bay"):
            logger.info(f"Processing bay: {bay}")
            self.setup_bay(bay)
            self.panel_drag_release("work_plan_add")
            self.place_cntr_in_bay(df, bay, group["cntr_id"].tolist())

        df.to_csv(p, index=False)

    def place_cntr_in_bay(self, df, bay, cntr_ids):
        for cntr_id in cntr_ids:
            cntr_id_xpath = self.voyage["list_row_cntr"].rsplit("cell", 1)[0] + f"cell[@text='{cntr_id}']"
            if not self.actions.find(cntr_id_xpath):
                self.update_planned(df, cntr_id)
                continue

            self.actions.click(cntr_id_xpath)
            if wait_for_window(".*(gdr2303|gdr1239)$", 1):
                send_keys_wlog("{ENTER}")

            if wait_for_window("Host Error", 1):
                raise Exception("Host Error window appeared")

            if not self.actions.find(cntr_id_xpath, timeout=1):
                self.update_planned(df, cntr_id)
            else:
                size = df[df["cntr_id"] == cntr_id]["size"].iloc[0]
                new_bay = self.next_bay(int(size), bay)
                if new_bay is None:
                    raise Exception(f"No space available for cntr_id: {cntr_id}")
                self.update_bay(df, cntr_id, new_bay)
                logger.info(f"Moved {cntr_id} to bay {new_bay}")
                self.setup_bay(new_bay)
                self.panel_drag_release("work_plan_add")
                self.actions.click(cntr_id_xpath)
                if wait_for_window(".*(gdr2303|gdr1239)$", 1):
                    send_keys_wlog("{ENTER}")

                if self.actions.find(cntr_id_xpath, 1):
                    raise Exception(f"Container {cntr_id} still in table after second attempt")
                else:
                    self.update_planned(df, cntr_id)

    def plan_cntr(self, target_count: int, bay_list: list[str], df, p: Path):
        times = 1
        limit = 3

        if not self.properties.visible(self.list["row_0"]):
            raise Exception("No container in the list")

        hold = True
        for bay in bay_list:
            if times >= limit:
                raise Exception("Abnormal loop count")

            count = self.properties.text_value(self.list["count"])
            logger.info(count)

            self.setup_bay(bay)
            if target_count == 1:
                self.panel_drag_release("work_plan_add")
                self.actions.click(self.list["row_0"])
            else:
                logger.info(target_count)
                self.work_plan_add(target_count)

            if hold:
                time.sleep(0.5)
                if find_window(".*-gdr2303"):
                    send_keys_wlog("{ENTER}")
                else:
                    hold = False

            current_count = self.properties.text_value(self.list["count"])
            target_count = target_count + int(current_count) - int(count)

            if target_count > 0:
                df.loc[df["bay"] == bay, "capacity"] = "F"
                df.to_csv(p, index=False)
            else:
                df.loc[df["bay"] == bay, "capacity"] = "A"
                df.to_csv(p, index=False)
                logger.info("All containers placed")
                return

            times += 1

    def work_plan_add(self, count: int):
        self.actions.click(self.list["row_0"])
        self.panel_drag_release("work_plan_add")
        focus_window(".*Mode  :  1$")
        for _ in range(count - 1):
            send_keys_wlog("+{DOWN}")
        self.actions.right_click(self.list["row_0"])

    @staticmethod
    def get_20_bay(df) -> list[str]:
        df_filtered = df[(df["reserved_size"] == 40) & (df["capacity"] != "F")]
        df_filtered = df_filtered["group"].tolist()
        df_filtered = df[(df["reserved_size"] == 20) & (df["capacity"] != "F") & (df["group"].isin(df_filtered))]

        return df_filtered["bay"].tolist()

    @staticmethod
    def get_40_bay(df) -> list[str]:
        df_filtered = df[(df["reserved_size"] == 20) & (df["capacity"] == "F")]
        df_filtered = df_filtered["group"].unique().tolist()
        df_filtered = df[(df["reserved_size"] == 40) & (df["capacity"] != "F") & (~df["group"].isin(df_filtered))]

        return df_filtered["bay"].tolist()

    @staticmethod
    def get_stowage_usage():
        p = Path("data/stowage_usage.csv")
        df = read_csv(p)
        yield df, p

    def setup_voyage(self, mode: str):
        focus_window(".*Mode  :  1$")
        self.check_mask_view()
        self.actions.click(self.voyage["refresh"])
        self.set_display_scale()
        self.setup_qc()

        if self.properties.item_text(self.voyage["mode"]) != mode:
            self.actions.click(self.voyage["mode"])

    def session_1(self, size_20_count: int, size_40_count: int, df, p):
        groups = [
            {"count": size_20_count, "size": "20", "bay_list": self.get_20_bay(df)},
            {"count": size_40_count, "size": "40", "bay_list": self.get_40_bay(df)}
        ]

        for group in groups:
            if group["count"] > 0:
                focus_window(".*Mode  :  2$")
                self.actions.click(self.filter["tag"])
                self.actions.click(self.voyage["reset"])
                self.actions.click(self.filter["size"])
                send_keys_wlog(group["size"])
                self.actions.click(self.list["search_list"])
                self.plan_cntr(group["count"], group["bay_list"], df, p)

    def voyage_loading_actions(self, size_20_count: int, size_40_count: int):
        df, p = next(self.get_stowage_usage())

        self.open_voyage_plan()
        self.setup_voyage("Load")
        self.session_1(size_20_count, size_40_count, df, p)
        self.order_out_all()

def main():
    v = Voyage()
    focus_window(".*Mode  :  2$")

if __name__ == "__main__":
    main()