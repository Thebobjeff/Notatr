from notion_client import Client
from core.schemas import MeetingPayload


def get_notion_client(api_key: str) -> Client:
    token = api_key.strip() if api_key else ""
    if not token:
        raise ValueError("A Notion integration token is required.")
    return Client(auth=token)


def get_parent_and_title_property(notion: Client, target_id: str) -> tuple[dict, str]:
    """Resolve a Notion page or database ID into a create-page parent."""
    try:
        notion.pages.retrieve(page_id=target_id)
    except Exception as page_error:
        try:
            database = notion.databases.retrieve(database_id=target_id)
        except Exception as database_error:
            raise ValueError(
                "The Notion URL/ID could not be accessed. Confirm the ID and "
                "share the page or database with your Notion integration."
            ) from database_error

        title_properties = [
            name
            for name, definition in database.get("properties", {}).items()
            if definition.get("type") == "title"
        ]
        if not title_properties:
            raise ValueError("The Notion database has no title property.")
        return {"database_id": target_id}, title_properties[0]

    return {"page_id": target_id}, "title"


def push_meeting_notes_to_notion(
    payload: MeetingPayload, target_id: str | None = None, api_key: str = ""
) -> str:
    """Creates a new formatted Notion page under the parent page defined in NOTION_PAGE_ID.

    Returns the URL of the created Notion page.
    """
    notion = get_notion_client(api_key)
    parent_page_id = target_id
    if not parent_page_id:
        raise ValueError("A Notion parent page URL or ID is required.")

    parent, title_property = get_parent_and_title_property(notion, parent_page_id)

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

    # Create the page under either a page or database parent.
    created_page = notion.pages.create(
        parent=parent,
        icon={"type": "emoji", "emoji": "📝"},
        properties={
            title_property: {
                "title": [
                    {
                        "text": {
                            "content": (
                                payload.meeting_title
                                if hasattr(payload, "meeting_title")
                                else payload.get("meeting_title", "Untitled")
                            )
                        }
                    }
                ]
            }
        },
        children=children_blocks,
    )

    return created_page.get("url", "https://notion.so")