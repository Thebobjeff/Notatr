import os
from notion_client import Client
from core.schemas import MeetingPayload
from dotenv import load_dotenv
load_dotenv()

def get_notion_client() -> Client:
    token = os.getenv("NOTION_API_KEY")
    if not token:
        raise ValueError("NOTION_API_KEY environment variable is missing.")
    return Client(auth=token)


def push_meeting_notes_to_notion(payload: MeetingPayload) -> str:
    """Creates a new formatted Notion page under the parent page defined in NOTION_PAGE_ID.

    Returns the URL of the created Notion page.
    """
    notion = get_notion_client()
    parent_page_id = os.getenv("NOTION_PARENT_PAGE_ID")
    if not parent_page_id:
        raise ValueError("NOTION_PAGE_ID environment variable is missing.")

    # Build Notion Block elements dynamically
    children_blocks = []

    # 1. Executive Summary Section
    children_blocks.extend(
        [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {"type": "text", "text": {"content": "Executive Summary"}}
                    ]
                },
            },
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": payload.executive_summary},
                        }
                    ],
                    "icon": {"emoji": "📌"},
                },
            },
        ]
    )

    # 2. Key Decisions Section
    if payload.decisions_made:
        children_blocks.append(
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": "Decisions Made"},
                        }
                    ]
                },
            }
        )
        for decision in payload.decisions_made:
            children_blocks.append(
                {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [
                            {"type": "text", "text": {"content": decision}}
                        ]
                    },
                }
            )

    # 3. Action Items Checklist Section
    if payload.action_items:
        children_blocks.append(
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {"type": "text", "text": {"content": "Action Items"}}
                    ]
                },
            }
        )
        for item in payload.action_items:
            task_label = (
                f"{item.task} (Owner: {item.assignee} | Due: {item.deadline})"
            )
            children_blocks.append(
                {
                    "object": "block",
                    "type": "to_do",
                    "to_do": {
                        "rich_text": [
                            {"type": "text", "text": {"content": task_label}}
                        ],
                        "checked": False,
                    },
                }
            )

    # 4. Key Discussion Points Section
    if payload.key_discussion_points:
        children_blocks.append(
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": "Discussion Points"},
                        }
                    ]
                },
            }
        )
        for point in payload.key_discussion_points:
            children_blocks.append(
                {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [
                            {"type": "text", "text": {"content": point}}
                        ]
                    },
                }
            )

    # 5. Mermaid Diagram (if any)
    if payload.diagram_mermaid:
        children_blocks.extend(
            [
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "Visual / Process Diagram"
                                },
                            }
                        ]
                    },
                },
                {
                    "object": "block",
                    "type": "code",
                    "code": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": payload.diagram_mermaid},
                            }
                        ],
                        "language": "mermaid",
                    },
                },
            ]
        )

    # Create the page under parent page
    page_title = (
        f"{payload.meeting_title} ({payload.date_detected})"
        if payload.date_detected
        else payload.meeting_title
    )
    created_page = notion.pages.create(
        parent={"page_id": parent_page_id},
        icon={"type": "emoji", "emoji": "📝"},
        properties={
            "title": {
                "title": [{"type": "text", "text": {"content": page_title}}]
            }
        },
        children=children_blocks,
    )

    return created_page.get("url", "https://notion.so")