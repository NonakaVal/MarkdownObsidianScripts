#!/usr/bin/env python3
"""gca — Git Commit Assistant com IA (versão standalone, 1 arquivo só)

Uso:
    gca                    # Menu interativo
    gca --stage-all        # IA: gera, confirma, stage all + commit
    gca --commit           # IA: gera, confirma, commit (sem stage)
    gca -y                 # IA direto (sem confirmação)

Requer: pip install requests
"""

import subprocess
import sys
import os
import json
import urllib.request
import urllib.error
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from config import GEMINI_API_KEY, GEMINI_API_URL, GEMINI_MODEL

# ── config da IA ────────────────────────────────────────────────────────
GEMINI_URL = GEMINI_API_URL

SYSTEM_PROMPT = """\
You are a commit message generator. Based on the git diff/status below, write a
CONCISE commit message:
- First line: short summary in English, lowercase, no period
- Blank line
- Bullet points describing each meaningful change
- Ignore .env, .obsidian, .vscode, .idea files (just say "update config" if relevant)
- Output ONLY the commit message, nothing else.
"""

COMMIT_TYPES = {
    "feat": "Nova funcionalidade",
    "fix": "Correção de bug",
    "docs": "Documentação",
    "refactor": "Refatoração",
    "style": "Estilo/Formatação",
    "chore": "Tarefas gerais",
    "perf": "Performance",
    "test": "Testes",
}

IGNORED_PREFIXES = (".obsidian/", ".vscode/", ".idea/")
IGNORED_SUFFIXES = (".env", ".env.local", ".env.development", ".env.production", ".env.test")


# ── helpers de git/shell ────────────────────────────────────────────────

def run(cmd, input_text=None):
    return subprocess.run(cmd, capture_output=True, text=True, input=input_text)


def git(*args):
    r = run(["git", *args])
    return r.stdout.strip() if r.returncode == 0 else ""


def is_ignored(path):
    return path.startswith(IGNORED_PREFIXES) or path.endswith(IGNORED_SUFFIXES)


def confirm(msg):
    try:
        return input(msg).strip().lower() == "y"
    except EOFError:
        return False


def clear():
    os.system("clear")


def print_msg(msg):
    print(f"\n{'─' * 52}\n📝 Mensagem:\n")
    for line in msg.split("\n"):
        print(f"   {line}")
    print("─" * 52)


# ── coleta de contexto do git (simplificada) ────────────────────────────

def collect_git_context():
    status = git("status", "--porcelain")
    lines = [l for l in status.split("\n") if l.strip() and not is_ignored(l[3:].strip())]
    if not lines:
        return None, ""

    diff = git("diff")
    staged = git("diff", "--cached")
    untracked = [f for f in git("ls-files", "--others", "--exclude-standard").split("\n")
                 if f and not is_ignored(f)]

    parts = ["## Status\n" + "\n".join(lines)]
    if diff:
        parts.append("## Diff (unstaged)\n```diff\n" + diff[:6000] + "\n```")
    if staged:
        parts.append("## Diff (staged)\n```diff\n" + staged[:6000] + "\n```")
    if untracked:
        parts.append("## New files\n" + "\n".join(f"- {f}" for f in untracked))

    return "\n\n".join(lines), "\n\n".join(parts)


# ── chamada direta à API do Gemini ───────────────────────────────────────

