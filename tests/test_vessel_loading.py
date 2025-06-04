import allure
import pytest

from driver.base_driver import BaseDriver
from test_ui.flow.container_details import ContainerDetails
from test_ui.flow.cwp_plan import CWP
from test_ui.flow.hold_release import HoldRelease
from test_ui.flow.voyage import Voyage


@pytest.mark.vessel_loading
@allure.title("Vessel Loading Workflow")
@allure.description("Complete vessel loading workflow with configurable steps")
@allure.feature("Vessel Operations")
@allure.story("Vessel Loading Process")
def test_vessel_loading_workflow(video_recorder):
    """Clean vessel loading workflow with step controls"""

    # Step configuration
    create_containers = False
    release_hold = False
    voyage_loading = True
    release_cwp = False

    # Parameters
    count = 2
    size_20 = 1
    size_40 = 1
    movement = "loading"

    with BaseDriver() as d:
        # Initialize flow components
        container_flow = ContainerDetails(d.driver)
        hold_flow = HoldRelease(d.driver)
        voyage_flow = Voyage(d.driver)
        cwp_flow = CWP(d.driver)

        # Execute workflow steps
        if create_containers:
            with allure.step(f"Create {count} containers for vessel loading"):
                container_flow.create_cntr(count=count, movement=movement)

        if release_hold:
            with allure.step("Release VM hold for vessel operations"):
                hold_flow.release_hold("vm")

        if voyage_loading:
            with allure.step(f"Execute voyage loading: {size_20} x 20ft, {size_40} x 40ft"):
                voyage_flow.voyage_loading_actions(size_20, size_40)

        if release_cwp:
            with allure.step("Release Container Work Plan"):
                cwp_flow.release_cwp()