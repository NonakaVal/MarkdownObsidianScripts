import os
from pathlib import Path

PYBOX_ROOT = Path(__file__).resolve().parent
MODULES_DIR = PYBOX_ROOT / "modules"


def _load_env_file() -> None:
    env_path = PYBOX_ROOT / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


_load_env_file()

# Configuração do ambiente e integrações externas
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "SUA_CHAVE_AQUI")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
)

MODULES = {
    "audio": {
        "label": "Audio Tools",
        "path": MODULES_DIR / "audio",
    },
    "file": {
        "label": "File Tools",
        "path": MODULES_DIR / "file_tools",
    },
    "gallery": {
        "label": "Gallery Tools",
        "path": MODULES_DIR / "gallery_tools",
    },
    "index": {
        "label": "Index Notes",
        "path": MODULES_DIR / "index_notes",
    },
    "manga": {
        "label": "Manga Reader",
        "path": MODULES_DIR / "manga_reader",
    },
    "obsidian": {
        "label": "Obsidian Tools",
        "path": MODULES_DIR / "obsidian_tools",
    },
    "shell": {
        "label": "Shell Tools",
        "path": MODULES_DIR / "shell_tools",
    },
}