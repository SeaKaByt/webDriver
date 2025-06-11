import pytest
import allure

from src.common.launcher import ApplicationLauncher

@pytest.mark.launcher
@allure.title("Application Launcher Workflow")
def test_workflow(video_recorder):
    initiate = True
    ngen = True
    guider = True

    a = ApplicationLauncher()

    if initiate:
        a.initiate_launcher()

    if ngen:
        a.login_ngen()

    if guider:
        a.login_guider()