from fastapi import APIRouter, HTTPException, status
from app.agent.models import model_router
from app.schemas.schemas import ModelListResponse, ModelSelectRequest, ModelInfo

router = APIRouter(prefix="/api/models", tags=["Model Provider Switcher"])


@router.get("", response_model=ModelListResponse)
async def get_models():
    model_statuses = await model_router.list_model_statuses()
    return ModelListResponse(
        active_provider=model_router.active_provider,
        active_model=model_router.get_adapter().model,
        models=[ModelInfo(**m) for m in model_statuses]
    )


@router.post("/select")
async def select_active_model(request: ModelSelectRequest):
    provider = request.provider.lower()
    if provider not in ["ollama", "anthropic", "openai"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid provider '{provider}'. Choose from: 'ollama', 'anthropic', 'openai'."
        )

    model_router.active_provider = provider
    if request.model:
        adapter = model_router.get_adapter(provider)
        adapter.model = request.model

    model_statuses = await model_router.list_model_statuses()
    return {
        "status": "success",
        "message": f"Active provider switched to {provider}",
        "active_provider": model_router.active_provider,
        "models": model_statuses
    }
