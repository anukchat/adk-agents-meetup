
import os
import subprocess
from typing import Dict, Any, Optional, List

def run_shell_command(
    command: str,
    description: Optional[str] = None,
    directory: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Executes a given bash shell command using `bash -c <command>`.

    Use this tool when downloading data via `curl`, `wget`, or when
    needing to unzip, rename, or move files. Prefer it over code_agent
    for command-line tasks.

    Args:
        command: The shell command to run.
        description: Optional label for the command (ignored by shell).
        directory: Directory to execute command in.

    Returns:
        Dict with stdout, stderr, and exit code.
    """
    if directory and not os.path.isdir(directory):
        return {"error": f"Directory not found: {directory}"}

    try:
        process = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=directory,
        )
        return {
            "stdout": process.stdout,
            "stderr": process.stderr,
            "exit_code": process.returncode,
        }
    except Exception as e:
        return {"error": str(e)}

def memory(
    operation: str,
    key: str,
    value: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Saves or retrieves key-value memory pairs between research phases.

    Use this to store:
    - Base authentic URLs
    - Direct file links
    - Important identifiers
    - Intermediate values

    Args:
        operation: "save" or "load".
        key: The identifier for the value.
        value: Optional value to save (only for 'save').

    Returns:
        Dict with result or error.
    """
    if 'memory_store' not in globals():
        global memory_store
        memory_store = {}

    if operation == "save":
        if value is None:
            return {"error": "Value is required for save operation"}
        memory_store[key] = value
        return {"status": "success"}
    elif operation == "load":
        return {"value": memory_store.get(key)}
    else:
        return {"error": f"Unknown operation: {operation}"}

def get_system_tools(selected_tools: List[str] = ["run_shell_command", "memory"]):
    tool_mapping = {
        "run_shell_command": run_shell_command,
        "memory": memory,
    }
    return [tool_mapping[tool] for tool in selected_tools if tool in tool_mapping]
