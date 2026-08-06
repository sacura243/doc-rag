from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from api.dependencies import AccessTokenUser, require_user
from doc_rag.config import load_config
from doc_rag.rag import ask_with_sources


router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    top_k: int = Field(default=4, ge=2, le=6)


@router.post("")
def chat(request: ChatRequest, _user: AccessTokenUser = Depends(require_user)) -> dict:
    try:
        answer, sources = ask_with_sources(load_config(), request.question.strip(), request.top_k, workspace_id="default")
    except RuntimeError:
        raise HTTPException(status_code=502, detail="Knowledge base service is unavailable") from None
    return {
        "answer": answer,
        "sources": [
            {"name": Path(item["source"]).name, "page": item.get("page"), "content": item["content"]}
            for item in sources
        ],
    }
