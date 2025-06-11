#!/usr/bin/env python3
"""
Test Results Cleanup Utility

This script helps clean up test results directories before running new tests.
"""

import shutil
import sys
from pathlib import Path


def cleanup_test_results():
    """Clean up all test result directories."""
    base_dir = Path(__file__).parent.parent
    test_results_dir = base_dir / "test-results"
    
    directories_to_clean = [
        test_results_dir / "allure-reports",
        test_results_dir / "videos", 
        test_results_dir / "logs",
        test_results_dir / "screenshots"
    ]
    
    print("🧹 Cleaning up test results directories...")
    
    for directory in directories_to_clean:
        if directory.exists():
            try:
                shutil.rmtree(directory)
                print(f"✅ Cleaned: {directory.relative_to(base_dir)}")
            except Exception as e:
                print(f"❌ Failed to clean {directory.relative_to(base_dir)}: {e}")
        else:
            print(f"ℹ️  Directory doesn't exist: {directory.relative_to(base_dir)}")
    
    # Recreate the main test-results directory structure
    test_results_dir.mkdir(exist_ok=True)
    (test_results_dir / "allure-reports").mkdir(exist_ok=True)
    (test_results_dir / "videos").mkdir(exist_ok=True)
    (test_results_dir / "logs").mkdir(exist_ok=True)
    (test_results_dir / "screenshots").mkdir(exist_ok=True)
    
    print("✅ Test results directories cleaned and recreated!")


if __name__ == "__main__":
    cleanup_test_results() 