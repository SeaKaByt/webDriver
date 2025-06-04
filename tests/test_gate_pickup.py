import allure
import pytest

from driver.base_driver import BaseDriver
from test_ui.flow.bol_maintenance import BolMaintenance
from test_ui.flow.container_details import ContainerDetails
from test_ui.flow.cro_maintenance import CROMaintenance
from test_ui.flow.gate_transaction import GateTransaction
from test_ui.flow.hold_release import HoldRelease

@pytest.mark.gate_pickup
@allure.title("Gate Pickup Workflow")
@allure.description("Complete gate pickup workflow with step control")
@allure.feature("Gate Operations")
@allure.story("Gate Pickup Process")
def test_gate_pickup_workflow(video_recorder):
    """Clean gate pickup workflow with boolean step controls"""

    # Step configuration - easily enable/disable steps
    create_container = False
    add_bol = False
    get_pin = False
    release_hold = False
    create_transaction = True
    release_mvt = True

    # Parameters
    count = 2
    movement = "gatePickup"

    with BaseDriver() as d:
        # Initialize flow components - they'll all share the same driver instance
        container_flow = ContainerDetails(d.driver)
        bol_flow = BolMaintenance(d.driver)
        cro_flow = CROMaintenance(d.driver)
        hold_flow = HoldRelease(d.driver)
        gate_flow = GateTransaction(d.driver)

        # Execute workflow steps
        if create_container:
            with allure.step(f"Create {count} containers for gate pickup"):
                container_flow.create_cntr(count=count, movement=movement)

        if add_bol:
            with allure.step("Add containers to Bill of Lading"):
                bol_flow.add_containers()

        if get_pin:
            with allure.step("Create CRO and obtain PIN"):
                cro_flow.cro_actions()

        if release_hold:
            with allure.step("Release DT hold"):
                hold_flow.release_hold("dt")

        if create_transaction:
            with allure.step("Create gate pickup transaction"):
                gate_flow.create_gate_pickup()