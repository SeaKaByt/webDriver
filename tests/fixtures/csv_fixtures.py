"""CSV backup fixtures for test data management."""

import pytest
from helper.io_utils import create_csv_snapshot
from helper.paths import ProjectPaths
from src.core.driver import BaseDriver
from src.pages.ioc_maintenance.booking_maintenance import BookingMaintenance
from src.pages.gate_house.gate_transaction import GateTransaction

@pytest.fixture(scope="function")
def backup_csv():
    """Factory fixture to backup specific CSV files per test."""
    def _backup_specific_files(*csv_types):
        
        csv_paths = {
            'gate_ground': ProjectPaths.DATA / "gate_ground_data.csv",
            'gate_pickup': ProjectPaths.DATA / "gate_pickup_data.csv",
            'tractor_usage': ProjectPaths.DATA / "tractor_usage.csv",
            'loading': ProjectPaths.DATA / "cntr_data.csv",
            'discharge': ProjectPaths.DATA / "vessel_discharge_data.csv",
        }
        
        for csv_type in csv_types:
            if csv_type in csv_paths:
                create_csv_snapshot(csv_paths[csv_type])
                print(f"✅ Backed up {csv_type} CSV")
            else:
                print(f"⚠️ Unknown CSV type: {csv_type}")
    
    return _backup_specific_files

@pytest.fixture(scope="function")
def session():
    """Fixture to provide driver session with common page objects."""
    with BaseDriver() as d:
        # Create page objects
        booking = BookingMaintenance(d.driver)
        gate = GateTransaction(d.driver)
        
        # Return a simple namespace object with page objects
        class DriverSession:
            def __init__(self, driver, booking, gate):
                self.driver = driver
                self.booking = booking
                self.gate = gate
        
        yield DriverSession(d.driver, booking, gate)