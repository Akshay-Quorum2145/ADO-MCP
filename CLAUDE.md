# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Azure DevOps MCP Server - A Model Context Protocol (MCP) server that provides Azure DevOps integration for Claude Code and other MCP-compatible clients. Built with Python and the official MCP SDK.

## Technology Stack

- **Language**: Python 3.10+
- **MCP Framework**: Official `mcp` Python SDK
- **Azure DevOps SDK**: `azure-devops` (Microsoft's official Python SDK)
- **Configuration**: `python-dotenv` for environment variable management
- **Build System**: setuptools with pyproject.toml

## Project Structure

```
ADO-MCP/
├── src/ado_mcp/           # Main package
│   ├── __init__.py        # Package initialization
│   ├── server.py          # MCP server implementation with tool definitions
│   └── ado_client.py      # Azure DevOps API client wrapper
├── pyproject.toml         # Package configuration and dependencies
├── .env.example           # Template for environment variables
├── .env                   # Local environment config (not in git)
├── .gitignore            # Git ignore rules
├── README.md             # User documentation and setup guide
├── FUTURE_ENHANCEMENTS.md # Planned features for future implementation
└── CLAUDE.md             # This file
```

## Architecture

### High-Level Design

The server follows a layered architecture:

1. **MCP Server Layer** (`server.py`):
   - Handles MCP protocol communication
   - Defines available tools (`get_work_item`, `update_work_item_status`)
   - Manages tool execution and response formatting
   - Entry point via `stdio_server()`

2. **ADO Client Layer** (`ado_client.py`):
   - Encapsulates Azure DevOps API interactions
   - Handles authentication via Personal Access Token
   - Provides high-level methods for work item operations
   - Manages error handling for API calls

3. **Azure DevOps SDK**:
   - Microsoft's official Python SDK
   - Handles low-level API communication
   - Provides models for work items, comments, etc.

### Key Components

#### ADOClient Class (`ado_client.py`)

The `ADOClient` class is the main interface to Azure DevOps:

```python
class ADOClient:
    def __init__(self):
        # Loads config from environment variables
        # Creates authenticated connection to ADO
        # Initializes WorkItemTrackingClient

    def get_work_item(self, work_item_id: int) -> Dict[str, Any]:
        # Fetches work item with all fields
        # Retrieves comments
        # Returns structured dictionary

    def get_work_item_comments(self, work_item_id: int) -> List[Dict[str, Any]]:
        # Retrieves all comments for a work item

    def update_work_item_state(self, work_item_id: int, new_state: str) -> Dict[str, Any]:
        # Updates work item state using JSON Patch
        # Returns updated work item details
```

#### MCP Server (`server.py`)

The server exposes two MCP tools:

1. **`get_work_item`**: Returns comprehensive work item information
2. **`update_work_item_status`**: Changes work item state

The server uses async/await pattern required by MCP SDK.

### Authentication Flow

1. Environment variables are loaded from `.env` file via `python-dotenv`
2. ADOClient reads `ADO_ORGANIZATION`, `ADO_PROJECT`, and `ADO_PAT`
3. BasicAuthentication is created with the PAT
4. Connection is established to `https://dev.azure.com/{organization}`
5. WorkItemTrackingClient is initialized for API calls

## Common Commands

### Installation and Setup

```bash
# Install the package in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

### Running the Server

The server is designed to be run by MCP clients (like Claude Code) via configuration. It communicates over stdio.

For manual testing:
```bash
# Run the server directly (will wait for MCP protocol messages on stdin)
python -m ado_mcp.server
```

### Configuration

1. Copy environment template:
```bash
cp .env.example .env
```

2. Edit `.env` with your Azure DevOps credentials:
```
ADO_ORGANIZATION=your-org
ADO_PROJECT=your-project
ADO_PAT=your-token
```

### Development

```bash
# Format code with black
black src/

# Run tests (when implemented)
pytest

# Type checking (if mypy is added)
mypy src/
```

## Important Patterns and Conventions

### Error Handling

- ADOClient methods raise exceptions with descriptive messages
- MCP server catches exceptions and returns them as TextContent
- Always include context in error messages (work item ID, operation, etc.)

### Field Access

Azure DevOps fields use dot notation in their schema:
- `System.Title` - Work item title
- `System.State` - Current state
- `System.Description` - HTML description
- `Microsoft.VSTS.TCM.ReproSteps` - Steps to reproduce (bugs)

Some fields return complex objects (like `System.AssignedTo`), handle both dict and string cases.

### State Updates

Work item state updates use JSON Patch operations:
```python
JsonPatchOperation(
    op="add",
    path="/fields/System.State",
    value=new_state
)
```

The operation type is "add" even when updating existing fields (ADO convention).

### Async Pattern

MCP server handlers must be async functions:
- `@server.list_tools()` decorator for tool listing
- `@server.call_tool()` decorator for tool execution
- Main entry point uses `asyncio.run()`

## Dependencies

### Core Dependencies

- `mcp>=0.9.0` - Model Context Protocol SDK for Python
- `azure-devops>=7.1.0` - Official Microsoft Azure DevOps SDK
- `python-dotenv>=1.0.0` - Environment variable management

### Why These Dependencies

- **mcp**: Official SDK simplifies MCP protocol implementation, handles stdio communication
- **azure-devops**: Official SDK ensures compatibility, provides type hints, handles API versioning
- **python-dotenv**: Secure credential management, keeps secrets out of code

## Testing Strategy

Currently manual testing via Claude Code integration. Future improvements should add:

1. Unit tests for ADOClient methods (mock azure-devops SDK)
2. Integration tests with test ADO project
3. MCP protocol tests for server handlers

## Future Development

See `FUTURE_ENHANCEMENTS.md` for planned features. Priority items:
1. Add comments to work items
2. Search/query work items
3. Update additional fields (description, assigned to, priority)
4. Create new work items

## Security Considerations

- PAT tokens have full access to configured scopes - use minimal permissions
- Never commit `.env` file (already in .gitignore)
- Consider implementing token refresh for long-running scenarios
- PATs expire - document renewal process for users

## Troubleshooting Development Issues

### Import Errors

If you see import errors for `ado_mcp` modules:
- Ensure you've installed the package: `pip install -e .`
- Check you're in the correct virtual environment

### Azure DevOps API Errors

- Verify PAT hasn't expired
- Check PAT has required scopes (Work Items: Read, Write)
- Ensure organization and project names are correct
- Confirm work item IDs exist in the project

### MCP Communication Issues

- MCP uses stdio - don't print debug statements to stdout
- Use proper logging if debug output is needed
- Ensure async functions are properly awaited

## Code Style

- Follow PEP 8 conventions
- Use type hints for function parameters and returns
- Keep functions focused and single-purpose
- Document complex logic with comments
- Use descriptive variable names

## Related Documentation

- [MCP Documentation](https://modelcontextprotocol.io)
- [Azure DevOps Python SDK](https://github.com/microsoft/azure-devops-python-api)
- [Azure DevOps REST API](https://docs.microsoft.com/en-us/rest/api/azure/devops/)
