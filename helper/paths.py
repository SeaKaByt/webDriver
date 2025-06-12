from pathlib import Path
from helper.io_utils import read_csv

class ProjectPaths:
    ROOT = Path(__file__).resolve().parent.parent
    DATA = ROOT / "data"
    CONFIG = ROOT / "config" 
    LOGS = ROOT / "tests" / "test-results" / "logs"
    RESPONSES = ROOT / "tests" / "test-results" / "responses"

    @staticmethod
    def _get_csv_data(filename: str):
        """Helper method to get CSV data."""
        p = ProjectPaths.DATA / filename
        df = read_csv(p)
        return df, p

    @staticmethod
    def get_loading_data():
        df, p = ProjectPaths._get_csv_data("cntr_data.csv")
        yield df, p

    @staticmethod
    def get_discharge_data():
        df, p = ProjectPaths._get_csv_data("vessel_discharge_data.csv")
        yield df, p
        
    @staticmethod
    def get_gate_pickup_data():
        df, p = ProjectPaths._get_csv_data("gate_pickup_data.csv")
        yield df, p

    @staticmethod
    def get_gate_ground_data():
        df, p = ProjectPaths._get_csv_data("gate_ground_data.csv")
        yield df, p

    @staticmethod
    def get_tractor_usage_data():
        df, p = ProjectPaths._get_csv_data("tractor_usage.csv")
        yield df, p

    @staticmethod
    def get_stowage_usage():
        df, p = ProjectPaths._get_csv_data("stowage_usage.csv")
        yield df, p

    @staticmethod
    def get_tractor_card_data():
        df, p = ProjectPaths._get_csv_data("tractor_usage.csv")
        yield df, p
    
