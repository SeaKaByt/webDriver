import pytest
import allure
import time
import yaml
import subprocess
import sys

# Load configuration from config.yaml
def load_config():
    with open("invoke/config.yaml", "r") as file:
        config = yaml.safe_load(file)
    return config

# Helper functions (replacing invoke task functions)
def create_cntr(count=1, movement=None):
    cmd = [sys.executable, "-m", "test_ui.flow.container_details", str(count), movement]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"create_cntr failed: {result.stderr}")
    return result

def add_bol():
    cmd = [sys.executable, "-m", "test_ui.flow.bol_maintenance", "add_containers"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"add_bol failed: {result.stderr}")
    return result

def create_cro():
    cmd = [sys.executable, "-m", "test_ui.flow.cro_maintenance"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"create_cro failed: {result.stderr}")
    return result

def hold_release(h1, h2=None):
    cmd = [sys.executable, "-m", "test_ui.flow.hold_release", "release_hold", "--hc1", h1]
    if h2:
        cmd.extend(["--hc2", h2])
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"hold_release failed: {result.stderr}")
    return result

def create_gate_pickup_movement():
    cmd = [sys.executable, "-m", "test_ui.flow.gate_transaction", "--methods", "create_gate_pickup"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"create_gate_pickup_movement failed: {result.stderr}")
    return result

# Refactored gate_pickup_task logic
def gate_pickup_task(count=1, movement="gatePickup"):
    config = load_config().get("gate_pickup_task", {})
    step_times = []

    try:
        if config.get("create_container", False):
            print(f"Creating container with count={count}, movement={movement}")
            start_time = time.perf_counter()
            create_cntr(count, movement)
            elapsed = time.perf_counter() - start_time
            step_times.append(f"create_container: count={count}, movement={movement}, time={elapsed:.3f}s")

        if config.get("add_bol", False):
            print("Adding BOL")
            start_time = time.perf_counter()
            add_bol()
            elapsed = time.perf_counter() - start_time
            step_times.append(f"add_bol: time={elapsed:.3f}s")

        if config.get("get_pin", False):
            print("Creating CRO")
            start_time = time.perf_counter()
            create_cro()
            elapsed = time.perf_counter() - start_time
            step_times.append(f"get_pin: time={elapsed:.3f}s")

        if config.get("release_hold", False):
            print("Releasing DT hold")
            start_time = time.perf_counter()
            hold_release("dt")
            elapsed = time.perf_counter() - start_time
            step_times.append(f"release_hold: hold=dt, time={elapsed:.3f}s")

        if config.get("gate_pickup", False):
            print("Creating gate pickup movement")
            start_time = time.perf_counter()
            create_gate_pickup_movement()
            elapsed = time.perf_counter() - start_time
            step_times.append(f"gate_pickup: time={elapsed:.3f}s")

        return step_times
    except Exception as e:
        print(f"Error in gate_pickup_task: {e}")
        raise

# Pytest test for gate_pickup_task
@pytest.mark.gate_pickup
@allure.title("Test Gate Pickup Task")
@allure.description("Tracks execution time and details of gate pickup task steps in Allure.")
def test_gate_pickup_task():
    count = 5
    movement = "gatePickup"
    with allure.step(f"Executing gate_pickup_task with count={count}, movement={movement}"):
        try:
            step_times = gate_pickup_task(count=count, movement=movement)
        except Exception as e:
            allure.attach(str(e), name="Error Log", attachment_type=allure.attachment_type.TEXT)
            raise

    # Attach step execution times and details to Allure
    allure.attach("\n".join(step_times), name="Step Execution Details", attachment_type=allure.attachment_type.TEXT)

    assert True  # Replace with specific assertions based on task output

# Example for another task (gate_ground_task)
def gate_ground_task():
    config = load_config().get("gate_ground_task", {})
    try:
        if config.get("add_return_container", False):
            print("Adding return container")
            cmd = [sys.executable, "-m", "test_ui.flow.booking_maintenance"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"add_return_cntr failed: {result.stderr}")
        if config.get("gate_ground", False):
            print("Creating gate ground movement")
            cmd = [sys.executable, "-m", "test_ui.flow.gate_transaction", "--methods", "create_gate_ground"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"create_gate_ground_movement failed: {result.stderr}")
    except Exception as e:
        print(f"Error in gate_ground_task: {e}")
        raise

@pytest.mark.gate_ground
@allure.title("Test Gate Ground Task")
@allure.description("Measures the execution time of gate ground task.")
def test_gate_ground_task():
    with allure.step("Executing gate_ground_task"):
        start_time = time.perf_counter()
        try:
            gate_ground_task()
        except Exception as e:
            allure.attach(str(e), name="Error Log", attachment_type=allure.attachment_type.TEXT)
            raise
        end_time = time.perf_counter()
    execution_time = end_time - start_time
    allure.attach(f"Execution time: {execution_time:.3f} seconds",
                  name="Gate Ground Task Time",
                  attachment_type=allure.attachment_type.TEXT)
    assert True  # Replace with specific assertions

# @pytest.mark.test_ui_flow_voyage
# @allure.title("Test Voyage Loading with Assertions")
# @allure.description("Measures the execution time and verifies CSV updates.")
# def test_voyage_loading():
#     size_20_count = 2
#     size_40_count = 2
#     voyage = Voyage()
#
#     with allure.step(f"Executing with {size_20_count} 20ft and {size_40_count} 40ft containers"):
#         start_time = time.perf_counter()
#         try:
#             voyage.voyage_loading_actions(size_20_count, size_40_count)
#         except Exception as e:
#             allure.attach(str(e), name="Error Log", attachment_type=allure.attachment_type.TEXT)
#             raise
#         end_time = time.perf_counter()
#
#     execution_time = end_time - start_time
#     allure.attach(f"Execution time: {execution_time:.3f} seconds",
#                   name="Voyage Loading Time",
#                   attachment_type=allure.attachment_type.TEXT)
#
#     # Verify CSV update
#     df = pd.read_csv(Path("data/stowage_usage.csv"))
#     assert not df.empty, "Stowage usage CSV is empty"