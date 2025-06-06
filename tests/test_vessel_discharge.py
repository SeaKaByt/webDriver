import allure
import pytest

from driver.base_driver import BaseDriver
from test_ui.flow.bay_plan import BayPlan
from test_ui.flow.cwp_plan import CWP
from test_ui.flow.discharge_container import DischargeContainer
from test_ui.flow.hold_release import HoldRelease
from test_ui.flow.jms_messaging import JMSMessaging

@pytest.mark.vessel_discharge
@allure.title("Vessel Discharge Workflow")
@allure.description("Complete vessel discharge workflow with optional steps")
@allure.feature("Vessel Operations")
@allure.story("Vessel Discharge Process")
def test_vessel_discharge_workflow(video_recorder):
    """Clean vessel discharge workflow with step controls"""

    # Step configuration
    send_bay_plan_message = False
    upload_bay_plan = False
    release_hold = False
    data_confirm = False
    vessel_discharge = True
    release_cwp = True

    with BaseDriver() as d:
        # Initialize flow components
        jms_flow = JMSMessaging()
        bay_plan_flow = BayPlan(d.driver)
        hold_flow = HoldRelease(d.driver)
        discharge_flow = DischargeContainer(d.driver)
        cwp_flow = CWP(d.driver)

        # Execute workflow steps
        if send_bay_plan_message:
            with allure.step("Send bay plan message to JMS queue"):
                jms_flow.send_bay_plan_message()

        if upload_bay_plan:
            with allure.step("Upload bay plan to system"):
                bay_plan_flow.upload_bay_plan()

        if release_hold:
            with allure.step("Release hold"):
                hold_flow.release_hold("cc", "hp")

        if data_confirm:
            with allure.step("Confirm bay plan data"):
                discharge_flow.data_confirm()

        if vessel_discharge:
            with allure.step("Execute voyage discharge actions"):
                discharge_flow.actions_chains()

        if release_cwp:
            with allure.step("Release Container Work Plan"):
                cwp_flow.release_cwp()