# Azure DevOps MCP Server

A Model Context Protocol (MCP) server that integrates Azure DevOps with Claude Code and other MCP-compatible clients. This server allows you to fetch work item details and update work item statuses directly from your AI assistant.

## Features

- **Get Work Item Details**: Fetch comprehensive information about any work item including:
  - Title, type, state, and assigned user
  - Description and steps to reproduce (for bugs)
  - All comments with authors and timestamps
  - Metadata (creation date, last modified, area path, iteration, tags)

- **Update Work Item Status**: Change the state/status of work items (e.g., from "New" to "Active", "Resolved" to "Closed")

## Prerequisites

- Python 3.10 or higher
- An Azure DevOps account with access to a project
- A Personal Access Token (PAT) with Work Items Read & Write permissions

## Installation

### Option 1: Install from GitHub (Easiest for Users)

```bash
pip install git+https://github.com/yourusername/ado-mcp.git
```

**MCP Config (without venv):**
```json
{
  "servers": {
    "ado": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "ado_mcp.server"],
      "env": {
        "ADO_ORGANIZATION": "your-org",
        "ADO_PROJECT": "your-project",
        "ADO_PAT": "your-pat"
      }
    }
  }
}
```

**MCP Config (with venv):**
```json
{
  "servers": {
    "ado": {
      "type": "stdio",
      "command": "C:\\path\\to\\venv\\Scripts\\python.exe",
      "args": ["-m", "ado_mcp.server"],
      "env": {
        "ADO_ORGANIZATION": "your-org",
        "ADO_PROJECT": "your-project",
        "ADO_PAT": "your-pat"
      }
    }
  }
}
```

### Option 2: Clone for Development

1. **Clone or download this repository**

2. **Install the package**:
   ```bash
   pip install -e .
   ```

   Or for development with optional dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Configuration

### Step 1: Create a Personal Access Token (PAT)

1. Go to your Azure DevOps organization: `https://dev.azure.com/[your-organization]`
2. Click on your profile icon (top right) → **Personal access tokens**
3. Click **+ New Token**
4. Configure the token:
   - **Name**: Give it a descriptive name (e.g., "MCP Server Access")
   - **Organization**: Select your organization
   - **Expiration**: Set an appropriate expiration date
   - **Scopes**: Select **Custom defined** and check:
     - Work Items: **Read, Write**
5. Click **Create**
6. **IMPORTANT**: Copy the token immediately (you won't be able to see it again)

### Step 2: Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and fill in your values:
   ```env
   ADO_ORGANIZATION=your-organization-name
   ADO_PROJECT=your-project-name
   ADO_PAT=your-personal-access-token
   ```

   - `ADO_ORGANIZATION`: Your Azure DevOps organization name (from the URL: `https://dev.azure.com/[organization]`)
   - `ADO_PROJECT`: Your project name
   - `ADO_PAT`: The Personal Access Token you created in Step 1

### Step 3: Configure Claude Code

Add the server to your Claude Code MCP settings:

1. Open your MCP settings file:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. Add the ADO MCP server configuration:
   ```json
   {
     "mcpServers": {
       "ado": {
         "command": "python",
         "args": ["-m", "ado_mcp.server"],
         "env": {
           "ADO_ORGANIZATION": "your-organization-name",
           "ADO_PROJECT": "your-project-name",
           "ADO_PAT": "your-personal-access-token"
         }
       }
     }
   }
   ```

   Or, to use the `.env` file approach (recommended for security):
   ```json
   {
     "mcpServers": {
       "ado": {
         "command": "python",
         "args": ["-m", "ado_mcp.server"],
         "cwd": "C:\\Users\\akshay.bachkar\\Downloads\\ADO-MCP"
       }
     }
   }
   ```

3. Restart Claude Code

## Usage

Once configured, you can interact with Azure DevOps through Claude Code:

### Get Work Item Details

```
Get details for work item 12345
```

or

```
Show me information about ADO work item 12345
```

### Update Work Item Status

```
Change work item 12345 status to Active
```

or

```
Update the state of work item 12345 to Resolved
```

## Available Tools

### `get_work_item`

Retrieves detailed information about a work item.

**Parameters:**
- `work_item_id` (integer, required): The ID of the work item

**Returns:**
- Complete work item details including description, comments, status, and metadata

### `update_work_item_status`

Updates the state/status of a work item.

**Parameters:**
- `work_item_id` (integer, required): The ID of the work item
- `new_state` (string, required): The new state (e.g., "Active", "Resolved", "Closed")

**Returns:**
- Confirmation with updated work item details

**Note**: Available states depend on your work item type and process template (Agile, Scrum, CMMI, etc.). Common states include:
- New, Active, Resolved, Closed, Removed (for Bugs)
- New, Active, Closed, Removed (for Tasks)
- New, Active, Resolved, Closed, Removed (for User Stories)

## Troubleshooting

### Authentication Issues

- **Error: "Missing required environment variables"**
  - Ensure your `.env` file exists and contains all three required variables
  - Check that the MCP settings correctly reference the environment variables or `.env` file location

- **Error: "Failed to initialize Azure DevOps client"**
  - Verify your PAT is valid and hasn't expired
  - Ensure your PAT has Work Items Read & Write permissions
  - Check that your organization and project names are correct

### Work Item Issues

- **Error: "Failed to get work item"**
  - Verify the work item ID exists in your project
  - Ensure you have permission to view the work item
  - Check that you're connected to the correct project

- **Error: "Failed to update work item state"**
  - Verify the new state is valid for the work item type
  - Ensure the state transition is allowed (some transitions may be restricted by workflow rules)
  - Check that you have permission to edit the work item

## Development

To contribute or modify the server:

1. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

2. Run tests (when available):
   ```bash
   pytest
   ```

3. Format code:
   ```bash
   black src/
   ```

## Security Notes

- **Never commit your `.env` file or expose your PAT**
- The `.gitignore` file is configured to exclude `.env` files
- Consider using short-lived PATs and rotating them regularly
- Use the minimum required scopes for your PAT (Read & Write for Work Items)

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
