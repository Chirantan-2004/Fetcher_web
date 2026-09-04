from pathlib import Path
import re
from app.config import Settings
from app.schemas import CanonicalDocument

def safe_name(value: str, fallback: str = "document") -> str:
    value = re.sub(r"[^a-zA-Z0-9._-]+", "-", value).strip("-.")[:80]
    return value or fallback
class LocalStorage:
    def __init__(self, settings: Settings): self.root = Path(settings.storage_path)
    def save(self, document: CanonicalDocument, docx: bytes, pdf: bytes) -> dict[str, str]:
        folder = self.root / str(document.id); folder.mkdir(parents=True, exist_ok=True)
        stem = safe_name(document.title or document.domain)
        paths = {"json": folder / f"{stem}.json", "docx": folder / f"{stem}.docx", "pdf": folder / f"{stem}.pdf"}
        paths["json"].write_text(document.model_dump_json(indent=2), encoding="utf-8"); paths["docx"].write_bytes(docx); paths["pdf"].write_bytes(pdf)
        return {key: str(path) for key, path in paths.items()}
