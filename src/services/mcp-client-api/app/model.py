from typing import Literal

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel

model_router = APIRouter()


class ModelSchema(BaseModel):
    model: str
    provider: Literal["OpenAI", 'Anthropic', 'Ollama']


@model_router.get("/models")
async def get_models() -> list[ModelSchema]:
    models: list[ModelSchema] = []

    # if config.openai_api_key:
    #     from openai import OpenAI
    #
    #     OpenAI(api_key=config.openai_api_key)

    return models


def init_model_api(app: FastAPI):
    app.include_router(model_router, prefix='/api')