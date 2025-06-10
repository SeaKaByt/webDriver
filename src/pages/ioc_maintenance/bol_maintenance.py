import pandas as pd

from src.core.driver import BaseDriver
from src.common.menu import Menu
from helper.win_utils import wait_for_window, sendkeys
from helper.logger import logger
from helper.paths import ProjectPaths

class BolMaintenance(BaseDriver):
    """Handles Bill of Lading (BOL) creation and container addition in a UI-based logistics application."""
    MODULE = "BOL"

    def __init__(self, external_driver=None):
        """Initialize with configuration and validate attributes."""
        super().__init__(external_driver=external_driver)
        self.bol_config = self.config["bol"]
        self.add_cntr_config = self.bol_config["add_cntr"]

        self.line = "NVD"
        self.vessel = "TSHM04"
        self.voyage = "V01"
        self.bol = "BL01"

    def create_bol(self) -> None:
        """Create a new Bill of Lading in the UI."""
        self._search_bol()
        self._handle_bol_creation()

    def add_containers(self) -> None:
        """Add containers to a BOL in the UI and update the DataFrame."""
        if not self.properties.visible(self.bol_config["line"], timeout=1):
            logger.info("Opening BOL module")
            Menu.to_module(self.MODULE, self)

        df, path = next(ProjectPaths.get_gate_pickup_data())

        df_filtered = df[df["bol"].isna() & df["cntr_id"].notna()]
        if df_filtered.empty:
            logger.warning("No containers without BOL found; cancelling operation")
            return

        if not self.properties.visible(self.bol_config["create_cntr_id"], timeout=1):
            self._search_bol()

        logger.info("Starting container addition process")
        self.actions.click(self.bol_config["add_cntr_btn"])

        if not wait_for_window("Create Bill of lading container", timeout=self.bol_config.get("window_timeout", 5)):
            raise RuntimeError("Create Bill of lading container window not found")

        for idx, cntr_id in enumerate(df_filtered["cntr_id"]):
            logger.info(f"Adding container {idx + 1}/{len(df_filtered)}: {cntr_id}")
            self._add_container(cntr_id, is_last=(idx == len(df_filtered) - 1))
            self._update_container_bol(df, cntr_id, self.bol)

        df.to_csv(path, index=False)
        if wait_for_window("Amend Bill", 1):
            self.actions.click(self.bol_config["create_cancel"])
        logger.info("Completed container addition process")

    def _search_bol(self) -> None:
        """Search for a BOL in the UI."""
        logger.info(f"Searching BOL: {self.bol}")
        self._send_keys_sequence([
            (self.bol_config["line"], "^a"),
            ("", self.line, True),
            ("", self.bol),
            ("", "{ENTER}")
        ])

    def _handle_bol_creation(self) -> None:
        """Handle BOL creation with error handling."""
        if wait_for_window(self.bol_config.get("error_window", "User Error ioc5618"), timeout=1):
            logger.info("Handling User Error ioc5618")
            self._send_keys_sequence([("{ENTER}",), ("%a",)])

            if not self.properties.editable(self.bol_config["details_line"]):
                logger.error("details_line not editable")
                raise RuntimeError("BOL creation failed: details_line not editable")

        self._set_bol_details()

    def _set_bol_details(self) -> None:
        """Set BOL details in the UI."""
        self._send_keys_sequence([
            (self.bol_config["details_line"], self.line, True),
            (self.bol_config["details_line"], self.bol, True),
            (self.bol_config["details_line"], self.line, True),
            (self.bol_config["details_line"], self.vessel),
            (self.bol_config["details_line"], self.voyage, True),
            (self.bol_config["details_line"], "{TAB}", False, 3),
            (self.bol_config["details_line"], "{ENTER}")
        ])

    def _add_container(self, cntr_id: str, is_last: bool = False) -> None:
        """Add a container to the BOL in the UI."""
        self.actions.click(self.add_cntr_config["cntr_id"])
        sendkeys(cntr_id)
        if is_last:
            self.actions.click(self.add_cntr_config["ok"])
        else:
            self.actions.click(self.add_cntr_config["add_next"])

        if not wait_for_window("Confirm", timeout=self.bol_config.get("window_timeout", 5)):
            logger.error("Confirm window not found")
            raise RuntimeError("Confirm window not found")

        self.actions.click(self.bol_config["confirm_yes"])

        if wait_for_window(self.bol_config.get("container_error", ".*ioc4665$"), timeout=1):
            logger.warning("Container under bill of lading")
            sendkeys("{ENTER}")

    def _send_keys_sequence(self, sequence: list[tuple]) -> None:
        """Send a sequence of keys to the UI.

        Args:
            sequence: List of tuples (element, value, with_tab, repeat).
        """
        for step in sequence:
            element = step[0] if len(step) > 1 else None
            value = step[1] if len(step) > 1 else step[0]
            with_tab = step[2] if len(step) > 2 else False
            repeat = step[3] if len(step) > 3 else 1

            if element:
                self.actions.click(element)
            for _ in range(repeat):
                sendkeys(value, with_tab=with_tab)

    def _update_container_bol(self, df: pd.DataFrame, cntr_id: str, bol: str) -> None:
        """Update the BOL column for a container in the DataFrame."""
        mask = df["cntr_id"] == cntr_id
        if mask.any():
            df.loc[mask, "bol"] = bol
            logger.info(f"Updated BOL for {cntr_id} to {bol}")
        else:
            raise ValueError(f"Container ID {cntr_id} not found in DataFrame")