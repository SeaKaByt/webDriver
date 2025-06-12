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
def test_workflow(backup_csv, video_recorder):
    # Backup only CSV files this test will modify
    backup_csv('gate_pickup', 'tractor_usage')
    
    create_container = True
    add_bol = False
    get_pin = False
    release_hold = False
    create_transaction = False

    count = 1
    movement = "gatePickup"
    status = "XF"
    size = "20"
    type = "G0"

    with BaseDriver() as d:
        c = ContainerDetails(d.driver)
        b = BolMaintenance(d.driver)
        cro = CROMaintenance(d.driver)
        h = HoldRelease(d.driver)
        g = GateTransaction(d.driver)

        if create_container:
            with allure.step(f"Create section"):
                c.create_cntr(count=count, movement=movement, status=status, size=size, type=type)

        if add_bol:
            with allure.step("Bill of Lading section"):
                b.add_containers()

        if get_pin:
            with allure.step("CRO section"):
                cro.cro_actions()

        if release_hold:
            with allure.step("Hold Release section"):
                h.release_hold("dt")

        if create_transaction:
            with allure.step("Gate Pickup section"):
                g.create_gate_pickup()