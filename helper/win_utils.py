import pywinauto

from typing import Optional
from pywinauto.keyboard import send_keys
from helper.logger import logger

def send_keys_wlog(keys: str, with_tab: bool = False, field_length: Optional[int] = None) -> None:
    should_send_tab = with_tab or (field_length is not None and len(keys) < field_length)

    logger.info(f"Sending keys: {keys}{' + TAB' if should_send_tab else ''}")
    send_keys(keys)
    if should_send_tab:
        send_keys("{TAB}")

def wait_for_window(title: str, timeout: int = 10) -> None:
    """Wait for a window with the given title to appear."""
    import time
    logger.info(f"Waiting for window: {title} (timeout={timeout}s)")
    for _ in range(timeout * 2):  # 0.5s intervals
        windows = pywinauto.findwindows.find_windows(title_re=title)
        if windows:
            logger.info(f"Found window: {windows}")
            return windows
        time.sleep(0.5)
    logger.warning(f"Window not found: {title} after {timeout}s")
    return None

def find_window(title: str, exact_match: bool = False) -> list:
    if exact_match:
        windows = pywinauto.findwindows.find_windows(title=title)
    else:
        windows = pywinauto.findwindows.find_windows(title_re=title)
    return windows

def focus_window(title: str, exact_match: bool = False) -> bool:
    try:
        # Find windows matching the title
        if exact_match:
            windows = pywinauto.findwindows.find_windows(title=title)
        else:
            windows = pywinauto.findwindows.find_windows(title_re=title)
        
        if not windows:
            logger.warning(f"No windows found with title: {title}")
            return False
        
        # Try each matching window until one succeeds
        for window_handle in windows:
            try:
                # Use pywinauto to connect to the window and bring it to front
                app = pywinauto.Application().connect(handle=window_handle)
                window = app.window(handle=window_handle)
                window.set_focus()
                logger.info(f"Successfully brought window to front: {title} (handle: {window_handle})")
                return True
            except Exception as window_error:
                logger.debug(f"Failed to focus window handle {window_handle}: {window_error}")
                continue
        
        logger.warning(f"All windows with title '{title}' failed to activate")
        return False
        
    except Exception as e:
        logger.error(f"Error bringing window to front by title '{title}': {e}")
        return False

def main():
    focus_window("Guider")
    focus_window("Application")

if __name__ == "__main__":
    main()