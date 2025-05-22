from helper.win_utils import send_keys_with_log
from test_ui.base_flow import BaseFlow


class TractorCard(BaseFlow):
    module = "TC"

    def __init__(self):
        super().__init__()
        self.detail_config = self.config["tractor_card"]["detail"]


    def create_tractor_card(self, numeric: int, count: int) -> None:
        self.actions.click(self.title)

        for i in range(count):
            send_keys_with_log("%a")
            self.actions.click(self.detail_config["tractor"])
            send_keys_with_log("^a")
            tractor = f"XT{str(numeric + i).zfill(3)}"
            send_keys_with_log(tractor, with_tab=True)
            send_keys_with_log(tractor, with_tab=True)
            send_keys_with_log(tractor)
            send_keys_with_log("{ENTER}")


if __name__ == "__main__":
    t = TractorCard()
    t.create_tractor_card(9, 12)


