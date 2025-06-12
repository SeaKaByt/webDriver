"""Video recording fixtures for test execution capture."""

import pytest
import allure
import time
import threading
import cv2
import numpy as np
import pyautogui
from pathlib import Path
from datetime import datetime
from screeninfo import get_monitors
from typing import Optional


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
        self.filename = self.output_dir / f"{test_name}_{timestamp}.mp4"
        
        # Get screen dimensions
        width, height = self._get_screen_dimensions()
        
        # Ensure dimensions are divisible by 2 (required for H.264)
        width = width if width % 2 == 0 else width - 1
        height = height if height % 2 == 0 else height - 1
        
        print(f"📐 Recording dimensions: {width}x{height} @ {self.fps} FPS")
        
        # Initialize H.264 video writer
        self.video_writer = self._init_video_writer(width, height)
        
        if not self.video_writer or not self.video_writer.isOpened():
            raise RuntimeError("❌ Could not initialize H.264 video writer")
        
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
    
    def _get_screen_dimensions(self):
        """Get screen dimensions with fallback options."""
        try:
            monitors = get_monitors()
            if len(monitors) >= 2:
                monitor = monitors[1]  # Second monitor
                print(f"📺 Using second monitor: {monitor.width}x{monitor.height}")
            else:
                monitor = monitors[0]  # Fallback to primary
                print(f"📺 Using primary monitor: {monitor.width}x{monitor.height}")
            return monitor.width, monitor.height
        except:
            # Fallback to pyautogui
            screenshot = pyautogui.screenshot()
            return screenshot.size
    
    def _init_video_writer(self, width, height):
        """Initialize video writer with H.264 codec."""
        h264_codecs = ['h264', 'avc1', 'x264']
        
        for codec_name in h264_codecs:
            try:
                fourcc = cv2.VideoWriter_fourcc(*codec_name)
                writer = cv2.VideoWriter(
                    str(self.filename),
                    fourcc,
                    self.fps,
                    (width, height)
                )
                
                if writer.isOpened():
                    print(f"✅ Video writer initialized with {codec_name.upper()}")
                    return writer
                else:
                    writer.release()
                    
            except Exception as e:
                print(f"❌ Failed to initialize {codec_name.upper()}: {e}")
                
        return None
    
    def _record_loop(self):
        """Main recording loop with error handling."""
        frame_duration = 1.0 / self.fps
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while self.recording:
            try:
                screenshot = self._capture_screen()
                
                if screenshot:
                    frame = np.array(screenshot)
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    
                    if self.video_writer and self.video_writer.isOpened():
                        self.video_writer.write(frame)
                    
                    consecutive_errors = 0
                else:
                    consecutive_errors += 1
                    if consecutive_errors >= max_consecutive_errors:
                        print("❌ Too many capture failures, stopping recording")
                        break
                
                time.sleep(frame_duration)
                
            except Exception as e:
                print(f"❌ Recording error: {e}")
                consecutive_errors += 1
                if consecutive_errors >= max_consecutive_errors:
                    break
                time.sleep(0.5)
    
    def _capture_screen(self):
        """Capture screen with multiple fallback methods."""
        try:
            return pyautogui.screenshot()
        except Exception:
            try:
                from PIL import ImageGrab
                return ImageGrab.grab()
            except Exception:
                return None


# Global recorder instance
_recorder = BrowserVideoRecorder()


@pytest.fixture(scope="function")
def video_recorder(request):
    """Video recorder fixture for test execution capture."""
    # Check command line options
    video_enabled = request.config.getoption("--video", default=False)
    video_on_failure = request.config.getoption("--video-on-failure", default=False)
    disable_on_error = request.config.getoption("--disable-video-on-error", default=True)
    
    # Safety check for previous errors
    if disable_on_error and hasattr(request.config, '_video_error_detected'):
        print("⚠️ Video recording disabled due to previous errors")
        yield None
        return
    
    if not (video_enabled or video_on_failure):
        yield None
        return
    
    # Clean test name for filename
    test_name = request.node.name.replace("::", "_").replace("[", "_").replace("]", "_")
    video_path = None
    
    # Start recording if enabled
    if video_enabled:
        try:
            video_path = _recorder.start_recording(test_name)
            print(f"📹 Started recording: {test_name}")
        except Exception as e:
            print(f"⚠️ Failed to start recording: {e}")
            if disable_on_error:
                request.config._video_error_detected = True
            yield None
            return
    
    yield video_path
    
    # Stop recording and attach to Allure
    try:
        final_path = _recorder.stop_recording()
        
        if final_path and Path(final_path).exists():
            _attach_video_to_allure(final_path, test_name)
    
    except Exception as e:
        print(f"❌ Error in video recorder: {e}")
        if disable_on_error:
            request.config._video_error_detected = True


def _attach_video_to_allure(video_path: str, test_name: str):
    """Attach video file to Allure report."""
    try:
        file_size = Path(video_path).stat().st_size
        print(f"📹 Video size: {file_size / 1024 / 1024:.2f} MB")
        
        # Attach video file
        allure.attach.file(
            video_path,
            name=f"🎬 Test Video - {test_name}",
            attachment_type=allure.attachment_type.MP4
        )
        
        # Add video metadata
        video_info = (
            f"Video Recording Details:\n"
            f"- Test: {test_name}\n"
            f"- File: {video_path}\n"
            f"- Size: {file_size / 1024 / 1024:.2f} MB\n"
            f"- Format: MP4/H.264 (Browser Compatible)"
        )
        
        allure.attach(
            video_info,
            name="📊 Video Info",
            attachment_type=allure.attachment_type.TEXT
        )
        
        print(f"✅ Video attached to Allure: {video_path}")
        
    except Exception as e:
        print(f"❌ Failed to attach video: {e}")
        # Fallback to binary attachment
        try:
            with open(video_path, 'rb') as f:
                allure.attach(
                    f.read(),
                    name=f"🎬 Video (Binary) - {test_name}",
                    attachment_type=allure.attachment_type.MP4
                )
            print(f"✅ Video attached as binary")
        except Exception as e2:
            print(f"❌ Binary attachment failed: {e2}") 