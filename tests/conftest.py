import pytest
import allure
from pathlib import Path
import cv2
import numpy as np
import threading
import time
from datetime import datetime
import pyautogui
from screeninfo import get_monitors
from typing import Optional
from src.core.driver import BaseDriver

class BrowserVideoRecorder:
    """Enhanced video recorder optimized for browser playback in Allure reports."""
    
    def __init__(self, output_dir: str = "test-results/videos", fps: int = 10):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.fps = fps
        self.recording = False
        self.video_writer = None
        self.thread = None
        self.filename = None
        
    def start_recording(self, test_name: str) -> str:
        """Start video recording optimized for browser playback."""
        if self.recording:
            self.stop_recording()
            
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Use MP4 with H.264 for maximum browser compatibility
        self.filename = self.output_dir / f"{test_name}_{timestamp}.mp4"
        
        # Get screen dimensions
        try:
            monitors = get_monitors()
            if len(monitors) >= 2:
                monitor = monitors[1]  # Second monitor
                print(f"📺 Using second monitor: {monitor.width}x{monitor.height}")
            else:
                monitor = monitors[0]  # Fallback to primary if no second monitor
                print(f"📺 Second monitor not found, using primary: {monitor.width}x{monitor.height}")
            width, height = monitor.width, monitor.height
        except:
            # Fallback to pyautogui if monitor detection fails
            screenshot = pyautogui.screenshot()
            width, height = screenshot.size
        
        # Ensure dimensions are divisible by 2 (required for H.264)
        width = width if width % 2 == 0 else width - 1
        height = height if height % 2 == 0 else height - 1
        
        print(f"📐 Recording dimensions: {width}x{height} @ {self.fps} FPS")
        
        # Try H.264 codec variants only for browser compatibility
        h264_codecs = ['h264', 'avc1', 'x264']
        self.video_writer = None
        
        for codec_name in h264_codecs:
            try:
                fourcc = cv2.VideoWriter_fourcc(*codec_name)
                self.video_writer = cv2.VideoWriter(
                    str(self.filename),
                    fourcc,
                    self.fps,
                    (width, height)
                )
                
                if self.video_writer.isOpened():
                    print(f"✅ H.264 video writer initialized with {codec_name.upper()} codec")
                    break
                else:
                    self.video_writer.release()
                    self.video_writer = None
                    
            except Exception as e:
                print(f"❌ Failed to initialize {codec_name.upper()} codec: {e}")
                if self.video_writer:
                    self.video_writer.release()
                    self.video_writer = None
        
        if not self.video_writer or not self.video_writer.isOpened():
            raise RuntimeError("❌ Could not initialize H.264 video writer - browser playback requires H.264 codec")
        
        self.recording = True
        self.thread = threading.Thread(target=self._record_loop, daemon=True)
        self.thread.start()
        
        return str(self.filename)
    
    def stop_recording(self) -> Optional[str]:
        """Stop recording and return the video file path."""
        if not self.recording:
            return None
            
        self.recording = False
        
        # Wait for recording thread to finish
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=10)
        
        # Release video writer
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
        
        final_path = str(self.filename) if self.filename and self.filename.exists() else None
        print(f"⏹️ Recording stopped: {final_path}")
        return final_path
    
    def _record_loop(self):
        """Main recording loop with Windows-compatible screen capture."""
        frame_duration = 1.0 / self.fps
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while self.recording:
            try:
                # Use multiple fallback methods for screen capture on Windows
                screenshot = None
                
                # Method 1: Try PyAutoGUI with thread safety
                try:
                    screenshot = pyautogui.screenshot()
                except Exception as e1:
                    print(f"PyAutoGUI capture failed: {e1}")
                    
                    # Method 2: Try PIL ImageGrab directly (more stable on Windows) 
                    try:
                        from PIL import ImageGrab
                        screenshot = ImageGrab.grab()
                    except Exception as e2:
                        print(f"PIL ImageGrab failed: {e2}")
                        
                        # Method 3: Try alternative screen capture
                        try:
                            import tkinter as tk
                            root = tk.Tk()
                            screen_width = root.winfo_screenwidth()
                            screen_height = root.winfo_screenheight()
                            root.destroy()
                            
                            from PIL import ImageGrab
                            screenshot = ImageGrab.grab(bbox=(0, 0, screen_width, screen_height))
                        except Exception as e3:
                            print(f"Alternative capture failed: {e3}")
                            consecutive_errors += 1
                            if consecutive_errors >= max_consecutive_errors:
                                print("❌ Too many consecutive capture errors, stopping recording")
                                break
                            time.sleep(0.5)  # Wait longer on error
                            continue
                
                if screenshot:
                    frame = np.array(screenshot)
                    
                    # Convert RGB to BGR (OpenCV format)
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    
                    # Write frame
                    if self.video_writer and self.video_writer.isOpened():
                        self.video_writer.write(frame)
                    
                    consecutive_errors = 0  # Reset error counter on success
                else:
                    consecutive_errors += 1
                    if consecutive_errors >= max_consecutive_errors:
                        print("❌ Could not capture screen, stopping recording")
                        break
                
                time.sleep(frame_duration)
                
            except Exception as e:
                print(f"❌ Recording error: {e}")
                consecutive_errors += 1
                if consecutive_errors >= max_consecutive_errors:
                    print("❌ Too many consecutive errors, stopping recording")
                    break
                time.sleep(0.5)  # Wait on error


