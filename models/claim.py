from dataclasses import dataclass
from typing import List

@dataclass
class Task:
    task_id: int
    name: str
    status: str = "Pending"  # Pending | Done | Blocked

@dataclass
class Claim:
    incident_description: str
    tasks: List[Task]
