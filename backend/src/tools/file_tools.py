
import os
import shutil
from typing import List, Dict, Any

def read_file(file_path: str) -> Dict[str, Any]:
    """
    Reads the full content of a local file as a string.

    Use this after downloading or generating a file to inspect its raw content,
    especially before cleaning or transforming the data with code_agent.

    Args:
        file_path: Path to the file to read.

    Returns:
        Dict with file content or error message.
    """

    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return {"content": f.read()}
    except Exception as e:
        return {"error": str(e)}

def write_file(file_path: str, content: str) -> Dict[str, str]:
    """
    Writes the given string content to a file. Overwrites if file exists.

    Use this to save raw HTML, intermediate data, or final outputs 
    during any phase of the investigation.

    Args:
        file_path: Where to save the file.
        content: Text content to write.

    Returns:
        Status dictionary.
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}

def list_directory(path: str = ".") -> Dict[str, Any]:
    """
    Lists all files and subfolders in the given directory.

    Use this to check available files before reading or overwriting,
    especially during cleanup or debugging steps.

    Args:
        path: Folder path (default is current directory).

    Returns:
        Dict with list of filenames or error.
    """
    if not os.path.isdir(path):
        return {"error": f"Directory not found: {path}"}
    try:
        return {"entries": os.listdir(path)}
    except Exception as e:
        return {"error": str(e)}

def delete_file(file_path: str) -> Dict[str, str]:
    """
    Deletes a file from the workspace.

    Use this only when cleaning up unnecessary files after the final result
    has been generated and saved.

    Args:
        file_path: Path to the file to delete.

    Returns:
        Status dictionary.
    """
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    try:
        os.remove(file_path)
        return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}


def copy_file(source_path: str, destination_path: str) -> Dict[str, str]:
    """
    Copies a file from one path to another.

    Use this to back up intermediate results, rename files, or preserve
    original data before transformation.

    Args:
        source_path: Existing file.
        destination_path: New location to copy to.

    Returns:
        Status dictionary.
    """
    if not os.path.exists(source_path):
        return {"error": f"Source file not found: {source_path}"}
    try:
        shutil.copy2(source_path, destination_path)
        return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}

def get_file_tools(selected_tools: List[str] = ["read_file", "write_file", "list_directory", "delete_file", "copy_file"]):
    tool_mapping = {
        "read_file": read_file,
        "write_file": write_file,
        "list_directory": list_directory,
        "delete_file": delete_file,
        "copy_file": copy_file,
    }
    return [tool_mapping[tool] for tool in selected_tools if tool in tool_mapping]
