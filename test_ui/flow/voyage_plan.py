import argparse
import time
from pathlib import Path
from helper.logger import logger
from helper.io_utils import read_csv
from helper.sys_utils import raise_with_log
from helper.win_utils import send_keys_with_log, wait_for_window
from test_ui.base_flow import BaseFlow

class Voyage(BaseFlow):
    def __init__(self):
        super().__init__()
        guider_config = self.config["guider"]
        self.title = guider_config["title"]
        self.window_1 = guider_config["window_1"]
        self.window_2 = guider_config["window_2"]
        self.window_2_penal = guider_config["window_2_penal"]
        self.voyage_plan_btn = guider_config["voyage_plan_btn"]
        self.voyage_plan_voyage = guider_config["voyage_plan_voyage"]
        self.open_module_btn = guider_config["open_module_btn"]

        voyage_config = self.config["voyage"]
        self.voyage_bay = voyage_config["voyage_bay"]
        self.voyage_tree_qc = voyage_config["voyage_tree_qc"]
        self.plan_section = voyage_config["plan_section"]
        self.filter = voyage_config["filter"]
        self.filter_cntr_id = voyage_config["filter_cntr_id"]
        self.search_list_btn = voyage_config["search_list_btn"]
        self.work_plan_add_btn = voyage_config["work_plan_add_btn"]
        self.voyage_qc = voyage_config["voyage_qc"]
        self.mask_view = voyage_config["mask_view"]
        self.minimize_mask_view = voyage_config["minimize_mask_view"]
        self.list_row_cntr = voyage_config["list_row_cntr"]
        self.list_row_planned = voyage_config["list_row_planned"]
        self.option_list = voyage_config["option_list"]

    def order_out_all(self):
        self.actions.right_click(self.voyage_tree_qc)
        for _ in range(5):
            send_keys_with_log("{VK_DOWN}")
        send_keys_with_log("{VK_RIGHT}")
        send_keys_with_log("{ENTER}")

    def set_display_scale(self):
        self.actions.right_click(self.plan_section)
        for _ in range(2):
            send_keys_with_log("{VK_DOWN}")
        send_keys_with_log("{ENTER}")
        send_keys_with_log("^a")
        send_keys_with_log("65")
        send_keys_with_log("{ENTER}")

    def drag_release(self):
        self.actions.click(self.work_plan_add_btn)
        self.actions.drag_release(self.plan_section, 50, 50, 680, 370)

    def open_voyage_plan(self):
        self.actions.click(self.title)
        self.actions.click(self.voyage_plan_btn)
        if wait_for_window("Open Voyage Plan"):
            self.actions.click(self.voyage_plan_voyage)
            send_keys_with_log(f"{self.full_voyage}")
            send_keys_with_log("{ENTER}")
            self.actions.click(self.open_module_btn)
        else:
            raise_with_log("Open Voyage Plan window not found")

    @staticmethod
    def next_bay(size: int, bay: str) -> str | None:
        logger.info(f"size: {size}, bay: {bay}")
        bay_number = int(bay[:2])
        bay_suffix = bay[2]

        if size == 20:
            if bay_number % 2 == 0:
                bay_number += 1
            else:
                bay_number += 2
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
            raise_with_log(f"Invalid size: {size}")

        if bay_number > 78:
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
            raise_with_log(f"Container ID {cntr_id} not found in DataFrame")

    @staticmethod
    def update_planned(df, cntr_id):
        mask = df["cntr_id"] == cntr_id
        if mask.any():
            df.loc[mask, "planned"] = "Yes"
        else:
            raise_with_log(f"Container ID {cntr_id} not found in DataFrame")

    def setup_voyage(self, bay):
        self.setup_bay(bay)
        self.actions.click(self.voyage_qc)
        send_keys_with_log("^a")
        send_keys_with_log(self.qc)
        send_keys_with_log("{ENTER}")
        self.drag_release()

    def setup_bay(self, bay):
        self.actions.click(self.voyage_bay)
        send_keys_with_log("^a")
        send_keys_with_log(bay)
        send_keys_with_log("{ENTER}")

    def check_mask_view(self):
        element = self.actions.find(self.mask_view)
        size = element.size
        if size['height'] > 500:
            self.actions.click(self.minimize_mask_view)
            logger.info("Mask view minimized")

    def _add_cntr(self):
        path = Path("data/vessel_loading_data.csv")
        df = read_csv(path)

        if not wait_for_window("Voyage", timeout=1):
            self.open_voyage_plan()
            time.sleep(10)
        self.set_display_scale()
        self.check_mask_view()
        self.actions.click(self.search_list_btn)

        grouped = df.groupby("bay")

        for bay, group in grouped:
            logger.info(f"Processing bay: {bay}")
            self.setup_bay(bay)
            self.drag_release()

            cntr_ids = group["cntr_id"].tolist()
            self.place_cntr_in_bay(df, bay, cntr_ids)

        df.to_csv(path, index=False)

    def place_cntr_in_bay(self, df, bay, cntr_ids):
        for cntr_id in cntr_ids:
            cntr_id_xpath = self.list_row_cntr.rsplit("cell", 1)[0] + f"cell[@text='{cntr_id}']"

            if not self.actions.find(cntr_id_xpath):
                self.update_planned(df, cntr_id)
                continue

            self.actions.click(cntr_id_xpath)
            if wait_for_window(".*(gdr2303|gdr1239)$", 1):
                send_keys_with_log("{ENTER}")

            if not self.actions.find(cntr_id_xpath, timeout=1):
                self.update_planned(df, cntr_id)
            else:
                size = df[df["cntr_id"] == cntr_id]["size"].iloc[0]
                new_bay = self.next_bay(int(size), bay)
                if new_bay is None:
                    raise_with_log(f"No space available for cntr_id: {cntr_id}")
                self.update_bay(df, cntr_id, new_bay)
                logger.info(f"Moved {cntr_id} to bay {new_bay}")
                self.setup_bay(new_bay)
                self.drag_release()

            self.actions.click(cntr_id_xpath)
            if wait_for_window(".*(gdr2303|gdr1239)$", 1):
                send_keys_with_log("{ENTER}")

            if self.actions.find(cntr_id_xpath, 1):
                raise_with_log(f"Container {cntr_id} still in table after second attempt")
            else:
                self.update_planned(df, cntr_id)

if __name__ == "__main__":
    v = Voyage()
    v._add_cntr()
    v.order_out_all()