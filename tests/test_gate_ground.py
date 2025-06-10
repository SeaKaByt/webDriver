import allure
import pytest

from src.core.driver import BaseDriver
from src.pages.ioc_maintenance.booking_maintenance import BookingMaintenance
from src.pages.gate_house.gate_transaction import GateTransaction
from helper.logger import logger

@pytest.mark.gate_ground
@allure.title("Gate Ground Workflow")
def test_gate_ground_workflow(video_recorder):
    return_cntr = True
    create_gate_ground = True

    # Create a single shared core session with proper cleanup
    with BaseDriver() as d:
        logger.info(f"Main driver session created: {d.driver.session_id if hasattr(d.driver, 'session_id') else 'Unknown'}")
        
        # Pass the driver instance directly, not just the driver attribute
        booking_flow = BookingMaintenance(d.driver)
        logger.info(f"BookingMaintenance driver session: {booking_flow.driver.session_id if hasattr(booking_flow.driver, 'session_id') else 'Unknown'}")
        
        gate_flow = GateTransaction(d.driver)
        logger.info(f"GateTransaction driver session: {gate_flow.driver.session_id if hasattr(gate_flow.driver, 'session_id') else 'Unknown'}")

        if return_cntr:
            with allure.step("Booking section"):
                booking_flow.add_return_cntr()

        if create_gate_ground:
            with allure.step("Gate Ground section"):
                gate_flow.create_gate_ground()