def generate_commit_message(context: str) -> str:
    if GEMINI_API_KEY == "SUA_CHAVE_AQUI":
        print("❌ Configure GEMINI_API_KEY no topo do script.")
        return "update files"

    payload = {
        "contents": [{"parts": [{"text": context}]}],
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
    }
    req = urllib.request.Request(
        GEMINI_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except urllib.error.HTTPError as e:
        print(f"❌ Erro na API ({e.code}): {e.read()[:300]}")
        return "update files"
    except Exception as e:
        print(f"❌ Falha ao chamar a IA: {e}")
        return "update files"


# ── commit core ──────────────────────────────────────────────────────────

def do_commit(msg, stage_all=False):
    if stage_all:
        print("\n→ Staging all changes...")
        if run(["git", "add", "-A"]).returncode != 0:
            print("❌ Falha no git add.")
            return False

    r = run(["git", "commit", "-m", msg])
    if r.returncode != 0:
        print(f"❌ Falha no git commit: {r.stderr[:300]}")
        return False

    print("\n✅ Commit realizado!")
    print_msg(msg)
    return True


def offer_push():
    if confirm("\nPush para remote? (y/n): "):
        print("→ Fazendo push...")
        print("🚀 Push realizado!" if run(["git", "push"]).returncode == 0 else "❌ Push falhou.")


def ia_commit(stage_all=True, auto_confirm=False):
    print("\n🐙 gerando mensagem de commit com IA...")
    _, context = collect_git_context()
    if not context:
        print("\n📭 Nenhuma mudança para commitar.")
        return

    msg = generate_commit_message(context)
    print_msg(msg)

    if not auto_confirm and not confirm("\nConfirmar commit? (y/n): "):
        print("\n❌ Cancelado.")
        return

    if do_commit(msg, stage_all=stage_all) and not auto_confirm:
        offer_push()


def guided_commit():
    keys = list(COMMIT_TYPES)
    print("\nSelecione o TIPO de commit:")
    for i, k in enumerate(keys, 1):
        print(f"  {i}: {k} — {COMMIT_TYPES[k]}")
    try:
        idx = int(input("\nEscolha: ")) - 1
        commit_type = keys[idx]
    except (ValueError, IndexError, EOFError):
        print("❌ Opção inválida.")
        return

    desc = input(f"Descrição ({commit_type}): ").strip()
    if not desc:
        print("❌ Descrição vazia. Cancelado.")
        return

    msg = f"{commit_type}: {desc}"
    print_msg(msg)
    if confirm("\nConfirmar commit? (y/n): ") and do_commit(msg, stage_all=True):
        offer_push()


def custom_commit():
    msg = input("\nMensagem: ").strip()
    if not msg:
        print("❌ Mensagem vazia. Cancelado.")
        return
    print_msg(msg)
    if confirm("\nConfirmar commit? (y/n): ") and do_commit(msg, stage_all=True):
        offer_push()


# ── menus ────────────────────────────────────────────────────────────────

def commit_flow():
    clear()
    print("\n📝 NOVO COMMIT")
    print("  1: 🤖 Commit com IA (stage all + commit)")
    print("  2: 🤖 Commit com IA (apenas commit)")
    print("  3: 🎯 Commit guiado (tipo + descrição)")
    print("  4: ✍️  Mensagem personalizada")
    print("  q: 🔙 Voltar")

    choice = input("\nEscolha: ").strip().lower()
    {
        "1": lambda: ia_commit(stage_all=True),
        "2": lambda: ia_commit(stage_all=False),
        "3": guided_commit,
        "4": custom_commit,
    }.get(choice, lambda: None)()


def check_git_repo():
    if run(["git", "rev-parse", "--is-inside-work-tree"]).returncode != 0:
        print("❌ Não é um repositório git.")
        sys.exit(1)


def main():
    if len(sys.argv) > 1:
        args = sys.argv[1:]
        ia_commit(stage_all="--commit" not in args, auto_confirm="-y" in args or "--yes" in args)
        return

    check_git_repo()
    clear()
    while True:
        print("\n" + "─" * 52)
        subprocess.run(["git", "status", "--short"])
        print("  [1] 📝 Novo commit   [2] 🚀 Push   [3] 👋 Sair")
        choice = input("\n  Escolha: ").strip()
        if choice == "1":
            commit_flow()
        elif choice == "2":
            if confirm("Push para remote? (y/n): "):
                print("🚀 Push realizado!" if run(["git", "push"]).returncode == 0 else "❌ Push falhou.")
        elif choice == "3":
            print("\n  👋 Até logo!\n")
            break
        else:
            print("  ❌ Opção inválida.")


if __name__ == "__main__":
    main()
