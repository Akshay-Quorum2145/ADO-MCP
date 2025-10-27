"""Azure DevOps API client wrapper."""

import os
from typing import Dict, List, Any, Optional
from azure.devops.connection import Connection
from azure.devops.v7_1.work_item_tracking import WorkItemTrackingClient
from azure.devops.v7_1.work_item_tracking.models import JsonPatchOperation
from msrest.authentication import BasicAuthentication


class ADOClient:
    """Client for interacting with Azure DevOps API."""

    def __init__(self):
        """Initialize the ADO client with credentials from environment variables."""
        self.organization = os.getenv("ADO_ORGANIZATION")
        self.project = os.getenv("ADO_PROJECT")
        pat = os.getenv("ADO_PAT")

        if not all([self.organization, self.project, pat]):
            raise ValueError(
                "Missing required environment variables: ADO_ORGANIZATION, ADO_PROJECT, ADO_PAT"
            )

        # Build organization URL
        organization_url = f"https://dev.azure.com/{self.organization}"

        # Create connection
        credentials = BasicAuthentication("", pat)
        self.connection = Connection(base_url=organization_url, creds=credentials)

        # Get work item tracking client
        self.wit_client: WorkItemTrackingClient = self.connection.clients.get_work_item_tracking_client()

    def get_work_item(self, work_item_id: int) -> Dict[str, Any]:
        """
        Get detailed information about a work item.

        Args:
            work_item_id: The ID of the work item to retrieve

        Returns:
            Dictionary containing work item details including:
            - id: Work item ID
            - title: Work item title
            - type: Work item type (Bug, Task, User Story, etc.)
            - state: Current state/status
            - description: Work item description (HTML)
            - assigned_to: Person assigned to the work item
            - created_date: When the work item was created
            - changed_date: When the work item was last modified
            - steps_to_reproduce: Steps to reproduce (if applicable for bugs)
            - comments: List of comments on the work item
        """
        try:
            # Get the work item with all fields
            work_item = self.wit_client.get_work_item(
                id=work_item_id,
                project=self.project,
                expand="All"
            )

            fields = work_item.fields

            # Extract common fields
            result = {
                "id": work_item.id,
                "title": fields.get("System.Title", ""),
                "type": fields.get("System.WorkItemType", ""),
                "state": fields.get("System.State", ""),
                "description": fields.get("System.Description", ""),
                "assigned_to": fields.get("System.AssignedTo", {}).get("displayName", "Unassigned")
                if isinstance(fields.get("System.AssignedTo"), dict)
                else str(fields.get("System.AssignedTo", "Unassigned")),
                "created_date": str(fields.get("System.CreatedDate", "")),
                "changed_date": str(fields.get("System.ChangedDate", "")),
                "created_by": fields.get("System.CreatedBy", {}).get("displayName", "Unknown")
                if isinstance(fields.get("System.CreatedBy"), dict)
                else str(fields.get("System.CreatedBy", "Unknown")),
                "area_path": fields.get("System.AreaPath", ""),
                "iteration_path": fields.get("System.IterationPath", ""),
                "tags": fields.get("System.Tags", ""),
            }

            # Add steps to reproduce if it exists (common in bugs)
            if "Microsoft.VSTS.TCM.ReproSteps" in fields:
                result["steps_to_reproduce"] = fields["Microsoft.VSTS.TCM.ReproSteps"]

            # Get comments
            comments = self.get_work_item_comments(work_item_id)
            result["comments"] = comments
            result["comment_count"] = len(comments)

            return result

        except Exception as e:
            raise Exception(f"Failed to get work item {work_item_id}: {str(e)}")

    def get_work_item_comments(self, work_item_id: int) -> List[Dict[str, Any]]:
        """
        Get all comments for a work item.

        Args:
            work_item_id: The ID of the work item

        Returns:
            List of comment dictionaries with text, author, and date
        """
        try:
            comments_result = self.wit_client.get_comments(
                project=self.project,
                work_item_id=work_item_id
            )

            comments = []
            if comments_result and hasattr(comments_result, 'comments'):
                for comment in comments_result.comments:
                    comments.append({
                        "text": comment.text,
                        "created_by": comment.created_by.display_name if comment.created_by else "Unknown",
                        "created_date": str(comment.created_date) if comment.created_date else "",
                    })

            return comments

        except Exception as e:
            # Some work items might not have comments enabled
            return []

    def update_work_item_state(self, work_item_id: int, new_state: str) -> Dict[str, Any]:
        """
        Update the state/status of a work item.

        Args:
            work_item_id: The ID of the work item to update
            new_state: The new state to set (e.g., "Active", "Closed", "Resolved")

        Returns:
            Dictionary containing updated work item details
        """
        try:
            # Create JSON patch document to update the state
            patch_document = [
                JsonPatchOperation(
                    op="add",
                    path="/fields/System.State",
                    value=new_state
                )
            ]

            # Update the work item
            updated_work_item = self.wit_client.update_work_item(
                document=patch_document,
                id=work_item_id,
                project=self.project
            )

            # Return updated work item details
            return self.get_work_item(work_item_id)

        except Exception as e:
            raise Exception(f"Failed to update work item {work_item_id} state to '{new_state}': {str(e)}")
