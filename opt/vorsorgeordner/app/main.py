"""Vorsorge-Ordner – FastAPI-Anwendung (lokal, ohne externe Dienste)."""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from content import APP_TITLE
from docx_export import build_docx
from models import VorsorgeDaten
from pdf_export import build_pdf, safe_filename

APP = "vorsorgeordner"
VERSION = "1.0.0"
PORT = int(os.environ.get("VO_PORT", "8080"))

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title=APP_TITLE, version=VERSION, docs_url=None, redoc_url=None, openapi_url=None)

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


@app.get("/api/health")
def health():
    return {"status": "ok", "app": APP, "version": VERSION}


async def _payload(request: Request) -> VorsorgeDaten:
    raw = await request.body()
    if not raw:
        raise HTTPException(status_code=400, detail="Leerer Request-Body – es wurden keine Daten übermittelt.")
    try:
        return VorsorgeDaten.model_validate_json(raw)
    except ValidationError as exc:
        chain = [
            {"pfad": ".".join(str(x) for x in err.get("loc", [])), "fehler": err.get("msg", "")}
            for err in exc.errors()
        ]
        raise HTTPException(
            status_code=422,
            detail={"meldung": "Daten konnten nicht validiert werden", "fehler": chain},
        ) from exc


def _response(data_bytes: bytes, filename: str, media_type: str) -> Response:
    ascii_name = filename.encode("ascii", "ignore").decode() or "vorsorge-ordner"
    headers = {
        "Content-Disposition": (
            f"attachment; filename=\"{ascii_name}\"; "
            f"filename*=UTF-8''{filename.replace(' ', '%20')}"
        ),
        "Cache-Control": "no-store",
    }
    return Response(content=data_bytes, media_type=media_type, headers=headers)


@app.post("/api/export/pdf")
async def export_pdf(request: Request):
    data = await _payload(request)
    name = safe_filename(data.person.name or "Ohne-Namen", "pdf")
    return _response(build_pdf(data), name, "application/pdf")


@app.post("/api/export/docx")
async def export_docx(request: Request):
    data = await _payload(request)
    name = safe_filename(data.person.name or "Ohne-Namen", "docx")
    return _response(build_docx(data), name, DOCX_MIME)


app.mount("/", StaticFiles(directory=BASE_DIR / "static", html=True), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=PORT)
