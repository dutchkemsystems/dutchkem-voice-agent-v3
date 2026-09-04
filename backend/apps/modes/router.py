from fastapi import APIRouter, HTTPException

from .registry import ModeRegistry
from .schemas import ModeResponse, ModeListResponse, ModeSwitchRequest, ModeSwitchResponse

router = APIRouter(prefix="/api/modes", tags=["modes"])


@router.get("/", response_model=ModeListResponse)
async def list_modes():
    """List all available modes."""
    modes = ModeRegistry.get_all()
    return ModeListResponse(
        modes=[
            ModeResponse(
                mode_id=m.mode_id,
                display_name=m.display_name,
                description=m.description,
                icon=m.icon,
                agent_classes=m.agent_classes,
                default_agent=m.default_agent,
                required_context=m.required_context,
                ui_components=m.ui_components,
                default_view=m.default_view,
            )
            for m in modes
        ],
        count=len(modes),
    )


@router.get("/{mode_id}", response_model=ModeResponse)
async def get_mode(mode_id: str):
    """Get a specific mode."""
    mode = ModeRegistry.get(mode_id)
    if not mode:
        raise HTTPException(status_code=404, detail=f"Mode '{mode_id}' not found")

    return ModeResponse(
        mode_id=mode.mode_id,
        display_name=mode.display_name,
        description=mode.description,
        icon=mode.icon,
        agent_classes=mode.agent_classes,
        default_agent=mode.default_agent,
        required_context=mode.required_context,
        ui_components=mode.ui_components,
        default_view=mode.default_view,
    )


@router.post("/switch", response_model=ModeSwitchResponse)
async def switch_mode(request: ModeSwitchRequest):
    """Switch to a different mode."""
    mode = ModeRegistry.get(request.mode_id)
    if not mode:
        raise HTTPException(status_code=400, detail=f"Invalid mode: {request.mode_id}")

    return ModeSwitchResponse(
        success=True,
        mode=ModeResponse(
            mode_id=mode.mode_id,
            display_name=mode.display_name,
            description=mode.description,
            icon=mode.icon,
            agent_classes=mode.agent_classes,
            default_agent=mode.default_agent,
            required_context=mode.required_context,
            ui_components=mode.ui_components,
            default_view=mode.default_view,
        ),
        message=f"Switched to {mode.display_name} mode",
    )
