"""Azure DevOps MCP Server implementation."""

import asyncio
import os
from typing import Any
from dotenv import load_dotenv
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .ado_client import ADOClient

# Load environment variables from .env file
load_dotenv()

# Create MCP server instance
server = Server("ado-mcp")

# Global ADO client instance
ado_client: ADOClient = None


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools for Azure DevOps integration."""
    return [
        Tool(
            name="get_work_item",
            description="Get detailed information about an Azure DevOps work item including description, steps to reproduce, comments, status, and other metadata. Works with all work item types (Bugs, Tasks, User Stories, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "work_item_id": {
                        "type": "integer",
                        "description": "The ID of the work item to retrieve",
                    }
                },
                "required": ["work_item_id"],
            },
        ),
        Tool(
            name="update_work_item_status",
            description="Update the state/status of an Azure DevOps work item. Common states include: New, Active, Resolved, Closed, Removed. Note: Available states depend on your work item type and process template.",
            inputSchema={
                "type": "object",
                "properties": {
                    "work_item_id": {
                        "type": "integer",
                        "description": "The ID of the work item to update",
                    },
                    "new_state": {
                        "type": "string",
                        "description": "The new state to set (e.g., 'Active', 'Resolved', 'Closed'). Must be a valid state for the work item type.",
                    },
                },
                "required": ["work_item_id", "new_state"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool execution requests."""
    global ado_client

    # Initialize ADO client on first use
    if ado_client is None:
        try:
            ado_client = ADOClient()
        except ValueError as e:
            return [
                TextContent(
                    type="text",
                    text=f"Error: {str(e)}\n\nPlease ensure ADO_ORGANIZATION, ADO_PROJECT, and ADO_PAT environment variables are set.",
                )
            ]
        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=f"Failed to initialize Azure DevOps client: {str(e)}",
                )
            ]

    try:
        if name == "get_work_item":
            work_item_id = arguments.get("work_item_id")
            if not work_item_id:
                return [
                    TextContent(
                        type="text",
                        text="Error: work_item_id is required",
                    )
                ]

            # Get work item details
            work_item = ado_client.get_work_item(work_item_id)

            # Format the response
            response_lines = [
                f"Work Item #{work_item['id']}: {work_item['title']}",
                f"Type: {work_item['type']}",
                f"State: {work_item['state']}",
                f"Assigned To: {work_item['assigned_to']}",
                f"Created: {work_item['created_date']} by {work_item['created_by']}",
                f"Last Changed: {work_item['changed_date']}",
                f"Area Path: {work_item['area_path']}",
                f"Iteration: {work_item['iteration_path']}",
            ]

            if work_item.get("tags"):
                response_lines.append(f"Tags: {work_item['tags']}")

            response_lines.append("\n--- Description ---")
            response_lines.append(work_item.get("description", "No description"))

            if work_item.get("steps_to_reproduce"):
                response_lines.append("\n--- Steps to Reproduce ---")
                response_lines.append(work_item["steps_to_reproduce"])

            # Add comments
            if work_item["comment_count"] > 0:
                response_lines.append(f"\n--- Comments ({work_item['comment_count']}) ---")
                for i, comment in enumerate(work_item["comments"], 1):
                    response_lines.append(
                        f"\nComment {i} by {comment['created_by']} on {comment['created_date']}:"
                    )
                    response_lines.append(comment["text"])
            else:
                response_lines.append("\n--- Comments ---")
                response_lines.append("No comments")

            return [TextContent(type="text", text="\n".join(response_lines))]

        elif name == "update_work_item_status":
            work_item_id = arguments.get("work_item_id")
            new_state = arguments.get("new_state")

            if not work_item_id or not new_state:
                return [
                    TextContent(
                        type="text",
                        text="Error: work_item_id and new_state are required",
                    )
                ]

            # Update the work item state
            updated_work_item = ado_client.update_work_item_state(work_item_id, new_state)

            response = f"Successfully updated work item #{work_item_id}\n"
            response += f"Title: {updated_work_item['title']}\n"
            response += f"Previous State -> New State: {updated_work_item['state']}\n"
            response += f"Type: {updated_work_item['type']}\n"
            response += f"Assigned To: {updated_work_item['assigned_to']}"

            return [TextContent(type="text", text=response)]

        else:
            return [
                TextContent(
                    type="text",
                    text=f"Unknown tool: {name}",
                )
            ]

    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"Error executing {name}: {str(e)}",
            )
        ]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="ado-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def run():
    """Entry point for the server."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
