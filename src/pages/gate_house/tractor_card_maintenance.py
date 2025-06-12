import csv
import os

from helper.paths import ProjectPaths
from helper.win_utils import sendkeys, focus_window
from src.common.menu import Menu
from src.core.driver import BaseDriver

class TractorCard(BaseDriver):
    MODULE = "TC"

    def __init__(self):
        super().__init__()
        self.d = self.config["tractor_card"]["detail"]
        
        _, self.path = next(ProjectPaths.get_tractor_card_data())

    def save_to_csv(self, tractor_ids: list) -> None:
        """Save generated tractor IDs to CSV file without overriding existing data"""
        # Read existing data
        existing_data = []
        header = ["tractor_id", "reserved", "problem"]
        
        if os.path.exists(self.path):
            with open(self.path, 'r', newline='') as file:
                reader = csv.reader(file)
                existing_data = list(reader)
                if existing_data:
                    header = existing_data[0]  # Use existing header
                    existing_data = existing_data[1:]  # Remove header from data
        
        # Create new records for generated tractor IDs
        new_records = []
        for tractor_id in tractor_ids:
            new_records.append([tractor_id, "", ""])  # Default: reserved=Y, problem=empty
        
        # Combine new records (at the beginning) with existing data
        all_data = new_records + existing_data
        
        # Write back to CSV
        with open(self.path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)  # Write header
            writer.writerows(all_data)  # Write all data

    def create_tractor_card(self, numeric: int, count: int) -> None:
        if count < 1:
            raise ValueError("Count must be at least 1")

        focus_window("nGen")
        
        generated_tractor_ids = []

        if not self.properties.visible(self.d["tractor"]):
            Menu.to_module(self.MODULE, self)

        for i in range(count):
            sendkeys("%a")
            self.actions.click(self.d["tractor"])
            sendkeys("^a")
            tractor = f"XT{str(numeric + i).zfill(3)}"
            generated_tractor_ids.append(tractor)
            sendkeys(tractor, with_tab=True)
            sendkeys(tractor, with_tab=True)
            sendkeys(tractor)
            sendkeys("{ENTER}")
        
        # Save generated tractor IDs to CSV
        self.save_to_csv(generated_tractor_ids)
        print(f"Saved {len(generated_tractor_ids)} tractor IDs to {self.path}")

if __name__ == "__main__":
    t = TractorCard()
    t.create_tractor_card(61, 20)