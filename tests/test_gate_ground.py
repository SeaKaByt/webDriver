import allure
import pytest
from pandas import DataFrame

from helper.paths import ProjectPaths

@pytest.mark.gate_ground
@allure.title("Gate Ground Workflow")
def test_workflow(backup_csv, video_recorder, session):
    """
    Test gate ground workflow with return container and ground operations.

    Args:
        backup_csv: Fixture to backup specific CSV files
        video_recorder: Fixture to record test execution
        session: Fixture providing driver and page objects
    """
    # Backup only CSV files this test will modify
    backup_csv('gate_ground', 'tractor_usage')
    
    return_cntr = True
    create_gate_ground = False

    gdf: DataFrame
    gp: str
    try:
        gdf, gp = next(ProjectPaths.get_gate_ground_data())
        if gdf.empty:
            pytest.skip("No gate ground data available")
    except Exception as e:
        pytest.fail(f"Failed to load gate ground data: {str(e)}")

    # Use page objects from driver_session fixture
    if return_cntr:
        with allure.step("Booking section"):
            session.booking.add_return_cntr(gdf, gp)
    
    if create_gate_ground:
        with allure.step("Gate Ground section"):
            session.gate.create_gate_ground(gdf, gp)