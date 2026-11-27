from __future__ import annotations

import json
import re
from pathlib import Path


def _clean_text(text: str) -> str:
    text = re.sub(r"-\s*\n", "", text)
    return re.sub(r"\s+", " ", text).strip()


def load_documents(directory: str | Path | None = None, min_chars: int = 30) -> list[dict]:
    from pypdf import PdfReader

    if directory is None:
        data_root = Path(__file__).parent / "data"
        root = data_root / "pdfs"
    else:
        root = Path(directory)
        data_root = root.parent
    metadata_path = data_root / "sources.json"
    pages_root = data_root / "pages"
    documents = []
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
    except (OSError, json.JSONDecodeError):
        metadata = {}

    if root.exists():
        for path in sorted(root.glob("*.pdf")):
            source = metadata.get(path.name, {})
            try:
                reader = PdfReader(str(path))
            except Exception:
                continue
            title = source.get("title") or (reader.metadata.title if reader.metadata else None) or path.name
            for page_number, page in enumerate(reader.pages, start=1):
                try:
                    text = _clean_text(page.extract_text() or "")
                except Exception:
                    continue
                if len(text) >= min_chars:
                    documents.append({"doc_id": f"{path.name}:{page_number}", "source": path.name,
                                      "title": title, "url": source.get("url", ""),
                                      "page": page_number, "kind": "pdf", "text": text})

    if pages_root.exists():
        for path in sorted(pages_root.glob("*.json")):
            try:
                page = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            text = _clean_text(page.get("text", ""))
            if len(text) >= min_chars:
                documents.append({"doc_id": f"{path.stem}:1", "source": page.get("url", path.name),
                                  "title": page.get("title") or page.get("url") or path.name,
                                  "url": page.get("url", ""), "page": 1, "kind": "web", "text": text})
    return documents
