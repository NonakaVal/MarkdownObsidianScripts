#!/usr/bin/env python3
"""gca — Git Commit Assistant com IA

Menu interativo para gerar mensagens de commit com IA e gerenciar commits.

Uso:
    gca                    # Menu interativo
    gca --stage-all        # IA: gera, confirma, stage all + commit
    gca --commit           # IA: gera, confirma, commit (sem stage)
    gca -y                 # IA direto (sem confirmação)
"""

import subprocess
import sys
import os
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve()
IA_SCRIPT = Path("/home/val/Documentos/Notepad/X/Scripts/generate_commit_msg.py")

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


# ── helpers ───────────────────────────────────────────────────────────

def run_silent(cmd):
    """Executa comando silenciosamente. Retorna True se sucesso."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def run_capture(cmd):
    """Executa comando e retorna (returncode, stdout, stderr)."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def select_option(prompt, options, allow_quit=False):
    """Menu numerado. Retorna índice ou None."""
    print(f"\n{prompt}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}: {opt}")

    suffix = " (ou 'q' para sair): " if allow_quit else ": "
    try:
        choice = input("\nEscolha" + suffix).strip().lower()
    except EOFError:
        return None

    if allow_quit and choice == "q":
        return None
    if choice.isdigit():
        idx = int(choice)
        if 1 <= idx <= len(options):
            return idx - 1
    print("⚠️  Opção inválida.")
    return None if allow_quit else len(options) - 1


def pause():
    try:
        input("\nENTER para continuar...")
    except EOFError:
        pass


def clear():
    os.system("clear")


def confirm(msg):
    """Pergunta confirmação. Retorna True se 'y', False se 'n' ou EOF."""
    try:
        return input(msg).lower().strip() == "y"
    except EOFError:
        return False


def print_msg(msg):
    """Exibe mensagem de commit formatada."""
    print(f"\n{'─' * 52}")
    print("📝 Mensagem:\n")
    for line in msg.split("\n"):
        print(f"   {line}")
    print(f"{'─' * 52}")


# ── commit core ────────────────────────────────────────────────────────

def do_commit(msg, stage_all=False):
    """Executa git add (opcional) + git commit. Retorna True se sucesso."""
    if stage_all:
        print("\n→ Staging all changes...")
        if not run_silent(["git", "add", "-A"]):
            print("❌ Falha no git add.")
            return False

    rc, _, stderr = run_capture(["git", "commit", "-m", msg])
    if rc != 0:
        print(f"❌ Falha no git commit: {stderr[:300]}")
        return False

    print(f"\n✅ Commit realizado!")
    print_msg(msg)
    return True


def offer_push():
    """Pergunta se quer fazer push para remote."""
    if confirm("\nPush para remote? (y/n): "):
        print("→ Fazendo push...")
        if run_silent(["git", "push"]):
            print("🚀 Push realizado!")
        else:
            print("❌ Push falhou.")


# ── IA commit ──────────────────────────────────────────────────────────

def ia_commit(stage_all=True, auto_confirm=False):
    """Gera mensagem com IA, confirma, commita e oferece push."""
    print("\n🐙 gerando mensagem de commit com IA...")

    # Gerar mensagem (sem commitar — chamada sem flags)
    rc, stdout, stderr = run_capture([sys.executable, str(IA_SCRIPT)])

    if rc != 0:
        print(f"\n❌ Falha ao gerar mensagem.")
        if stderr:
            print(f"   {stderr[:300]}")
        return

    msg = stdout.strip()
    if not msg or msg.startswith("No changes"):
        print("\n📭 Nenhuma mudança para commitar.")
        return

    # Mostrar mensagem gerada
    print_msg(msg)

    # Confirmação
    if not auto_confirm:
        if not confirm("\nConfirmar commit? (y/n): "):
            print("\n❌ Cancelado.")
            return

    # Commit
    if not do_commit(msg, stage_all=stage_all):
        return

    # Push opcional
    if not auto_confirm:
        offer_push()


# ── guided commit ──────────────────────────────────────────────────────

def guided_commit():
    """Commit guiado: seleciona tipo + digita descrição."""
    type_keys = list(COMMIT_TYPES.keys())
    type_labels = [f"{k} — {v}" for k, v in COMMIT_TYPES.items()]

    idx = select_option("Selecione o TIPO de commit:", type_labels, allow_quit=True)
    if idx is None:
        return

    commit_type = type_keys[idx]
    print(f"\nDigite a descrição curta ({commit_type}):")
    desc = input("Descrição: ").strip()
    if not desc:
        print("❌ Descrição vazia. Cancelado.")
        return

    msg = f"{commit_type}: {desc}"
    print_msg(msg)

    if not confirm("\nConfirmar commit? (y/n): "):
        print("\n❌ Cancelado.")
        return

    if do_commit(msg, stage_all=True):
        offer_push()


