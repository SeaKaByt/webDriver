from invoke import task
import yaml

def load_config():
    with open("invoke/config.yaml", "r") as file:
        config = yaml.safe_load(file)
    return config

@task
def initiate(c):
    """
    UI automation for launching nGen and Guider applications
    """
    c.run("python -m test_ui.app full_load")

@task
def create_cntr(c, count=1):
    """
    UI automation for creating containers

    *** args ***
    count: Number of containers to create
    """
    cmd = f"python -m test_ui.flow.container_details {count}"
    c.run(cmd)

@task
def vessel_loading_plan(c):
    """
    UI automation for creating vessel loading movements
    - Release VM hold condition
    - Add work plan in guilder
    - CWP release
    """
    config = load_config().get("vessel_loading_plan", {})

    if config.get("release_hold", True):
        hold_release(c, "vm")
    if config.get("work_plan", True):
        voyage_plan(c)
    if config.get("cwp_release", True):
        cwp_plan(c)

@task
def vessel_discharge_plan(c):
    """
    UI automation for creating vessel discharge movements
    - Send Inbound Bay Plan message
    - Upload bay plan to nGen
    - Release CC and HP hold conditions
    - Add edit plan in guilder
    - CWP release
    """
    config = load_config().get("vessel_discharge_plan", {})

    if config.get("send_msg", True):
        send_jms(c)
    if config.get("upload_bay_plan", True):
        upload_bay_plan(c)
    if config.get("release_hold", True):
        hold_release(c, "cc", "hp")
    if config.get("edit_plan", True):
        plan_discharge_container(c)
    if config.get("cwp_release", True):
        cwp_plan(c)

@task
def gate_pickup_task(c, count=1):
    """
    UI automation for creating gate pickup movements
    - Create container
    - Add BOL
    - Release DT hold condition
    - Create gate pickup movement
    """
    config = load_config().get("gate_pickup_task", {})

    if config.get("create_container", True):
        create_cntr(c, count)
    if config.get("add_bol", True):
        add_bol(c)
    if config.get("get_pin", True):
        create_cro(c)
    if config.get("release_hold", True):
        hold_release(c, "dt")
    if config.get("gate_pickup", True):
        create_gate_pickup_movement(c)

@task
def gate_ground_task(c):
    """
    UI automation for creating gate ground movements
    - Add container to return list
    - Create gate ground movement
    """
    config = load_config().get("gate_ground_task", {})

    if config.get("add_return_container", True):
        add_return_cntr(c)
    if config.get("gate_ground", True):
        create_gate_ground_movement(c)

def add_bol(c):
    c.run("python -m test_ui.flow.bol_maintenance add_cntr")

def create_cro(c):
    c.run("python -m test_ui.flow.cro_maintenance")

def hold_release(c, h1, h2=None):
    c.run(f"python -m test_ui.flow.hold_release release_hold --hc1 {h1} --hc2 {h2}")

def add_return_cntr(c):
    c.run("python -m test_ui.flow.booking_maintenance")

def create_gate_pickup_movement(c):
    c.run("python -m test_ui.flow.gate_transaction --methods create_gate_pickup")

def create_gate_ground_movement(c):
    c.run("python -m test_ui.flow.gate_transaction --methods create_gate_ground")

def voyage_plan(c):
    c.run("python -m test_ui.flow.voyage_plan")

def cwp_plan(c):
    c.run("python -m test_ui.flow.cwp_plan")

def send_jms(c):
    c.run("python -m helper.JMS.send_msg")

def upload_bay_plan(c):
    c.run("python -m test_ui.flow.bay_plan")

def plan_discharge_container(c):
    c.run("python -m test_ui.flow.discharge_container")