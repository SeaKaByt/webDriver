from typing import List, Optional
import pywinauto
from pywinauto.keyboard import send_keys
from helper.logger import logger

class WindowNotFoundError(Exception):
    """Raised when a window is not found."""
    pass

def send_keys_with_log(keys: str, with_tab: bool = False) -> None:
    """Send keys with optional TAB press."""
    try:
        logger.info(f"Sending keys: {keys}{' + TAB' if with_tab else ''}")
        send_keys(keys)
        if with_tab:
            send_keys("{TAB}")
    except Exception as e:
        logger.error(f"Failed to send keys {keys}: {e}")
        raise

def wait_for_window(title: str, timeout: int = 10) -> Optional[List[int]]:
    """Wait for a window with the given title to appear."""
    import time
    try:
        logger.info(f"Waiting for window: {title} (timeout={timeout}s)")
        for _ in range(timeout * 2):  # 0.5s intervals
            windows = pywinauto.findwindows.find_windows(title_re=title)
            if windows:
                logger.info(f"Found window: {windows}")
                return windows
            time.sleep(1)
        logger.warning(f"Window not found: {title} after {timeout}s")
        return None
    except Exception as e:
        logger.error(f"Error waiting for window {title}: {e}")
        raise

def window_exists(title: str, timeout: int = 10) -> bool:
    """Check if a window exists, raising an error if not found."""
    windows = wait_for_window(title, timeout)
    if windows:
        logger.info(f"Window exists: {title}")
        return True
    logger.error(f"Window not found: {title}")
    raise WindowNotFoundError(f"Window not found: {title}")

