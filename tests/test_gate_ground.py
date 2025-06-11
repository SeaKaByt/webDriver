import allure
import pytest

from src.core.driver import BaseDriver
from src.pages.ioc_maintenance.booking_maintenance import BookingMaintenance
from src.pages.gate_house.gate_transaction import GateTransaction

@pytest.mark.gate_ground
@allure.title("Gate Ground Workflow")
def test_workflow(video_recorder):
    return_cntr = True
    create_gate_ground = True

    with BaseDriver() as d:
        b = BookingMaintenance(d.driver)
        g = GateTransaction(d.driver)
        
        if return_cntr:
            with allure.step("Booking section"):
                b.add_return_cntr()
        
        if create_gate_ground:
            with allure.step("Gate Ground section"):
                g.create_gate_ground()