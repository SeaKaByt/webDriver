from invoke import task

@task
def initiate(c):
    c.run("python -m test_ui.app full_load")

@task
def initiate_guider(c):
    c.run("python -m test_ui.app login_guider")

@task
def create_cntr(c, count=1):
    cmd = f"python -m test_ui.flow.container_details {count}"
    c.run(cmd)

@task
def add_bol(c):
    c.run("python -m test_ui.flow.bol_maintenance add_cntr")

@task()
def create_cro(c):
    c.run("python -m test_ui.flow.cro_maintenance")

@task
def hold_release(c, hold_condition, hold_condition2=None):
    c.run(f"python -m test_ui.flow.hold_release release_hold --hold_condition {hold_condition} --hold_condition2 {hold_condition2}")

@task
def add_return_cntr(c):
    c.run("python -m test_ui.flow.booking_maintenance")

@task
def create_gate_pickup_movement(c):
    c.run("python -m test_ui.flow.gate_transaction --methods create_gate_pickup")
    # c.run("python -m test_ui.flow.queue_monitor --pickup")
    # c.run("python -m test_ui.flow.gate_transaction confirm_pickup")

@task
def create_gate_ground_movement(c):
    c.run("python -m test_ui.flow.gate_transaction --methods create_gate_ground")
    # c.run("python -m test_ui.flow.queue_monitor --ground")
    # c.run("python -m test_ui.flow.gate_transaction confirm_ground")

@task
def voyage_plan(c):
    c.run("python -m test_ui.flow.voyage_plan")

@task
def cwp_plan(c):
    c.run("python -m test_ui.flow.cwp_plan")

@task
def vessel_loading_plan(c):
    hold_release(c, "vm")
    # voyage_plan(c)
    # cwp_plan(c)

@task
def vessel_discharge_plan(c):
    c.run("python -m helper.JMS.send_msg")
    c.run("python -m test_ui.flow.bay_plan")
    hold_release(c, "cc", "hp")
    c.run("python -m test_ui.flow.discharge_container")
    cwp_plan(c)

@task
def gate_pickup_task(c):
    # initiate(c)
    # create_cntr(c)
    # add_bol(c)
    # create_cro(c)
    hold_release(c, "dt")
    create_gate_pickup_movement(c)

@task
def gate_ground_task(c):
    # initiate(c)
    add_return_cntr(c)
    create_gate_ground_movement(c)