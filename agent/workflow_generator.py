from models.claim import Task

def generate_claim_tasks(policy_rules: str, incident_description: str):
    """
    Core agent behavior:
    converts policy rules + incident into tasks
    """

    task_names = [
        "Notify insurer",
        "Upload hospital admission note",
        "Upload hospital bill",
        "Upload discharge summary",
        "Upload ID proof"
    ]

    tasks = []
    for i, name in enumerate(task_names):
        tasks.append(Task(task_id=i + 1, name=name))

    return tasks
