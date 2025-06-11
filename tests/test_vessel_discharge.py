import allure
import pytest

from src.core.driver import BaseDriver
from src.pages.ship_plan.edi_bay_plan import BayPlan
from src.pages.guider.cwp_plan import CWP
from src.pages.ship_plan.discharge_container import DischargeContainer
from src.pages.inventory_operation.hold_release import HoldRelease
from helper.JMS.baplie import Baplie

@pytest.mark.vessel_discharge
@allure.title("Vessel Discharge Workflow")
def test_workflow(video_recorder):
    send_bay_plan_message = False
    upload_bay_plan = False
    release_hold = False
    data_confirm = False
    vessel_discharge = True
    release_cwp = True

    with BaseDriver() as d:
        jms = Baplie()
        bay_plan = BayPlan(d.driver)
        hold = HoldRelease(d.driver)
        discharge = DischargeContainer(d.driver)
        cwp = CWP(d.driver)

        if send_bay_plan_message:
            with allure.step("Send bay plan message to JMS queue"):
                jms.send_bay_plan_message()

        if upload_bay_plan:
            with allure.step("Upload bay plan to system"):
                bay_plan.upload_bay_plan()

        if release_hold:
            with allure.step("Release hold"):
                hold.release_hold("cc", "hp")

        if data_confirm:
            with allure.step("Confirm bay plan data"):
                discharge.data_confirm()

        if vessel_discharge:
            with allure.step("Execute voyage discharge actions"):
                discharge.actions_chains()

        if release_cwp:
            with allure.step("Release Container Work Plan"):
                cwp.release_cwp()