ALLOWED_TRANSITIONS={
    "CREATED" : {"IN_PROGRESS"},
    "IN_PROGRESS" : {"COMPLETED"},
    "COMPLETED" : set(),
} # Define allowed status transitions

def validate_status_transition(old_status: str, new_status: str): # Function to validate status transitions
    if new_status not in ALLOWED_TRANSITIONS.get(old_status,set()): # Check if the new status is allowed from the old status
        raise ValueError(
            f"Invalid status transition from {old_status} to {new_status}"
        )