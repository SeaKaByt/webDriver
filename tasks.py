from invoke import task

@task
def initiate(c):
    """
    Initialize the environment for the container details task.
    """
    c.run("python -m test_ui.app")

@task
def create_cntr(c, count=1):
    """
    Create a specified number of containers using container_details.py.
    Args:
        count: Number of containers to create (default: 1).
    """
    cmd = f"python -m test_ui.flow.container_details {count}"
    c.run(cmd)

@task
def add_bol(c):
    """
    Add Bill of Lading (BOL) using the container details.
    """
    c.run("python -m test_ui.flow.bol_maintenance")

@task
def test_code(c):
    """
    Run the test code for container details.
    """
    c.run(f"python -m test_ui.flow.container_details --test")

@task
def full_task(c):
    """
    Full task to create containers, add BOL, and run tests.
    """
    initiate(c)
    create_cntr(c, count=2)
    add_bol(c)