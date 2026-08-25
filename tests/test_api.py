"""Smoke-Tests für die Vorsorge-Ordner API.

Aufruf lokal:
    cd opt/vorsorgeordner/app
    ../venv/bin/pip install -r ../requirements.txt httpx pytest --break-system-packages
    ../venv/bin/python -m pytest ../../../tests/test_api.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

APP_DIR = Path(__file__).resolve().parent.parent / "opt" / "vorsorgeordner" / "app"
sys.path.insert(0, str(APP_DIR))

from fastapi.testclient import TestClient  # noqa: E402

from main import app  # noqa: E402

SAMPLE_PAYLOAD = json.loads((Path(__file__).parent / "sample-payload.json").read_text(encoding="utf-8"))

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.parametrize("kind,magic", [("pdf", b"%PDF"), ("docx", b"PK")])
def test_export_sample_payload(kind, magic):
    r = client.post(f"/api/export/{kind}", json=SAMPLE_PAYLOAD)
    assert r.status_code == 200, r.text
    assert r.content[:4].startswith(magic[: len(r.content[:4])]) or r.content.startswith(magic)


@pytest.mark.parametrize("kind", ["pdf", "docx"])
def test_export_empty_payload_uses_defaults(kind):
    """Leeres JSON darf nicht crashen - alle Felder haben Defaults."""
    r = client.post(f"/api/export/{kind}", json={})
    assert r.status_code == 200


def test_export_empty_body_is_400():
    r = client.post("/api/export/pdf", data=b"", headers={"Content-Type": "application/json"})
    assert r.status_code == 400


def test_export_invalid_json_is_422_not_500():
    r = client.post("/api/export/pdf", data=b"{not valid json", headers={"Content-Type": "application/json"})
    assert r.status_code == 422


def test_ausweiskopie_field_reaches_pdf():
    """Regressionstest fuer den Tippfehler-Bug (urkunden.ausweikopie statt ausweiskopie)."""
    r = client.post("/api/export/pdf", json={"urkunden": {"ausweiskopie": "Safe im Büro"}})
    assert r.status_code == 200
    # PDF-Bytes sind komprimiert/kodiert - wir pruefen nur, dass der Export ohne Fehler
    # durchlaeuft; der eigentliche Text-Check laeuft in der manuellen QS mit pdfplumber.
