import os
from invoke import task, run

@task
def initiate(c):
    """
    Initialize the environment for the container details task.
    """
    c.run("python -m test_ui.app login_ngen")

@task
def create_cntr(c, count=2):
    """
    Create a specified number of containers using container_details.py.
    Args:
        count: Number of containers to create (default: 1).
    """
    cmd = f"python -m test_ui.flow.container_details {count}"
    os.system(cmd)
    # c.run(cmd)

@task
def add_bol(c):
    """
    Add Bill of Lading (BOL) for the container.
    """
    c.run("python -m test_ui.flow.bol_maintenance add_cntr")

@task()
def createCro(c):
    """
    Create a CRO and get the PIN.
    """
    c.run("python -m test_ui.flow.cro_maintenance")

@task
def hold_release(c):
    """
    Release hold on the container.
    """
    c.run("python -m test_ui.flow.hold_release release_hold")

@task
def add_return_cntr(c):
    """
    Add return container.
    """
    c.run("python -m test_ui.flow.booking_maintenance")

@task
def create_gate_pickup(c):
    """
    Create a pickup task.
    """
    # c.run("python -m test_ui.flow.gate_transaction create_pickup")
    # c.run("python -m test_ui.flow.gate_transaction release_print_cwp")
    # c.run("python -m test_ui.flow.queue_monitor --pickup")
    c.run("python -m test_ui.flow.gate_transaction confirm_pickup")

def create_gate_ground(c):
    c.run("python -m test_ui.flow.gate_transaction create_gate_ground")
    # c.run("python -m test_ui.flow.queue_monitor --ground")
    # c.run("python -m test_ui.flow.gate_transaction confirm_ground")

@task
def gate_pickup_task(c):
    """
    Run the pickup task.
    """
    # initiate(c)
    # create_cntr(c)
    # add_bol(c)
    # createCro(c)
    # hold_release(c)
    create_gate_pickup(c)

@task
def gate_ground_task(c):
    # initiate(c)
    # add_return_cntr(c)
    create_gate_ground(c)