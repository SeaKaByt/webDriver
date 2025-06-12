import time
import pandas as pd
import allure

from pathlib import Path
from helper.logger import logger
from helper.win_utils import sendkeys, wait_for_window, find_window, focus_window
from src.core.driver import BaseDriver
from src.common.menu import Menu

class BookingMaintenance(BaseDriver):
    MODULE = "BM"

    def __init__(self, external_driver=None):
        super().__init__(external_driver=external_driver)
        self.bk = self.config["booking"]
        self.ld = self.bk["laden"]

        self.line = "NVD"
        self.booking_list = ["BK01", "BK02", "BK04"]
        self.booking_map = {"XF": "BK01", "EM": "BK02", "XM": "BK04"}  # Status to booking mapping

    def add_return_cntr(self, df, p) -> None:
        """Main entry point for adding return containers."""
        focus_window("nGen")

        df_filtered = self.validate_df(df, p)
        if df_filtered.empty:
            logger.info("No data to process, skipping booking maintenance")
            return
        
        if not self.properties.visible(self.bk["line"]):
            Menu.to_module(self.MODULE, self)

        # Process each status group
        for status, group in df_filtered.groupby("status"):
            logger.info(f"Processing status group: {status}")
            allure.attach(f"Starting processing for Status: {status} ({len(group)} containers)", 
                         name=f"📋 Status Group: {status}", 
                         attachment_type=allure.attachment_type.TEXT)
            self._process_status_group(status, group, df, p)

    def _process_status_group(self, status: str, group, df, p) -> None:
        """Process a single status group."""
        # Initialize booking for this status
        self.actions.click(self.bk["line"])
        sendkeys("^a")
        sendkeys(self.line, with_tab=True)
        booking_no = self.booking_map[status]  # Will raise KeyError for unknown status
        sendkeys(booking_no)
        sendkeys("{ENTER}")
        sendkeys("%b")

        if not wait_for_window("Booking Request"):
            logger.error("Booking Request window not found")
            raise RuntimeError("Booking Request window not found")

        # Process each size subgroup within this status
        for size, subgroup in group.groupby("size"):
            logger.info(f"Processing Status: {status}, Size: {size}, Subgroup size: {len(subgroup)}")
            container_list = subgroup["cntr_id"].tolist()
            allure.attach(f"Processing {len(subgroup)} containers of size {size}ft:\n" + 
                         "\n".join(f"- {cntr}" for cntr in container_list), 
                         name=f"📦 {status} Size {size}ft Batch", 
                         attachment_type=allure.attachment_type.TEXT)
            self._process_size_subgroup(status, size, subgroup, booking_no, df)
        
        # Save and close only after ALL sizes for this status are processed
        df.to_csv(p, index=False)
        self.actions.click(self.bk["close"])
        allure.attach(f"✅ Status {status} completed successfully with booking: {booking_no}", 
                     name=f"🎯 {status} Completed", 
                     attachment_type=allure.attachment_type.TEXT)

    def _process_size_subgroup(self, status: str, size: str, subgroup, booking_no: str, df) -> None:
        """Process containers for a specific status/size combination."""
        # Select appropriate request sequence
        request_sequence = self._get_request_sequence(status, size)
        self._select_request_sequence(request_sequence, status, size)
        
        # Open return window and prepare for container entry
        self._open_return_window(status, size)
        
        # Process each container in the subgroup
        self._process_containers(subgroup, booking_no, df)
        
        # Save and close the return window
        self._save_and_close_return()

    def _get_request_sequence(self, status: str, size: str):
        """Get the appropriate request sequence for status/size combination."""
        sequence_map = {
            ("XF", "20"): self.bk["request_sequence_3004"],
            ("XF", "40"): self.bk["request_sequence_3005"],
            ("EM", "20"): self.bk["request_sequence_2843"],
            ("EM", "40"): self.bk["request_sequence_2882"],
            ("XM", "20"): self.bk["request_sequence_3006"],
            ("XM", "40"): self.bk["request_sequence_3007"],
        }
        request_sequence = sequence_map.get((status, str(size)))
        if request_sequence is None:
            raise ValueError(f"Invalid status/size combination: {status}/{size}")
        return request_sequence

    def _select_request_sequence(self, request_sequence, status: str, size: str) -> None:
        """Select the request sequence with retry logic."""
        self.actions.click(request_sequence)
        if not self.properties.selected(request_sequence):
            # Try double-click if single click failed
            self.actions.click(request_sequence)
            if not self.properties.selected(request_sequence):
                raise RuntimeError(f"Failed to select request_sequence for status: {status}, size: {size}")

    def _open_return_window(self, status: str, size: str) -> None:
        """Open and prepare the return window."""
        self.actions.click(self.bk["return"])
        time.sleep(0.5)
        if not find_window("Laden Return"):
            logger.error(f"Laden Return window not found for status: {status}, size: {size}")
            raise RuntimeError(f"Laden Return window not found for status: {status}, size: {size}")

        self.actions.click(self.ld["row"])
        self.actions.click(self.ld["copy"])

        if not self.properties.visible(self.ld["new_cntr"], 1):
            logger.error("New Container field not found")
            raise RuntimeError("New Container field not found")

    def _process_containers(self, subgroup, booking_no: str, df) -> None:
        """Process individual containers in the subgroup."""
        for _, row in subgroup.iterrows():
            logger.info(f"Processing row: {row}")
            self._enter_container(row["cntr_id"])
            self._handle_user_errors()
        
        # Update original df with booking number
        df.loc[subgroup.index, "bk_no"] = booking_no

    def _enter_container(self, cntr_id: str) -> None:
        """Enter a single container ID."""
        self.actions.click(self.ld["new_cntr"])
        sendkeys("^a")
        sendkeys(cntr_id)
        if self.properties.text_value(self.ld["new_cntr"]) != cntr_id:
            logger.error(f"Container {cntr_id} not found")
            allure.attach(f"❌ Failed to enter container: {cntr_id}", 
                         name="🚫 Container Entry Failed", 
                         attachment_type=allure.attachment_type.TEXT)
            raise ValueError(f"Container {cntr_id} not entered correctly")

        self.actions.click(self.ld["add_next"])
        time.sleep(0.5)
        allure.attach(f"✅ Container {cntr_id} entered successfully", 
                     name="📋 Container Added", 
                     attachment_type=allure.attachment_type.TEXT)

    def _handle_user_errors(self) -> None:
        """Handle user error dialogs during container entry."""
        if find_window("User Error"):
            logger.info("User Error window is found")
            sendkeys("{ENTER}")

    def _save_and_close_return(self) -> None:
        """Save the return data and close the window."""
        self.actions.click(self.ld["cancel"])
        self.actions.click(self.ld["save"])

        if wait_for_window("Confirm"):
            sendkeys("{TAB}")
            sendkeys("{ENTER}")
            allure.attach("Batch saved successfully - Confirm dialog handled", 
                         name="💾 Batch Save Confirmed", 
                         attachment_type=allure.attachment_type.TEXT)
        else:
            logger.error("Confirm window not found")
            raise RuntimeError("Confirm window not found")

        if wait_for_window(".*ioc5643$", 1):
            logger.info("ioc5643 window found")
            sendkeys("{ENTER}")

        if find_window("User Error"):
            logger.error("User Error window is found")
            raise

        self.actions.click(self.ld["close"])

    def validate_df(self, df: pd.DataFrame, p: Path) -> pd.DataFrame:
        """Validate and prepare DataFrame for processing.
        
        Updates original CSV file if needed, returns filtered data for processing.
        """
        # Update twin_ind NA values to 'S' for rows where mvt != 'C'
        condition = (df["mvt"] != "C") & (df["twin_ind"].isna())
        if condition.any():
            logger.warning("Some 'twin_ind' values are NaN, filling with 'S'")
            logger.info(f"Found {condition.sum()} rows with NA twin_ind values where mvt != 'C'")
            
            # Direct pandas update - much simpler and faster
            df.loc[condition, "twin_ind"] = "S"
            
            # Save with automatic backup
            df.to_csv(p, index=False)
        
        # Filter and clean data for processing
        df_filtered = df[df["mvt"] != "C"]
        
        # Only process containers without booking numbers
        if "bk_no" not in df_filtered.columns:
            df_filtered["bk_no"] = None
        df_filtered = df_filtered[df_filtered["bk_no"].isna()]
        
        if df_filtered.empty:
            logger.warning("No data to process after filtering (all rows have mvt='C')")
            return df_filtered
        
        if df_filtered["status"].isna().any() or df_filtered["size"].isna().any():
            raise ValueError("DataFrame contains NA values in 'status' or 'size' columns")
        
        df_filtered["status"] = df_filtered["status"].astype(str).str.strip()
        df_filtered["size"] = df_filtered["size"].astype('int64')
        
        return df_filtered