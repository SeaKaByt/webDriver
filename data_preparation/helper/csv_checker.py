"""
CSV File Checker - Utility to check if CSV files are open and prompt user to close them
"""

import os
import time
import psutil
from pathlib import Path
from helper.logger import logger


def is_file_locked(file_path):
    """
    Check if a file is locked (being used by another process).
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        bool: True if file is locked, False otherwise
    """
    try:
        # Try to open the file in write mode
        with open(file_path, 'a'):
            return False
    except (IOError, PermissionError):
        return True


def find_processes_using_file(file_path):
    """
    Find processes that are using a specific file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        list: List of process names using the file
    """
    processes = []
    file_path = str(Path(file_path).resolve())
    
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                # Get open files for this process
                for file_info in proc.open_files():
                    if file_info.path.lower() == file_path.lower():
                        processes.append(proc.info['name'])
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    except Exception as e:
        logger.debug(f"Error checking processes: {e}")
    
    return list(set(processes))  # Remove duplicates


def check_csv_files_accessibility(csv_files):
    """
    Check if CSV files are accessible (not locked by other processes).
    
    Args:
        csv_files: List of CSV file paths to check
        
    Returns:
        dict: Dictionary with file status information
    """
    results = {
        "all_accessible": True,
        "locked_files": [],
        "file_details": {}
    }
    
    for csv_file in csv_files:
        file_path = Path(csv_file)
        
        # Check if file exists
        if not file_path.exists():
            results["file_details"][str(csv_file)] = {
                "exists": False,
                "locked": False,
                "processes": []
            }
            continue
        
        # Check if file is locked
        is_locked = is_file_locked(file_path)
        processes = find_processes_using_file(file_path) if is_locked else []
        
        results["file_details"][str(csv_file)] = {
            "exists": True,
            "locked": is_locked,
            "processes": processes
        }
        
        if is_locked:
            results["all_accessible"] = False
            results["locked_files"].append({
                "file": str(csv_file),
                "processes": processes
            })
    
    return results


def prompt_user_to_close_files(locked_files):
    """
    Prompt user to close locked CSV files.
    
    Args:
        locked_files: List of locked file information
        
    Returns:
        bool: True if user wants to continue, False to abort
    """
    print("\n" + "="*60)
    print("CSV FILES ARE CURRENTLY OPEN!")
    print("="*60)
    
    for file_info in locked_files:
        file_name = Path(file_info["file"]).name
        processes = file_info["processes"]
        
        print(f"\nFile: {file_name}")
        print(f"Location: {file_info['file']}")
        
        if processes:
            print(f"Opened by: {', '.join(processes)}")
        else:
            print("Opened by: Unknown process")
    
    print("\n" + "-"*60)
    print("Please close these CSV files before continuing.")
    print("Common applications that might have them open:")
    print("- Microsoft Excel")
    print("- LibreOffice Calc") 
    print("- Text editors (Notepad++, VS Code, etc.)")
    print("-"*60)
    
    while True:
        response = input("\nHave you closed the files? (y/n/q): ").lower().strip()
        
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            print("Please close the CSV files and try again.")
            continue
        elif response in ['q', 'quit']:
            return False
        else:
            print("Please enter 'y' (yes), 'n' (no), or 'q' (quit)")


def wait_for_files_to_be_accessible(csv_files, max_attempts=3):
    """
    Wait for CSV files to become accessible, with user prompts.
    
    Args:
        csv_files: List of CSV file paths to check
        max_attempts: Maximum number of attempts to check
        
    Returns:
        bool: True if all files are accessible, False otherwise
    """
    for attempt in range(max_attempts):
        logger.info(f"Checking CSV file accessibility (attempt {attempt + 1}/{max_attempts})...")
        
        results = check_csv_files_accessibility(csv_files)
        
        if results["all_accessible"]:
            logger.info("All CSV files are accessible!")
            return True
        
        # Show locked files
        if attempt == 0:  # Only show detailed info on first attempt
            if not prompt_user_to_close_files(results["locked_files"]):
                logger.info("User chose to abort.")
                return False
        
        # Wait a moment and check again
        if attempt < max_attempts - 1:
            print("Checking again...")
            time.sleep(2)
            
            # Quick recheck
            recheck_results = check_csv_files_accessibility(csv_files)
            if recheck_results["all_accessible"]:
                print("Great! All files are now accessible.")
                return True
            else:
                print("Some files are still open. Please make sure they are closed.")
    
    print("\nFiles are still locked after multiple attempts.")
    print("Please ensure all CSV files are closed and try running the script again.")
    return False


def check_gate_pickup_csv_files():
    """
    Check the specific CSV files used by the gate pickup workflow.
    
    Returns:
        bool: True if all files are accessible, False otherwise
    """
    csv_files = [
        "data/gate_pickup_data.csv",
        "data/tractor_usage.csv"
    ]
    
    logger.info("Checking gate pickup CSV files...")
    return wait_for_files_to_be_accessible(csv_files)


if __name__ == "__main__":
    # Test the CSV checker
    test_files = [
        "data/gate_pickup_data.csv",
        "data/tractor_usage.csv"
    ]
    
    print("Testing CSV file accessibility...")
    results = check_csv_files_accessibility(test_files)
    
    print(f"\nAll accessible: {results['all_accessible']}")
    
    for file_path, details in results["file_details"].items():
        print(f"\nFile: {file_path}")
        print(f"  Exists: {details['exists']}")
        print(f"  Locked: {details['locked']}")
        print(f"  Processes: {details['processes']}") 