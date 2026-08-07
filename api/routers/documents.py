from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from api.config import load_api_settings
from api.dependencies import AccessTokenUser, require_admin, require_user
from api.schemas import ImportDocumentRequest
from api.services.files import save_remote_upload, save_upload
from doc_rag.config import load_config
from doc_rag.rag import ingest_files
from doc_rag.vector_store import VectorStore


router = APIRouter(prefix="/documents", tags=["documents"])


def document_name(source: str) -> str:
    name = source.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
    return name.split("_", 1)[-1] if "_" in name else name


@router.get("")
def list_documents(_user: AccessTokenUser = Depends(require_user)) -> dict:
    settings = load_api_settings()
    cfg = load_config()
    store = VectorStore(cfg.db_dir, cfg.collection)
    return {
        "items": [
            {"id": source["source"].rsplit("/", 1)[-1].rsplit("\\", 1)[-1], "name": document_name(source["source"]), "chunks": source["chunks"]}
            for source in store.source_summary(workspace_id="default")
        ]
    }


@router.post("", status_code=201)
async def upload_documents(
    files: list[UploadFile] = File(...),
    _user: AccessTokenUser = Depends(require_admin),
) -> dict:
    if len(files) > 5:
        raise HTTPException(status_code=422, detail="Upload at most 5 documents")
    settings = load_api_settings()
    paths = [await save_upload(upload, settings.upload_dir) for upload in files]
    try:
        return ingest_files(load_config(), [str(path) for path in paths], workspace_id="default")
    except Exception:
        for path in paths:
            path.unlink(missing_ok=True)
        raise


@router.post("/import-url", status_code=201)
def import_document_from_url(
    request: ImportDocumentRequest,
    _user: AccessTokenUser = Depends(require_admin),
) -> dict:
    settings = load_api_settings()
    path = save_remote_upload(request.url, request.filename, settings.upload_dir)
    try:
        return ingest_files(load_config(), [str(path)], workspace_id="default")
    except Exception:
        path.unlink(missing_ok=True)
        raise


@router.delete("/{document_id}")
def delete_document(document_id: str, _user: AccessTokenUser = Depends(require_admin)) -> dict:
    if document_id != document_id.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]:
        raise HTTPException(status_code=404, detail="Document not found")
    settings = load_api_settings()
    path = settings.upload_dir / document_id
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Document not found")
    cfg = load_config()
    deleted = VectorStore(cfg.db_dir, cfg.collection).delete_source(str(path), workspace_id="default")
    path.unlink()
    return {"deleted_chunks": deleted}


@router.post("/rebuild")
def rebuild_documents(_user: AccessTokenUser = Depends(require_admin)) -> dict:
    settings = load_api_settings()
    cfg = load_config()
    paths = [path for path in settings.upload_dir.glob("*") if path.suffix.lower() in {".txt", ".pdf", ".docx"}]
    store = VectorStore(cfg.db_dir, cfg.collection)
    store.delete_workspace("default")
    if not paths:
        return {"files": 0, "chunks": 0, "total_chunks": 0}
    return ingest_files(cfg, [str(path) for path in paths], workspace_id="default")
