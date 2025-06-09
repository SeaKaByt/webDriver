from pathlib import Path
from helper.io_utils import read_csv

class ProjectPaths:
    ROOT = Path(__file__).resolve().parent.parent
    DATA = ROOT / "data"
    CONFIG = ROOT / "config"

    @staticmethod
    def get_loading_data():
        p = ProjectPaths.DATA / "container_data.csv"
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

