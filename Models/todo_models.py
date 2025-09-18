
priority_map = {
    1: "Immediatly",
    2: "Shortly",
    3: "Today",
    4: "This Week",
    5: "This Month",
    6: "At Some Point",
}

class Task:
    def __init__(self, id:int, user_id:int, assigned_time_stamp:str, details:str, closed_time_stamp:str=None, archived:int=0, priority:int=3):
        self.id = id
        self.user_id = user_id
        self.assigned_time_stamp = assigned_time_stamp
        self.closed_time_stamp = closed_time_stamp
        self.archived = archived
        self.details = details
        self.priority = priority
    
    def __init__(self):
        self.id = None
        self.user_id = None
        self.assigned_time_stamp = ""
        self.closed_time_stamp = None
        self.archived = 0
        self.details = ""
        self.priority = 3  # Default priority is 3 (today)

    def load_from_dict(self, data: dict):
        self.id = data.get("id", None)
        self.user_id = data.get("user_id", None)
        self.assigned_time_stamp = data.get("task_assigned_time_stamp", "")
        self.closed_time_stamp = data.get("task_closed_time_stamp", None)
        self.archived = data.get("archived", 0)
        self.details = data.get("task_details", "")
        self.priority = data.get("task_priority", 3)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "task_assigned_time_stamp": self.assigned_time_stamp,
            "task_closed_time_stamp": self.closed_time_stamp,
            "archived": self.archived,
            "task_details": self.details,
            "task_priority": self.priority
        }
    def __str__(self):
        return f"Task(id={self.id}, user_id={self.user_id}, assigned_time_stamp='{self.assigned_time_stamp}', closed_time_stamp='{self.closed_time_stamp}', archived={self.archived}, details='{self.details}', priority={self.priority})"
    
    def to_display_string(self) -> str:
        status = "Archived" if self.archived == 1 else "Active"
        return f"ID: {self.id} | Priority: {priority_map[self.priority]} | Status: {status} | Details: {self.details} | Assigned: {self.assigned_time_stamp}"