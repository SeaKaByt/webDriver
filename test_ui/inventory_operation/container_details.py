import time

from pywinauto.keyboard import send_keys
from main import GetDriver
from helper.utils import send_keys_tab, update_yaml
from helper.function_shortcut import enter_to_function_view

class ContainerDetails(GetDriver):
    function = "Container Details"

    # Define the common base path
    common_path = "/form[@title>'nGen IUT-SAPT - 14.7.0-M87-SNAPSHOT']/container[@type='GuiPanel']/container[@type='GuiPanel']"
    discharge_path = f"{common_path}//container[@name='tabContainerPanel']/container[@name='tabbedPanel']/container[@name='dischargePanel']/container[@name='dischargeScrollPane']"

    # Common Details
    iv_cntr_id = f"{common_path}//combobox[@name='cntrNoComboBox']/text[@name='cntrNoEditField']"
    iv_status = f"{common_path}//combobox[@name='statusComboBox']/text[@type='GuiAlloyComboBoxUI$PrivateTextField']"
    iv_size = f"{common_path}//container[@name='sizeTypePanel']/text[@name='sizeTextField']"
    iv_type = f"{common_path}//container[@name='sizeTypePanel']/text[@name='typeTextField']"
    iv_owner = f"{common_path}//container[@name='ownerPanel']/text[@name='ownerTextField']"
    iv_region = f"{common_path}//container[@name='ownerPanel']/text[@name='regionTextField']"
    iv_yard_loc = f"{common_path}//container[@name='headerPanel']//element[@name='cntrLocationComboBox']/combobox[@name='guiComboBox1']/text[@type='GuiAlloyComboBoxUI$PrivateTextField']"
    iv_material = f"{common_path}//combobox[@name='materialComboBox']/text[@type='GuiAlloyComboBoxUI$PrivateTextField']"
    iv_max_gross_wt = f"{common_path}//container[@name='headerPanel']/container[@name='headFieldsPanel']/container[@name='commonDetailPanel']//text[@name='maxGrWtTextField']"

    # Extent for IF Container
    iv_voyage = f"{discharge_path}//container[@name='topPanel']/container[@name='voyagePanel']/text[@name='voyageIdTextField']"
    iv_pol = f"{discharge_path}//container[@name='portPanel']/text[@name='polTextField']"
    iv_gross_wt = f"{discharge_path}//container[@name='gwPanel']/text[@name='grWtTextField']"

    create_ok = f"{common_path}//container[@name='headButtonPanel']/container[@name='headOkCancelButtonPanel']/button[@name='amendOkButton']"
    cancel = f"{common_path}//container[@name='headButtonPanel']/container[@name='headOkCancelButtonPanel']/button[@name='amendCancelButton']"

    # Confirmation Dialog
    create_container_yes = "/form[@title='Create Container']//container[@name='OptionPane.buttonArea']/button[@text='Yes']"
    invalid_container_id_yes = "/form[@title='Confirm']//container[@name='OptionPane.buttonArea']/button[@text='Yes']"
    gem = "/form[@title='Choices']//container[@name='OptionPane.buttonArea']/button[@text='General EM']"

    # Function path
    inventory = "/form[@title>'nGen IUT-SAPT - 14.7.0-M8']/container[@type='GuiPanel']//body/?/?/table/tr[3]/td[2]/tag[@tagname='p-implied']"
    inventory_operation = f"{common_path}//container[@name='buttonPanel']/text[@caption='F2 - Inventory Operation']"
    container_details = f"{common_path}//container[@name='buttonPanel']/text[@caption='F1 - Container Details']"
    function_view = f"{common_path}//container[@name='headerPanel']/container[@name='commonDetailPanel']/container[@name='commonDetailView']"

    def __init__(self):
        super().__init__()
        self.cntr_id = self.config["container"]["cntr_id"]
        self.status = self.config["container"]["status"]
        self.size = self.config["container"]["size"]
        self.type = self.config["container"]["type"]
        self.owner = self.config["container"]["owner"]
        self.block = self.config["container"]["location"]["block"]
        self.stack = self.config["container"]["location"]["stack"]
        self.lane = self.config["container"]["location"]["lane"]
        self.material = self.config["container"]["material"]
        self.max_gross_wt = self.config["container"]["max_gross_wt"]
        self.line = self.config["container"]["line"]
        self.vessel = self.config["container"]["vessel"]
        self.voyage = self.config["container"]["voyage"]
        self.POL = self.config["container"]["POL"]
        self.gross_wt = self.config["container"]["gross_wt"]
        self.test_field = self.config["test"]["value"]

    def common_details(self, status = None):
        self.click(self.iv_cntr_id)
        send_keys('^a')
        self.send_keys(self.iv_cntr_id, self.cntr_id)
        send_keys('{ENTER}')
        self.click(self.create_container_yes)
        self.click(self.invalid_container_id_yes)
        self.click(self.iv_status)
        self.send_keys(self.iv_status, self.status)
        if status == "em":
            self.click(self.gem)
        self.click(self.iv_size)
        self.send_keys(self.iv_size, self.size)
        self.click(self.iv_type)
        self.send_keys(self.iv_type, self.type)
        time.sleep(0.2)
        self.click(self.iv_owner)
        self.send_keys(self.iv_owner, self.owner)
        self.click(self.iv_region)
        self.click(self.iv_yard_loc)
        # send_keys('^a')
        self.send_keys(self.iv_yard_loc, self.block)
        self.send_keys(self.iv_yard_loc, self.stack)
        self.send_keys(self.iv_yard_loc, self.lane)
        # self.click(self.iv_material)
        # self.send_keys(self.iv_material, self.material)
        # self.click(self.iv_max_gross_wt)
        # self.send_keys(self.iv_max_gross_wt, self.max_gross_wt)
        if status == "em":
            print("ok")
        if status == "if":
            self.if_discharge_details()
            print("ok")

    def if_discharge_details(self):
        self.click(self.iv_voyage)
        send_keys_tab(self.line)
        send_keys_tab(self.vessel)
        send_keys_tab(self.voyage)
        self.click(self.iv_pol)
        self.send_keys(self.iv_pol, self.POL)
        self.click(self.iv_gross_wt)
        self.send_keys(self.iv_gross_wt, self.gross_wt)

    def create_container(self):
        if not self.visible(self.function_view, 1) == "True":
            enter_to_function_view(function=self.function)
            self.click(self.inventory)
            self.click(self.inventory_operation)
            self.click(self.container_details)
        if self.visible(self.cancel) == "True":
            self.click(self.cancel)
        self.common_details(self.status)
        # self.click(self.create_ok)

    def test(self):
        self.test_field = "04"
        update_yaml(self.yaml_path, "test.value", self.test_field)

if __name__ == '__main__':
    # python -m test_ui.inventory_operation.container_details
    cd = ContainerDetails()
    # cd.create_container()
    cd.test()