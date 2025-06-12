import allure
import pytest

from src.core.driver import BaseDriver
from src.pages.inventory_operation.container_details import ContainerDetails
from src.pages.guider.cwp_plan import CWP
from src.pages.inventory_operation.hold_release import HoldRelease
from src.pages.guider.voyage import Voyage


@pytest.mark.vessel_loading
@allure.title("Vessel Loading Workflow")
def test_workflow(video_recorder):
    create_containers = False
    release_hold = False
    voyage_loading = True
    release_cwp = True

    count = 1
    status = "XF"
    size = "20"
    type = "G0"
    movement = "loading"

    size_20 = 2
    size_40 = 2

    with BaseDriver() as d:
        c = ContainerDetails(d.driver)
        h = HoldRelease(d.driver)
        v = Voyage(d.driver)
        cwp = CWP(d.driver)

        if create_containers:
            with allure.step(f"Create section"):
                c.create_cntr(count=count, movement=movement, status=status, size=size, type=type)

        if release_hold:
            with allure.step("Hold Release section"):
                h.release_hold("vm")

        if voyage_loading:
            with allure.step(f"Voyage Loading section"):
                v.voyage_loading_actions(size_20, size_40)

        if release_cwp:
            with allure.step("CWP section"):
                cwp.release_cwp()