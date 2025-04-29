import pandas as pd
import pytest
from pathlib import Path
from helper.io_utils import read_csv
from test_ui.flow.gate_transaction import GateTransaction

@pytest.fixture
def gate_transaction_data():
    df = pd.DataFrame({"twin_ind": ["T", "T", "S", "T", "T", "S"]})
    path = Path("data/test.csv")
    yield df, path

def test_get_tractor(gate_transaction_data):
    # python -m pytest tests/test_gate_transaction.py::test_get_tractor -v
    df, path = gate_transaction_data

    GateTransaction()._get_tractor(df, path)

    expected = ["XT001", "XT001", "XT003", "XT002", "XT002", "XT004"]
    assert df["tractor"].tolist() == expected, f"Expected {expected}, got {df['tractor'].tolist()}"
    assert path.exists()
    saved_df = read_csv(path)
    assert saved_df["tractor"].tolist() == expected


