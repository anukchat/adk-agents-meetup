
import os
from typing import List, Dict, Union

TODO_FILE = "artifacts/todo.txt"

def add_task(task_description: str) -> Dict[str, str]:
    """Adds a new task to the to-do list."""
    try:
        os.makedirs(os.path.dirname(TODO_FILE), exist_ok=True)
        with open(TODO_FILE, "a") as f:
            f.write(task_description + "\n")
        return {"status": "success", "message": f"Task '{task_description}' added."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def list_tasks() -> Dict[str, Union[str, List[str]]]:
    """Lists all tasks in the to-do list."""
    if not os.path.exists(TODO_FILE):
        return {"status": "success", "message": "No tasks found.", "tasks": []}
    try:
        with open(TODO_FILE, "r") as f:
            tasks = [line.strip() for line in f if line.strip()]
        return {"status": "success", "message": f"Found {len(tasks)} tasks.", "tasks": tasks}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def mark_task_complete(task_index: int) -> Dict[str, str]:
    """Marks a task as complete by its 1-based index."""
    if not os.path.exists(TODO_FILE):
        return {"status": "error", "message": "No tasks found to mark as complete."}
    try:
        with open(TODO_FILE, "r") as f:
            tasks = [line.strip() for line in f if line.strip()]
        if 0 < task_index <= len(tasks):
            completed_task = tasks.pop(task_index - 1)
            with open(TODO_FILE, "w") as f:
                for task in tasks:
                    f.write(task + "\n")
            return {"status": "success", "message": f"Task '{completed_task}' marked complete."}
        else:
            return {"status": "error", "message": f"Invalid task index: {task_index}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_todo_tools(selected_tools: List[str] = ["add_task", "list_tasks", "mark_task_complete"]):
    tool_mapping = {
        "add_task": add_task,
        "list_tasks": list_tasks,
        "mark_task_complete": mark_task_complete,
    }
    return [tool_mapping[tool] for tool in selected_tools if tool in tool_mapping]
