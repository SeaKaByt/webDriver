"""Main pytest configuration and fixture imports."""

# Import fixtures to make them available to all tests
from tests.fixtures.csv_fixtures import backup_csv, session
from tests.fixtures.video_recorder import video_recorder

def pytest_addoption(parser):
    """Add custom command line options for pytest."""
    parser.addoption(
        "--video",
        action="store_true",
        default=False,
        help="Enable video recording for tests"
    )
    parser.addoption(
        "--video-on-failure",
        action="store_true", 
        default=False,
        help="Enable video recording only on test failures"
    )
    parser.addoption(
        "--disable-video-on-error",
        action="store_true",
        default=True,
        help="Disable video recording if access violations occur (Windows safety)"
    ) 