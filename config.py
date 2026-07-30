import os
from pathlib import Path

PYBOX_ROOT = Path(__file__).resolve().parent
MODULES_DIR = PYBOX_ROOT / "modules"

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