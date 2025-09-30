import json
import os
from typing import Optional, List
from pathlib import Path

from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StdioServerParameters,
    StdioConnectionParams,
    SseConnectionParams,
)


def load_mcp_toolset_from_mcp_json(
    config_path: str,
    alias: str,
    tool_names: Optional[List[str]] = None
) -> MCPToolset:
    """
    Reads .mcp.json, picks the MCP server named `alias`, and returns
    an MCPToolset exposing only the tools in tool_names (if provided).
    
    Args:
        config_path: Path to the MCP configuration file
        alias: Name of the MCP server to load
        tool_names: Optional list of tool names to filter by
        
    Returns:
        MCPToolset instance configured with the specified server
        
    Raises:
        FileNotFoundError: If the config file doesn't exist
        KeyError: If the specified alias is not found in the config
        ValueError: If the server type is not supported
    """
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"MCP config file not found: {config_path}")
    
    try:
        with open(config_file, 'r') as f:
            cfg = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in MCP config file: {e}")
    
    # Normalize both syntax variants:
    servers = cfg.get("servers") or cfg.get("mcpServers")
    if not servers or alias not in servers:
        raise KeyError(f"No MCP server '{alias}' found in config")

    srv = servers[alias]
    server_type = srv.get("type", "stdio")
    tools_cfg = tool_names or srv.get("tools", ["*"])

    # Build connection parameters based on the MCP server type
    if server_type in ("local", "stdio"):
        sp = StdioServerParameters(
            command=srv["command"],
            args=srv.get("args", [])
        )
        if "env" in srv:
            env = {}
            for k, v in srv["env"].items():
                if isinstance(v, str) and v.startswith("${env:"):
                    # Handle environment variable substitution
                    env_var = v.split(":", 1)[1].rstrip("}")
                    env[k] = os.getenv(env_var, "")
                else:
                    env[k] = v
            sp = StdioServerParameters(
                command=sp.command,
                args=sp.args,
                env=env
            )
        conn = StdioConnectionParams(server_params=sp, timeout=srv.get("timeout", 100))

    elif server_type in ("sse", "http"):
        url = srv["url"]
        headers = {}
        for k, v in srv.get("headers", {}).items():
            # Copilot convention: "${SECRET_NAME}" → lookup in os.env
            if isinstance(v, str) and v.startswith("${") and v.endswith("}"):
                secret = v[2:-1]
                headers[k] = os.getenv(secret, "")
            else:
                headers[k] = v
        conn = SseConnectionParams(url=url, headers=headers, timeout=srv.get("timeout", 100))

    else:
        raise ValueError(f"Unsupported MCP server type '{server_type}'")

    return MCPToolset(connection_params=conn, tool_filter=tools_cfg)


def get_available_mcp_servers(config_path: str) -> List[str]:
    """
    Get a list of available MCP server aliases from the config file.
    
    Args:
        config_path: Path to the MCP configuration file
        
    Returns:
        List of server aliases
    """
    config_file = Path(config_path)
    if not config_file.exists():
        return []
    
    try:
        with open(config_file, 'r') as f:
            cfg = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []
    
    servers = cfg.get("servers") or cfg.get("mcpServers")
    return list(servers.keys()) if servers else []


def get_mcp_tool(config_path: str = "./deep_researcher/tools/mcp.json", alias: str = "playwright", tool_names: Optional[List[str]] = None):
    """
    Creates and returns an MCP toolset for the specified server.
    
    Args:
        config_path: Path to the MCP configuration file
        alias: Name of the MCP server to load
        tool_names: Optional list of tool names to filter by
        
    Returns:
        MCPToolset instance
    """
    try:
        return load_mcp_toolset_from_mcp_json(config_path, alias, tool_names)
    except Exception as e:
        print(f"Warning: Could not load MCP tool '{alias}': {e}")
        return None
