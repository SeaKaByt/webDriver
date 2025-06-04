import allure
import pytest

from driver.base_driver import BaseDriver
from test_ui.flow.booking_maintenance import BookingMaintenance
from test_ui.flow.gate_transaction import GateTransaction

@pytest.mark.gate_ground
@allure.title("Gate Ground Workflow")
def test_gate_ground_workflow(video_recorder):
    return_cntr = False
    create_gate_ground = True

    # Create a single shared driver session
    with BaseDriver() as d:
        booking_flow = BookingMaintenance(d.driver)
        gate_flow = GateTransaction(d.driver)

        if return_cntr:
            with allure.step("Booking section"):
                booking_flow.add_return_cntr()

        if create_gate_ground:
            with allure.step("Gate Ground section"):
                gate_flow.create_gate_ground()


