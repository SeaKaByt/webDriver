from src.core.driver import BaseDriver
from helper.paths import ProjectPaths

class GenerateDischarge(BaseDriver):
    def __init__(self):
        super().__init__()
        self.df, self.p = next(ProjectPaths.get_discharge_data())

    def debug_planned_0082_positions(self):
        """Debug logger to show all stowage positions ending in 0082 that are planned"""
        # Find all rows where StowageCell_ISO ends with 0082 and planned = "Yes"
        mask = (self.df["StowageCell_ISO"].astype(str).str.endswith("0082")) & (self.df["planned"] == "Yes")
        planned_0082 = self.df[mask]
        
        print("=== DEBUG: Planned positions at row 00, tier 82 ===")
        if not planned_0082.empty:
            for _, row in planned_0082.iterrows():
                stowage = row["StowageCell_ISO"]
                bay = row["Bay"]
                print(f"Stowage {stowage} in bay {bay} is PLANNED")
        else:
            print("No positions ending in 0082 are currently planned")
        print("=" * 50)

    def get_bay_groups(self):
        """
        Get bay groups of 3 consecutive D bays and check availability for size 20 and 40 containers.
        Size 20: uses group[1] (middle bay) - checks stowage like '20082'
        Size 40: uses group[0] and group[2] (first and last bay) - checks stowages like '10082' and '30082'
        """
        # Debug: Show all planned 0082 positions
        self.debug_planned_0082_positions()
        # Get unique D bays from CSV
        all_bays = self.df["Bay"].unique()
        d_bays = [bay for bay in all_bays if 'D' in str(bay)]
        
        # Extract bay numbers and sort
        bay_numbers = []
        for bay in d_bays:
            # Extract number from bay like "01D" -> 1
            bay_num = int(str(bay).replace('D', ''))
            bay_numbers.append(bay_num)
        
        bay_numbers.sort()
        
        # Group by 3s
        groups = []
        for i in range(0, len(bay_numbers), 3):
            group = bay_numbers[i:i+3]
            if len(group) == 3:  # Only complete groups of 3
                groups.append(group)
        
        # Check availability for each group
        available_for_20 = []
        available_for_40 = []
        
        for group in groups:
            # Convert back to bay format: [1,2,3] -> ["01D", "02D", "03D"]
            bay_group = [f"{num:02d}D" for num in group]
            
            # Check size 20 availability (group[1] only)
            size_20_available = self._check_position_free(group[1], "0082")
            
            # Check size 40 availability (group[0] and group[2])
            size_40_pos1_free = self._check_position_free(group[0], "0082")
            size_40_pos2_free = self._check_position_free(group[2], "0082")
            size_40_available = size_40_pos1_free and size_40_pos2_free
            
            # Add to available groups
            if size_20_available:
                available_for_20.append(bay_group)
            if size_40_available:
                available_for_40.append(bay_group)
        
        return {
            'available_for_20': available_for_20,
            'available_for_40': available_for_40
        }
    
    def auto_assign_containers(self, id: str, count: int, size: int):
        """
        Auto assign container IDs to available bay groups
        
        Args:
            id: Base container ID like "DIS1000000" (increments by 1)
            count: Number of containers to assign
            size: Container size (20 or 40)
        """
        # Get available groups
        groups_result = self.get_bay_groups()
        
        if size == 20:
            available_groups = groups_result['available_for_20']
            target_bays_in_group = [0, 2]  # Use first and last bay in group
        elif size == 40:
            available_groups = groups_result['available_for_40'] 
            target_bays_in_group = [1]  # Use middle bay in group
        else:
            raise ValueError("Size must be 20 or 40")
        
        if not available_groups:
            print(f"No available groups for size {size}")
            return []
        
        print(f"Available groups for size {size}: {available_groups}")
        
        assignments = []
        current_id = id
        containers_assigned = 0
        
        # Process groups in order
        for group in available_groups:
            if containers_assigned >= count:
                break
            
            # Re-check if this group is still available after previous assignments
            if not self._is_group_still_available(group, size):
                print(f"Skipping group {group} - no longer available for size {size}")
                continue
                
            print(f"Processing group: {group}")
            
            # Get bays to assign to based on size
            bays_to_assign = [group[i] for i in target_bays_in_group]
            print(f"Assigning to bays: {bays_to_assign}")
            
            # For each bay in this group - complete each bay before moving to next
            for bay in bays_to_assign:
                if containers_assigned >= count:
                    break
                    
                print(f"Filling bay {bay} completely...")
                
                # Extract bay number (like "01D" -> 1)
                bay_num = int(bay.replace('D', ''))
                
                # Keep assigning containers to this bay until it's full or we reach count
                while containers_assigned < count:
                    assigned = self._assign_to_bay(bay_num, current_id)
                    
                    if assigned:
                        assignments.append({
                            'container_id': current_id,
                            'bay': bay,
                            'stowage': assigned['stowage'],
                            'size': size
                        })
                        print(f"Assigned {current_id} to bay {bay}, stowage {assigned['stowage']}")
                        
                        # Increment container ID
                        current_id = self._increment_id(current_id)
                        containers_assigned += 1
                    else:
                        print(f"Bay {bay} is full, moving to next bay")
                        break  # Bay is full, move to next bay
        
        print(f"Total containers assigned: {containers_assigned}/{count}")
        return assignments
    
    def _assign_to_bay(self, bay_num: int, container_id: str):
        """
        Find first free position in a bay and assign container
        Order: tier first (82→84→86→88→90), then row (0→1→2→...→12)
        """
        tiers = [82, 84, 86, 88, 90]
        rows = list(range(0, 13))  # 0 to 12
        
        for tier in tiers:
            for row in rows:
                stowage = int(f"{bay_num}{row:02d}{tier}")
                
                # Check if position is free
                if self._is_position_free(stowage):
                    # Update CSV with new container assignment
                    self._update_csv_with_assignment(container_id, bay_num, stowage, row, tier)
                    
                    print(f"  Assigned {container_id} to position: {stowage} (bay {bay_num}, row {row:02d}, tier {tier})")
                    return {
                        'stowage': stowage,
                        'row': row,
                        'tier': tier
                    }
        
        return None  # No free positions found
    
    def _is_position_free(self, stowage: int) -> bool:
        """Check if a stowage position is free (ContainerNum is empty)"""
        matching_rows = self.df[self.df["StowageCell_ISO"] == stowage]
        
        if not matching_rows.empty:
            # Check if ContainerNum is empty at this stowage
            container_nums = matching_rows["ContainerNum"]
            is_empty = container_nums.isna() | (container_nums == "")
            return is_empty.all()  # True if all ContainerNum fields are empty
        
        # If stowage doesn't exist, position is not available
        return False
    
    def _update_csv_with_assignment(self, container_id: str, bay_num: int, stowage: int, row: int, tier: int):
        """Update existing CSV row with container assignment"""
        # Find the row with this stowage
        mask = self.df["StowageCell_ISO"] == stowage
        matching_indices = self.df[mask].index
        
        if len(matching_indices) > 0:
            # Update the first matching row
            idx = matching_indices[0]
            self.df.loc[idx, "ContainerNum"] = container_id
            
            # Save to CSV
            self.df.to_csv(self.p, index=False)
            print(f"  Updated CSV: {container_id} assigned to stowage {stowage}")
        else:
            print(f"  Warning: Stowage {stowage} not found in CSV")
    
    def _increment_id(self, container_id: str) -> str:
        """Increment container ID by 1 (e.g., DIS1000000 -> DIS1000001)"""
        import re
        
        # Find numeric part at the end
        match = re.search(r'(\d+)$', container_id)
        if match:
            number = int(match.group(1))
            new_number = number + 1
            # Preserve leading zeros
            return container_id[:match.start()] + str(new_number).zfill(len(match.group(1)))
        
        return container_id + "1"
    
    def _is_group_still_available(self, group: list, size: int) -> bool:
        """Check if a group is still available for the given size after current assignments"""
        # Extract bay names
        if size == 20:
            # For size 20: check that group[1] (middle bay) has NO containers at all
            middle_bay = group[1]
            return self._bay_has_no_containers(middle_bay)
        elif size == 40:
            # For size 40: check that group[0] and group[2] have NO containers at all
            first_bay = group[0]
            last_bay = group[2]
            first_bay_free = self._bay_has_no_containers(first_bay)
            last_bay_free = self._bay_has_no_containers(last_bay)
            return first_bay_free and last_bay_free
        
        return False
    
    def _bay_has_no_containers(self, bay: str) -> bool:
        """Check if a bay has no containers assigned (ContainerNum is empty for all positions)"""
        bay_rows = self.df[self.df["Bay"] == bay]
        
        if bay_rows.empty:
            return True  # No rows for this bay means it's free
        
        # Check if ALL ContainerNum fields in this bay are empty
        container_nums = bay_rows["ContainerNum"]
        all_empty = (container_nums.isna() | (container_nums == "")).all()
        return all_empty
    
    def _check_position_free(self, bay_num: int, row_tier: str) -> bool:
        """
        Check if a specific stowage position is free.
        bay_num: bay number like 1, 2, 3
        row_tier: like "0082" for row 00, tier 82
        Returns True if position is free (planned column is not "Yes")
        """
        target_stowage = int(f"{bay_num}{row_tier}")  # Convert to integer like 10082
        
        # Find rows with this stowage
        matching_rows = self.df[self.df["StowageCell_ISO"] == target_stowage]
        
        # Check if any of these rows have "Yes" in planned column
        if not matching_rows.empty:
            planned_yes = (matching_rows["planned"] == "Yes").any()
            return not planned_yes  # True if position is free (no "Yes" in planned)
        
        # If stowage doesn't exist, position is free
        return True
    

if __name__ == "__main__":
    g = GenerateDischarge()
    
    # Test auto assignment
    assignments = g.auto_assign_containers(
        id="DISH100046",
        count=5,
        size=40
    )
    
    print("\nFinal assignments:")
    for assignment in assignments:
        print(f"  {assignment}")