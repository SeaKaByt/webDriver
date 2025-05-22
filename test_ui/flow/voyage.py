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
        self.guider_config = self.config["guider"]
        self.voyage_config = self.config["voyage"]
        self.filter_config = self.config["voyage"]["filter"]
        self.list_config = self.config["voyage"]["list"]
        self.mask_view_config = self.config["voyage"]["mask_view"]

    def order_out_all(self):
        self.actions.right_click(self.voyage_config["qc_tree"])
        for _ in range(5):
            send_keys_with_log("{VK_DOWN}")
        send_keys_with_log("{VK_RIGHT}")
        send_keys_with_log("{ENTER}")

    def set_display_scale(self):
        self.actions.right_click(self.voyage_config["plan_section"])
        for _ in range(2):
            send_keys_with_log("{VK_DOWN}")
        send_keys_with_log("{ENTER}")
        send_keys_with_log("^a")
        send_keys_with_log("65")
        send_keys_with_log("{ENTER}")

    def panel_drag_release(self, function: str):
        self.actions.click(self.voyage_config[function])
        self.actions.drag_release(self.voyage_config["plan_section"], 50, 50, 680, 370)

    def open_voyage_plan(self):
        if not wait_for_window("Voyage", 1):
            self.actions.click(self.guider_config["title"])
            self.actions.click(self.guider_config["voyage_plan_btn"])
            if wait_for_window("Open Voyage Plan"):
                self.actions.click(self.guider_config["voyage_plan_voyage"])
                send_keys_with_log(f"{self.full_voyage}")
                send_keys_with_log("{ENTER}")
                self.actions.click(self.guider_config["open_module_btn"])
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
            raise_with_log(f"Invalid size: {size}")

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
            raise_with_log(f"Container ID {cntr_id} not found in DataFrame")

    @staticmethod
    def update_planned(df, cntr_id):
        mask = df["cntr_id"] == cntr_id
        if mask.any():
            df.loc[mask, "planned"] = "Yes"
        else:
            raise ValueError(f"Container ID {cntr_id} not found in DataFrame")

    def setup_bay(self, bay):
        self.actions.click(self.voyage_config["bay"])
        send_keys_with_log("^a")
        send_keys_with_log(bay)
        send_keys_with_log("{ENTER}")

    def check_mask_view(self):
        element = self.actions.find(self.mask_view_config["view"])
        if element.size['height'] > 500:
            self.actions.click(self.mask_view_config["minimize"])
            logger.info("Mask view minimized")

    def setup_qc(self):
        self.actions.click(self.voyage_config["qc"])
        send_keys_with_log("^a")
        send_keys_with_log(self.qc)
        send_keys_with_log("{ENTER}")

    def add_cntr(self) -> None:
        p = Path("data/vessel_loading_data.csv")
        df = read_csv(p)

        if not wait_for_window("Voyage", timeout=1):
            self.open_voyage_plan()
            time.sleep(10)

        self.check_mask_view()
        self.actions.click(self.voyage_config["option_list"])
        self.actions.click(self.voyage_config["refresh"])
        self.set_display_scale()
        self.setup_qc()

        if self.properties.item_text(self.voyage_config["qc_methods"]) == "Disc":
            self.actions.click(self.voyage_config["qc_methods"])

        if self.properties.item_text(self.voyage_config["qc_methods"]) != "Load":
            raise ValueError("QC method is not Load")

        self.actions.click(self.voyage_config["search_list"])

        for bay, group in df.groupby("bay"):
            logger.info(f"Processing bay: {bay}")
            self.setup_bay(bay)
            self.panel_drag_release("work_plan_add")
            self.place_cntr_in_bay(df, bay, group["cntr_id"].tolist())

        df.to_csv(p, index=False)

    def place_cntr_in_bay(self, df, bay, cntr_ids):
        for cntr_id in cntr_ids:
            cntr_id_xpath = self.voyage_config["list_row_cntr"].rsplit("cell", 1)[0] + f"cell[@text='{cntr_id}']"
            if not self.actions.find(cntr_id_xpath):
                self.update_planned(df, cntr_id)
                continue

            self.actions.click(cntr_id_xpath)
            if wait_for_window(".*(gdr2303|gdr1239)$", 1):
                send_keys_with_log("{ENTER}")

            if wait_for_window("Host Error", 1):
                raise_with_log("Host Error window appeared")

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
                self.panel_drag_release("work_plan_add")
                self.actions.click(cntr_id_xpath)
                if wait_for_window(".*(gdr2303|gdr1239)$", 1):
                    send_keys_with_log("{ENTER}")

                if self.actions.find(cntr_id_xpath, 1):
                    raise_with_log(f"Container {cntr_id} still in table after second attempt")
                else:
                    self.update_planned(df, cntr_id)

    def plan_cntr(self, target_count: int, bay_list: list[str], df, p: Path):
        times = 1
        limit = 3

        if not self.properties.visible(self.list_config["row_0"]):
            raise Exception("No container in the list")

        for bay in bay_list:
            if times >= limit:
                raise Exception("Abnormal loop count")

            count = self.properties.text_value(self.list_config["count"])
            logger.info(count)

            self.setup_bay(bay)
            if target_count == 1:
                self.panel_drag_release("work_plan_add")
                self.actions.click(self.list_config["row_0"])
            else:
                logger.info(target_count)
                self.work_plan_add(target_count)

            current_count = self.properties.text_value(self.list_config["count"])
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
        self.actions.click(self.list_config["row_0"])
        self.panel_drag_release("work_plan_add")
        self.actions.click(self.voyage_config["mode_2"])
        for _ in range(count - 1):
            send_keys_with_log("+{DOWN}")
        self.actions.right_click(self.list_config["row_0"])

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

    def setup_voyage(self, unexpected_method: str, target_method: str):
        self.check_mask_view()
        self.actions.click(self.voyage_config["refresh"])
        self.set_display_scale()
        self.setup_qc()

        if self.properties.item_text(self.voyage_config["qc_methods"]) == unexpected_method:
            self.actions.click(self.voyage_config["qc_methods"])

        if self.properties.item_text(self.voyage_config["qc_methods"]) != target_method:
            raise ValueError("QC method is not Load")

    def session_1(self, size_20_count: int, size_40_count: int, df, p):
        groups = [
            {"count": size_20_count, "size": "20", "bay_list": self.get_20_bay(df)},
            {"count": size_40_count, "size": "40", "bay_list": self.get_40_bay(df)}
        ]

        for group in groups:
            if group["count"] > 0:
                self.actions.click(self.filter_config["tag"])
                self.actions.click(self.voyage_config["reset"])
                self.actions.click(self.filter_config["size"])
                send_keys_with_log(group["size"])
                self.actions.click(self.voyage_config["search_list"])
                self.plan_cntr(group["count"], group["bay_list"], df, p)

    def voyage_loading_actions(self, size_20_count: int, size_40_count: int):
        df, p = next(self.get_stowage_usage())

        self.open_voyage_plan()
        self.setup_voyage("Disc", "Load")
        self.session_1(size_20_count, size_40_count, df, p)
        self.order_out_all()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Voyage management")
    parser.add_argument("size_20_count", type=int, nargs="?", default=0, help="Number of 20 size containers")
    parser.add_argument("size_40_count", type=int, nargs="?", default=0, help="Number of 40 size containers")
    args = parser.parse_args()

    v = Voyage()
    v.voyage_loading_actions(args.size_20_count, args.size_40_count)