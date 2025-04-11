import os
from helper.logger import logger
from invoke import task

@task
def initiate(c):
    """
    Initialize the environment for the container details task.
    """
    logger.info("Initializing environment...")
    os.system("python -m test_ui.app")
    # c.run("python -m test_ui.app")

@task
def create_cntr(c, count=1):
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
    c.run("python -m test_ui.flow.bol_maintenance")

@task
def test_code(c):
    """
    Run the test code for code test.
    """
    c.run("python -m test_ui.flow.container_details --test")

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
    c.run("python -m test_ui.flow.hold_release")

@task
def create_pickup(c):
    """
    Create a pickup task.
    """
    c.run("python -m test_ui.flow.gate_transaction")

@task
def pickup_task(c):
    """
    Run the pickup task.
    """
    # initiate(c)
    create_cntr(c)
    add_bol(c)

@task
def pickup(c):
    c.run("python -m test_ui.flow.gate_transaction")