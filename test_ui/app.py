import os

from helper.utils import get_match_windows, wait_for_window, send_keys_tab
from main import BaseDriver
from pywinauto import Application
from pywinauto.keyboard import send_keys
from dotenv import load_dotenv

load_dotenv()

class ApplicationLauncher(BaseDriver):
    app = Application()

    # security_alert_yes = "/form[@title='Security Alert']/button[@text='&Yes']"

    # ngen = "/form[@title>'Application Launcher 1.3.']/container[@caption>'<html class=\" js csstransitions\"']//text[@accessiblename='nGen']"
    # ngen_username = "/form[@title='Login']/container[@name='mainPanel']/?/?/text[@type='GuiTextField']"
    # ngen_password = "/form[@title='Login']/container[@name='mainPanel']/?/?/text[@type='GuiPasswordField']"
    # ngen_login_btn = "/form[@title='Login']/container[@name='mainPanel']/?/?/button[@name='okButton']"

    def __init__(self):
        super().__init__()
        self.username = self.config["nGen"]["username"]
        self.password = self.config["nGen"]["password"]
        self.app_ngen = self.config["app"]["ngen"]
        self.app_guider = self.config['app']['guider']

    def launch_application(self):
        app_path = self.config["nGen"]["jal_path"]
        self.app.start(app_path, timeout=5, wait_for_idle=False, work_dir=os.path.dirname(app_path))

    # def login_ngen(self):
    #     if not get_match_windows("Application Launcher"):
    #         self.launch_application()
    #         wait_for_window("Security Alert")
    #         self.click(self.security_alert_yes)
    #     if not get_match_windows("Login"):
    #         self.click(self.ngen)
    #     wait_for_window("Login")
    #     self.click(self.ngen_username)
    #     send_keys(self.username)
    #     self.click(self.ngen_password)
    #     send_keys(self.password)
    #     self.click(self.ngen_login_btn)

    def fat_login_ngen(self):
        if not get_match_windows("Application Launcher"):
            self.launch_application()
            wait_for_window("Application Launcher")
        if not get_match_windows("Login"):
            self.click(self.app_ngen)
        wait_for_window("Login")
        send_keys_tab(self.username)
        send_keys(self.password)
        send_keys("{ENTER}")

    def login_guider(self):
        if not get_match_windows("Application Launcher"):
            self.launch_application()
            wait_for_window("Application Launcher")
        if not get_match_windows("Guider Logon"):
            self.click(self.app_guider)
        wait_for_window("Guider Logon")
        send_keys_tab(self.username)
        send_keys(self.password)
        send_keys("{ENTER}")

    def full_load(self):
        self.fat_login_ngen()
        wait_for_window('nGen')
        self.login_guider()

    def test(self):
        pass

if __name__ == '__main__':
    # python -m test_ui.app
    a = ApplicationLauncher()
    a.full_load()
