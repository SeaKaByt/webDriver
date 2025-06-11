import csv
from pathlib import Path

import pandas as pd

import helper.io_utils

def size_assignments():
    # Initialize dictionary to store identifier-size pairs
    size_assignments = {}

    # Define the range and suffixes
    num_range = range(1, 76)  # 1 to 75
    suffixes = ['D', 'H']

    # Generate groups starting at 1, 5, 9, ..., 73
    group_starts = range(1, 74, 4)  # Step of 4: 1, 5, 9, ..., 73
    for group_idx, start in enumerate(group_starts, 1):  # 1-based group index
        # Generate group identifiers (e.g., 01D, 02D, 03D for start=1)
        for suffix in suffixes:
            group = [f"{i:02d}{suffix}" for i in range(start, min(start + 3, 76))]
            if group:  # Ensure group is not empty
                if group_idx % 2 == 1:  # Odd group (1, 3, 5, ...)
                    size_assignments[group[0]] = 20  # First value gets size 20
                    if len(group) > 2:  # Ensure third value exists
                        size_assignments[group[2]] = 20  # Third value gets size 20
                else:  # Even group (2, 4, 6, ...)
                    if len(group) > 1:  # Ensure second value exists
                        size_assignments[group[1]] = 40  # Second value gets size 40

    # Sort assignments by numerical part and suffix for consistent output
    sorted_assignments = sorted(
        size_assignments.items(),
        key=lambda x: (int(x[0][:-1]), x[0][-1])
    )

    # Save to CSV file
    with open('size_assignments.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write header
        writer.writerow(['Identifier', 'Size'])
        # Write sorted assignments
        for identifier, size in sorted_assignments:
            writer.writerow([identifier, size])

    print("Size assignments have been saved to 'size_assignments.csv'.")

def bay_table(start_bay: int, end_bay: int):
    # Creating list to store bay combinations
    bays = []
    end_bay += 1
    p = Path("data/stowage_usage.csv")

    group_num = 1
    bay_count = 0
    # Generate combinations for D and H with numbers 01 to 75
    for letter in ['D', 'H']:
        for number in range(start_bay, end_bay):
            if number % 4 == 0:
                continue
            # Format number with leading zero and combine with letter
            bay = f"{number:02d}{letter}"
            if bay_count % 3 == 0 and bay_count != 0:
                group_num += 1
            bay_count += 1
            bay_in_group = (bay_count - 1) % 3 + 1
            reserved_size = 20 if bay_in_group in [1, 3] else 40
            bays.append([group_num, bay, reserved_size])  # Store as single-item list for CSV writing

    # Create DataFrame
    df = pd.DataFrame(bays, columns=['group', 'Bay', 'reserved_size'])

    df['capacity'] = None

    # Save to CSV
    df.to_csv(p, index=False)

    print("CSV file 'bay_table.csv' has been created.")

if __name__ == "__main__":
    bay_table(1, 75)