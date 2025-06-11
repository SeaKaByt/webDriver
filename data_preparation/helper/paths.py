from pathlib import Path
from helper.io_utils import read_csv

class ProjectPaths:
    ROOT = Path(__file__).resolve().parent.parent
    DATA = ROOT / "data"
    CONFIG = ROOT / "config"
    LOGS = ROOT / "tests" / "test-results" / "logs"
    RESPONSES = ROOT / "tests" / "test-results" / "responses"

    @staticmethod
    def get_loading_data():
        p = ProjectPaths.DATA / "cntr_data.csv"
        df = read_csv(p)
        yield df, p

    @staticmethod
    def get_discharge_data():
        p = ProjectPaths.DATA / "vessel_discharge_data.csv"
        df = read_csv(p)
        yield df, p
        
    @staticmethod
    def get_gate_pickup_data():
        p = ProjectPaths.DATA / "gate_pickup_data.csv"
        df = read_csv(p)
        yield df, p

    @staticmethod
    def get_gate_ground_data():
        p = ProjectPaths.DATA / "gate_ground_data.csv"
        df = read_csv(p)
        yield df, p

    @staticmethod
    def get_tractor_usage_data():
        p = ProjectPaths.DATA / "tractor_usage.csv"
        df = read_csv(p)
        yield df, p

    @staticmethod
    def get_stowage_usage():
        p = ProjectPaths.DATA / "stowage_usage.csv"
        df = read_csv(p)
        yield df, p

    @staticmethod
    def get_tractor_card_data():
        p = ProjectPaths.DATA / "tractor_card_data.csv"
        df = read_csv(p)
        yield df, p