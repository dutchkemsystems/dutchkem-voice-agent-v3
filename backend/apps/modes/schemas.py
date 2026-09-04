from pydantic import BaseModel
from typing import List, Optional, Dict


class ModeResponse(BaseModel):
    mode_id: str
    display_name: str
    description: str
    icon: str
    agent_classes: List[str]
    default_agent: str
    required_context: List[str]
    ui_components: List[str]
    default_view: str


class ModeListResponse(BaseModel):
    modes: List[ModeResponse]
    count: int


class ModeSwitchRequest(BaseModel):
    mode_id: str
    context: Optional[Dict] = None


class ModeSwitchResponse(BaseModel):
    success: bool
    mode: ModeResponse
    message: str
