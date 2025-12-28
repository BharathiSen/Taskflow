class BusinessRuleViolation(Exception): # Custom exception for business rule violations
    def __init__(self,message:str): # Initialize with a message
        self.message=message