# ── custom commit ──────────────────────────────────────────────────────

def custom_commit():
    """Commit com mensagem totalmente personalizada."""
    print("\nDigite sua mensagem de commit:")
    msg = input("Mensagem: ").strip()
    if not msg:
        print("❌ Mensagem vazia. Cancelado.")
        return

    print_msg(msg)

    if not confirm("\nConfirmar commit? (y/n): "):
        print("\n❌ Cancelado.")
        return

    if do_commit(msg, stage_all=True):
        offer_push()


# ── commit flow submenu ───────────────────────────────────────────────

def commit_flow():
    """Submenu de opções de commit."""
    clear()
    print("\n╭" + "─" * 50 + "╮")
    print("│  📝  NOVO COMMIT                        │")
    print("╰" + "─" * 50 + "╯")
    print("\n  1: 🤖  Commit com IA     (auto-stage + commit)")
    print("  2: 🤖  Commit com IA     (apenas commit)")
    print("  3: 🎯  Commit guiado     (tipo + descrição)")
    print("  4: ✍️   Mensagem personalizada")
    print("  q: 🔙  Voltar")

    choice = input("\nEscolha: ").strip().lower()

    if choice == "1":
        ia_commit(stage_all=True)
    elif choice == "2":
        ia_commit(stage_all=False)
    elif choice == "3":
        guided_commit()
    elif choice == "4":
        custom_commit()
    elif choice == "q":
        return
    else:
        print("❌ Opção inválida.")
        pause()


# ── utilitários ───────────────────────────────────────────────────────

def show_status():
    """Exibe git status --short."""
    print()
    subprocess.run(["git", "status", "--short"])
    print()


def push():
    """Push para remote."""
    if confirm("Push para remote? (y/n): "):
        print("→ Fazendo push...")
        if run_silent(["git", "push"]):
            print("🚀 Push realizado!")
        else:
            print("❌ Push falhou.")


def edit_script():
    """Abre o script no editor disponível."""
    editors = ["nano", "vim", "vi", "gedit", "code"]
    editor = None
    for e in editors:
        rc, _, _ = run_capture(["which", e])
        if rc == 0:
            editor = e
            break
    if not editor:
        print("❌ Nenhum editor encontrado (nano, vim, gedit, code).")
        return
    print(f"\n📝 Abrindo {SCRIPT_PATH} com {editor}...")
    subprocess.run([editor, str(SCRIPT_PATH)])


def check_git_repo():
    """Verifica se está num repositório git."""
    rc, _, _ = run_capture(["git", "rev-parse", "--is-inside-work-tree"])
    if rc != 0:
        print("❌ Não é um repositório git. Navegue até um diretório com .git")
        sys.exit(1)


def about():
    """Exibe informações do script."""
    clear()
    print(f"""
╭──────────────────────────────────────────────────╮
│  🐙  gca — Git Commit Assistant                  │
├──────────────────────────────────────────────────┤
│  📦  PyBox — Shell Tools Module                  │
│  📁  {SCRIPT_PATH.name}                                  │
╰──────────────────────────────────────────────────╯""")


# ── main ──────────────────────────────────────────────────────────────

def main():
    # Modo direto (sem menu) se argumentos forem passados
    if len(sys.argv) > 1:
        args = sys.argv[1:]
        auto = "-y" in args or "--yes" in args
        stage_all = "--commit" not in args
        ia_commit(stage_all=stage_all, auto_confirm=auto)
        return

    check_git_repo()
    clear()

    print("\n  🐙  Git Commit Assistant — gca")
    print(f"  📁  {os.getcwd()}")

    while True:
        print("\n" + "─" * 52)
        show_status()
        print("  [1] 📝  Novo commit")
        print("  [2] 🚀  Push")
        print("  [3] ✏️   Editar script")
        print("  [4] ℹ️   Sobre")
        print("  [5] 👋  Sair")

        choice = input("\n  Escolha: ").strip()

        if choice == "1":
            commit_flow()
            clear()
            print("\n  🐙  Git Commit Assistant — gca")
            print(f"  📁  {os.getcwd()}")
        elif choice == "2":
            push()
        elif choice == "3":
            edit_script()
        elif choice == "4":
            about()
            clear()
            print("\n  🐙  Git Commit Assistant — gca")
            print(f"  📁  {os.getcwd()}")
        elif choice == "5":
            print("\n  👋  Até logo!\n")
            break
        else:
            print("  ❌  Opção inválida.")


if __name__ == "__main__":
    main()