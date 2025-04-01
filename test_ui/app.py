import os

from helper.utils import get_match_windows, wait_for_window
from main import GetDriver
from pywinauto import Application
from dotenv import load_dotenv

load_dotenv()

class ApplicationLauncher(GetDriver):
    app = Application()

    security_alert_yes = "/form[@title='Security Alert']/button[@text='&Yes']"

    ngen = "/form[@title>'Application Launcher 1.3.']/container[@caption>'<html class=\" js csstransitions\"']//text[@accessiblename='nGen']"
    ngen_username = "/form[@title='Login']/container[@name='mainPanel']/?/?/text[@type='GuiTextField']"
    ngen_password = "/form[@title='Login']/container[@name='mainPanel']/?/?/text[@type='GuiPasswordField']"
    ngen_login_btn = "/form[@title='Login']/container[@name='mainPanel']/?/?/button[@name='okButton']"

    def __init__(self):
        super().__init__()
        self.username = self.config["nGen"]["username"]
        self.password = self.config["nGen"]["password"]

    def launch_application(self):
        app_path = self.config["nGen"]["jal_path"]
        self.app.start(app_path, timeout=5, wait_for_idle=False, work_dir=os.path.dirname(app_path))

    def login_ngen(self):
        if not get_match_windows("Application Launcher"):
            self.launch_application()
            wait_for_window("Security Alert")
            self.click(self.security_alert_yes)
        if not get_match_windows("Login"):
            self.click(self.ngen)
        wait_for_window("Login")
        self.click(self.ngen_username)
        self.send_keys(self.ngen_username, self.username)
        self.click(self.ngen_password)
        self.send_keys(self.ngen_password, self.password)
        self.click(self.ngen_login_btn)

    def test(self):
        print(get_match_windows("Login"))
        print(get_match_windows("Security Alert"))


if __name__ == '__main__':
    # python -m test_ui.app
    a = ApplicationLauncher()
    a.login_ngen()
    # a.test()