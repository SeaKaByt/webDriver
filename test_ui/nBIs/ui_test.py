from main import BaseDriver

class NibsUiTest(BaseDriver):
    login_btn = "/form[@title='Sprint']/container[@name>'NBISIV - ECT - Microsoft']//container[@classname='BrowserView']/container[@classname='SidebarContentsSplitView']/container[@classname='SidebarContentsSplitView']/container[@classname='SidebarContentsSplitView']/container[@classname='SidebarContentsSplitView']//container[@automationid='325002672']/text[@automationid='RootWebArea']/?/?/container[@automationid='kc-content']//container[@automationid='kc-form-wrapper']/container[@automationid='kc-form-login']/container[@automationid='kc-form-buttons']/?/?/button[@automationid='kc-login']"

    def __init__(self):
        super().__init__()

    def test_nbis_ui(self):
        self.click(self.login_btn)

if __name__ == '__main__':
    # python -m test_ui.nBIs.ui_test
    a = NibsUiTest()
    a.test_nbis_ui()
