import allure
import pytest

from driver.base_driver import BaseDriver
from test_ui.flow.bay_plan import BayPlan
from test_ui.flow.cwp_plan import CWP
from test_ui.flow.discharge_container import DischargeContainer
from test_ui.flow.hold_release import HoldRelease


@pytest.mark.vessel_discharge
@allure.title("Vessel Discharge Workflow")
@allure.description("Complete vessel discharge workflow with optional steps")
@allure.feature("Vessel Operations")
@allure.story("Vessel Discharge Process")
def test_vessel_discharge_workflow(video_recorder):
    """Clean vessel discharge workflow with step controls"""

    # Step configuration
    upload_bay_plan = False
    release_hold = False
    vessel_discharge = True
    release_cwp = False

    with BaseDriver() as d:
        # Initialize flow components
        bay_plan_flow = BayPlan(d.driver)
        hold_flow = HoldRelease(d.driver)
        discharge_flow = DischargeContainer(d.driver)
        cwp_flow = CWP(d.driver)

        # Execute workflow steps
        if upload_bay_plan:
            with allure.step("Upload bay plan to system"):
                bay_plan_flow.upload_bay_plan()

        if release_hold:
            with allure.step("Release CC hold"):
                hold_flow.release_hold("cc", "hp")

        if vessel_discharge:
            with allure.step("Execute voyage discharge actions"):
                discharge_flow.voyage_discharge_actions()

        if release_cwp:
            with allure.step("Release Container Work Plan"):
                cwp_flow.release_cwp()