import pytest
import pandas as pd
from unittest.mock import Mock
from test_ui.flow.gate_transaction import GateTransaction

@pytest.fixture
def gate_transaction(mocker):
    """Set up GateTransaction with minimal mocks."""
    mocker.patch("test_ui.base_flow.BaseDriver.__init__", return_value=None)
    gt = GateTransaction()
    gt.config = {
        "nGen": {"username": "test_user", "password": "test_pass"},
        "gt": {"search_tractor": "//tractor", "create_pin": "//pin", "create_driver": "//driver",
               "row0_cntr_id": "//row0", "inspection_seal": "//seal", "manual_confirm_btn": "//btn",
               "printer_id": "//printer"},
        "gate_settings": {"confirmation_code": "2000", "inspection_seal_value": "yfn", "printer_dummy": "dummy"}
    }
    gt.df = pd.DataFrame({"cntr_id": ["test000001"], "pin": [1234], "tractor": ["OXT01"]})
    gt.actions = Mock()
    gt.properties = Mock()
    gt.data_path = "data/test_data.csv"
    return gt

def test_get_tractor(gate_transaction, mocker):
    """Test get_tractor updates DataFrame."""
    gt = gate_transaction
    gt.df = pd.DataFrame({"cntr_id": ["test000001"]})  # No tractor
    mocker.patch("pandas.DataFrame.to_csv")
    gt.get_tractor()
    assert gt.df["tractor"].iloc[0] == "OXT01"
    gt.df.to_csv.assert_called()

def test_create_pickup(gate_transaction, mocker):
    """Test create_pickup clicks and sends keys."""
    gt = gate_transaction
    gt.properties.visible.return_value = True
    mocker.patch("helper.win_utils.wait_for_window", return_value=True)
    mocker.patch("helper.win_utils.send_keys_with_log")
    gt.create_pickup()
    gt.actions.click.assert_called_with("//tractor")
    helper.win_utils.send_keys_with_log.assert_called()

def test_confirm_pickup(gate_transaction, mocker):
    """Test confirm_pickup handles tractor loop."""
    gt = gate_transaction
    gt.properties.visible.return_value = True
    mocker.patch("helper.win_utils.wait_for_window", return_value=True)
    mocker.patch("helper.win_utils.send_keys_with_log")
    gt.confirm_pickup()
    gt.actions.click.assert_called_with("//tractor")
    helper.win_utils.send_keys_with_log.assert_called_with("2000")