# Global recorder instance
_browser_recorder = BrowserVideoRecorder()


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

@pytest.fixture(scope="function")
def video_recorder(request):
    """Enhanced video recorder fixture optimized for Allure browser playback."""
    # Check if video recording is enabled
    video_enabled = request.config.getoption("--video")
    video_on_failure = request.config.getoption("--video-on-failure")
    disable_on_error = request.config.getoption("--disable-video-on-error")
    
    # Safety check for Windows - if we detect potential issues, disable recording
    if disable_on_error and hasattr(request.config, '_video_error_detected'):
        print("⚠️ Video recording disabled due to previous errors")
        yield None
        return
    
    if not (video_enabled or video_on_failure):
        yield None
        return
    
    test_name = request.node.name.replace("::", "_").replace("[", "_").replace("]", "_")
    video_path = None
    
    # Start recording if always enabled
    if video_enabled:
        try:
            video_path = _browser_recorder.start_recording(test_name)
            print(f"📹 Started recording for test: {test_name}")
        except Exception as e:
            print(f"⚠️ Failed to start video recording: {e}")
            if disable_on_error:
                request.config._video_error_detected = True
            yield None
            return
    
    yield video_path
    
    # Handle recording based on test result
    try:
        # Check if test failed (for video-on-failure mode)
        test_failed = hasattr(request.node, 'rep_call') and request.node.rep_call.failed
        
        # Start recording for failed tests if video-on-failure is enabled
        if video_on_failure and test_failed and not video_enabled:
            # Unfortunately, we can't start recording after test completion
            # This would require a different approach with continuous recording
            print("⚠️ Cannot start recording after test failure. Use --video for full recording.")
        
        # Stop recording and attach to Allure
        final_path = _browser_recorder.stop_recording()
        
        if final_path and Path(final_path).exists():
            # Attach video to Allure report with optimal settings for browser playback
            try:
                file_size = Path(final_path).stat().st_size
                print(f"📹 Video file size: {file_size / 1024 / 1024:.2f} MB")
                
                # Use allure.attach.file for better browser compatibility
                allure.attach.file(
                    final_path,
                    name=f"🎬 Test Execution Video - {test_name}",
                    attachment_type=allure.attachment_type.MP4
                )
                
                # Also add video metadata as text attachment
                video_info = (
                    f"Video Recording Details:\n"
                    f"- Test Name: {test_name}\n"
                    f"- File Path: {final_path}\n"
                    f"- File Size: {file_size / 1024 / 1024:.2f} MB\n"
                    f"- Duration: ~{(time.time() - getattr(_browser_recorder, 'start_time', time.time())):.1f}s\n"
                    f"- FPS: {_browser_recorder.fps}\n"
                    f"- Browser Compatible: Yes (MP4/H.264)"
                )
                
                allure.attach(
                    video_info,
                    name="📊 Video Info",
                    attachment_type=allure.attachment_type.TEXT
                )
                
                print(f"✅ Video attached to Allure report: {final_path}")
                
            except Exception as e:
                print(f"❌ Failed to attach video to Allure: {e}")
                # Still try to attach as binary if file method fails
                try:
                    with open(final_path, 'rb') as video_file:
                        allure.attach(
                            video_file.read(),
                            name=f"🎬 Video (Binary) - {test_name}",
                            attachment_type=allure.attachment_type.MP4
                        )
                    print(f"✅ Video attached as binary to Allure report")
                except Exception as e2:
                    print(f"❌ Failed to attach video as binary: {e2}")
    
    except Exception as e:
        print(f"❌ Error in video recorder fixture: {e}")
        if disable_on_error:
            request.config._video_error_detected = True