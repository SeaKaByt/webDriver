from pathlib import Path

class ProjectPaths:
    ROOT = Path(__file__).resolve().parent.parent
    CONFIG = ROOT / "config"
    DATA = ROOT / "data"
    LOGS = ROOT / "logs"

    @staticmethod
    def get_yaml_path(env: str, bu: str) -> Path:
        return ProjectPaths.CONFIG / env / f"{bu}.yaml"

    @staticmethod
    def get_json_data_path() -> Path:
        return ProjectPaths.DATA / "data.json"

    @staticmethod
    def get_excel_data_path(file_name: str = "data.csv") -> Path:
        return ProjectPaths.DATA / file_name

