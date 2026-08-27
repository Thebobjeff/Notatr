from pydantic import BaseModel, Field
from typing import List, Optional

class ActionItem(BaseModel):
    task: str = Field(description="The specific task to be done")
    assignee: Optional[str] = Field(default="Unassigned", description="Person responsible")
    deadline: Optional[str] = Field(default="TBD", description="Date or timeframe mentioned")

class MeetingPayload(BaseModel):
    meeting_title: str
    date_detected: Optional[str]
    executive_summary: str
    key_discussion_points: List[str]
    decisions_made: List[str]
    action_items: List[ActionItem]
    diagram_mermaid: Optional[str] = Field(
        default=None, 
        description="Mermaid.js code if a flowchart or sketch is present"
    )