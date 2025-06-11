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
def test_workflow(video_recorder):
    create_container = False
    add_bol = False
    get_pin = False
    release_hold = False
    create_transaction = True

    count = 2
    movement = "gatePickup"

    with BaseDriver() as d:
        c = ContainerDetails(d.driver)
        b = BolMaintenance(d.driver)
        cro = CROMaintenance(d.driver)
        h = HoldRelease(d.driver)
        g = GateTransaction(d.driver)

        if create_container:
            with allure.step(f"Create {count} containers for gate pickup"):
                c.create_cntr(count=count, movement=movement)

        if add_bol:
            with allure.step("Add containers to Bill of Lading"):
                b.add_containers()

        if get_pin:
            with allure.step("Create CRO and obtain PIN"):
                cro.cro_actions()

        if release_hold:
            with allure.step("Release DT hold"):
                h.release_hold("dt")

        if create_transaction:
            with allure.step("Create gate pickup transaction"):
                g.create_gate_pickup()