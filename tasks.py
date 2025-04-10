from invoke import task

@task
def initiate(c):
    """
    Initialize the environment for the container details task.
    """
    try:
        print("Initializing environment...")
        c.run("python -m test_ui.app", timeout=10)
    except Exception as e:
        print(f"Failed to initialize environment: {e}")
        raise

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
    Add Bill of Lading (BOL) for the container.
    """
    c.run("python -m test_ui.flow.bol_maintenance")

@task
def test_code(c):
    """
    Run the test code for code test.
    """
    c.run(f"python -m test_ui.flow.container_details --test")

@task
def pickup_task(c):
    """
    Run the pickup task.
    """
    initiate(c)
    create_cntr(c, count=2)
    add_bol(c)