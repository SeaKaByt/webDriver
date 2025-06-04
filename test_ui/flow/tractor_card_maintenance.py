from helper.win_utils import send_keys_wlog
from test_ui.flow_config import BaseFlow
import csv
import os


class TractorCard(BaseFlow):
    module = "TC"

    def __init__(self):
        super().__init__()
        self.detail_config = self.config["tractor_card"]["detail"]
        self.csv_file_path = "data/tractor_usage.csv"

    def save_to_csv(self, tractor_ids: list) -> None:
        """Save generated tractor IDs to CSV file without overriding existing data"""
        # Read existing data
        existing_data = []
        header = ["tractor_id", "reserved", "problem"]
        
        if os.path.exists(self.csv_file_path):
            with open(self.csv_file_path, 'r', newline='') as file:
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
        with open(self.csv_file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)  # Write header
            writer.writerows(all_data)  # Write all data

    def create_tractor_card(self, numeric: int, count: int) -> None:
        if count < 1:
            raise ValueError("Count must be at least 1")

        self.actions.click(self.title)
        
        generated_tractor_ids = []

        for i in range(count):
            send_keys_wlog("%a")
            self.actions.click(self.detail_config["tractor"])
            send_keys_wlog("^a")
            tractor = f"XT{str(numeric + i).zfill(3)}"
            generated_tractor_ids.append(tractor)
            send_keys_wlog(tractor, with_tab=True)
            send_keys_wlog(tractor, with_tab=True)
            send_keys_wlog(tractor)
            send_keys_wlog("{ENTER}")
        
        # Save generated tractor IDs to CSV
        self.save_to_csv(generated_tractor_ids)
        print(f"Saved {len(generated_tractor_ids)} tractor IDs to {self.csv_file_path}")


if __name__ == "__main__":
    t = TractorCard()
    t.create_tractor_card(49, 11)

# python -m test_ui.flow.tractor_card_maintenance
