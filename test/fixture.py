import pandas as pd
import pytest
from pathlib import Path
from helper.io_utils import read_csv
from test_ui.flow.container_details import ContainerDetails
from test_ui.flow.gate_transaction import GateTransaction
from test_ui.flow.voyage_plan import Voyage

path = Path("data/test.csv")

@pytest.fixture
def gate_transaction_data():
    df = pd.DataFrame({"twin_ind": ["T", "T", "S", "T", "T", "S"]})
    p = Path("data/test.csv")
    yield df, p

@pytest.fixture
def voyage_plan_data():
    df = pd.DataFrame({"cntr_id":["TEST000127", "TEST000128", "TEST000125"]})
    p = Path("data/test.csv")
    yield df, p

@pytest.fixture
def temp_csv():
    df = pd.DataFrame({
        "cntr_id": ["TEST000127", "TEST000128", "TEST000125"],
        "bay": ["01D", "02D", "03D"],
        "size": ["20", "40", "20"],
        "status": ["XF", "XF", "XF"],
    })
    yield df, path

def test_get_tractor(gate_transaction_data):
    # python -m pytest test/fixture.py::test_get_tractor -v
    df, p = gate_transaction_data

    GateTransaction().get_tractor(df, p)

    expected = ["XT001", "XT001", "XT003", "XT002", "XT002", "XT004"]
    assert df["tractor"].tolist() == expected, f"Expected {expected}, got {df['tractor'].tolist()}"
    assert p.exists()
    saved_df = read_csv(p)
    assert saved_df["tractor"].tolist() == expected

def test_next_bay():
    # python -m pytest test/fixture.py::test_next_bay -v
    v = Voyage()

    assert v.next_bay(20, "02D") == "03D"
    assert v.next_bay(20, "04D") == "05D"
    assert v.next_bay(20, "06D") == "07D"
    assert v.next_bay(20, "76D") == "77D"  # Near limit

    assert v.next_bay(40, "04D") == "06D"
    assert v.next_bay(40, "05D") == "06D"
    assert v.next_bay(40, "07D") == "10D"
    assert v.next_bay(40, "75D") == "78D"  # Near limit

    # Test invalid size
    with pytest.raises(Exception):
        v.next_bay(30, "01D")
    # Test bay number exceeding limit
    with pytest.raises(Exception):
        v.next_bay(20, "78D")
    with pytest.raises(Exception):
        v.next_bay(40, "79D")

def test_update_bay(temp_csv):
    # python -m pytest test/fixture.py::test_update_bay -v
    v = Voyage()

    df, p = temp_csv
    df.to_csv(p)

    # Test updating bay
    v.update_bay(p, "TEST000125", "05D")
    updated_df = read_csv(p)
    assert updated_df.loc[updated_df["cntr_id"] == "TEST000125", "bay"].values[0] == "05D"
    # assert updated_df.loc[updated_df["cntr_id"] == "TEST000128", "bay"].values[0] == "04D"
    # assert updated_df.loc[updated_df["cntr_id"] == "TEST000125", "bay"].values[0] == "05D"

def test_yard_container(temp_csv):
    # python -m pytest test/fixture.py::test_yard_container -v
    c = ContainerDetails

    df, path = temp_csv

    new_data = [
        {"cntr_id": "TEST000129", "status": "XF", "size": 40, "twin_ind": "N"},
        {"cntr_id": "TEST000127", "status": "XF", "size": 20, "twin_ind": "Y"}  # Duplicate cntr_id
    ]

    c.save_as_csv(new_data, df, path)

