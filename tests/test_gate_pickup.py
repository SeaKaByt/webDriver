import allure
import pytest

from src.core.driver import BaseDriver
from src.pages.ioc_maintenance.bol_maintenance import BolMaintenance
from src.pages.inventory_operation.container_details import ContainerDetails
from src.pages.ioc_maintenance.cro_maintenance import CROMaintenance
from src.pages.gate_house.gate_transaction import GateTransaction
from src.pages.inventory_operation.hold_release import HoldRelease

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

    # Parameters
    count = 2
    movement = "gatePickup"

    with BaseDriver() as d:
        # Initialize pages components - they'll all share the same core instance
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