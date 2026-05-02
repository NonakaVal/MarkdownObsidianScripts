# -*- coding: utf-8 -*-
import os
import sys
from collections import defaultdict

# 🔹 CAMINHO ÚNICO
BASE_PATH = "/home/val/Documentos/Notes/Knowlegde/33 Concept"





EXTS_IMAGEM = [".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".base",".md"]
EXT_MD = ".md"

NOME_RAIZ = os.path.basename(BASE_PATH.rstrip(os.sep))

if not os.path.exists(BASE_PATH):
    print(f"Erro: a pasta '{BASE_PATH}' não existe!")
    sys.exit(1)

# Estrutura: { pasta_relativa: [links...] }
estrutura = defaultdict(list)

for root, _, files in os.walk(BASE_PATH):
    pasta_rel = os.path.relpath(root, BASE_PATH)
    pasta_rel = "" if pasta_rel == "." else pasta_rel.replace("\\", "/")

    for f in files:
        ext = os.path.splitext(f)[1].lower()

        # ---------- MARKDOWN ----------
        if ext == EXT_MD:
            nome_base = os.path.splitext(f)[0]
            estrutura[pasta_rel].append(nome_base)

        # ---------- IMAGENS ----------
        elif ext in EXTS_IMAGEM:
            estrutura[pasta_rel].append(f)

# ---------- OUTPUT PARA OBSIDIAN ----------
for pasta in sorted(estrutura.keys()):
    nivel = 1 if pasta == "" else pasta.count("/") + 1
    header = "#" * nivel

    if pasta:
        titulo = pasta.split("/")[-1]
        print(f"\n{header} {titulo}")
    else:
        print(f"\n# {NOME_RAIZ}")

    for link in sorted(estrutura[pasta]):
        print(f"- [[{link}]]")



""""

# -*- coding: utf-8 -*-
import os
import sys
from collections import defaultdict
from config import VAULT_PATH


VAULT_PATH = "/home/val/Github/Pro-Vault/"

PASTA_ARQUIVOS = os.path.join(
    VAULT_PATH,
    r"X/Templates/Forma")



EXTS_IMAGEM = [".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".base"]
EXT_MD = ".md"


NOME_RAIZ = os.path.basename(PASTA_ARQUIVOS.rstrip(os.sep))

if not os.path.exists(PASTA_ARQUIVOS):
    print(f"Erro: a pasta '{PASTA_ARQUIVOS}' não existe!")
    sys.exit(1)


# Estrutura: { pasta_relativa: [links...] }
estrutura = defaultdict(list)

for root, _, files in os.walk(PASTA_ARQUIVOS):
    pasta_rel = os.path.relpath(root, PASTA_ARQUIVOS)
    pasta_rel = "" if pasta_rel == "." else pasta_rel.replace("\\", "/")

    for f in files:
        ext = os.path.splitext(f)[1].lower()

        # ---------- MARKDOWN ----------
        if ext == EXT_MD:
            nome_base = os.path.splitext(f)[0]
            estrutura[pasta_rel].append(nome_base)

        # ---------- IMAGENS ----------
        elif ext in EXTS_IMAGEM:
            estrutura[pasta_rel].append(f)


# ---------- OUTPUT PARA OBSIDIAN ----------
for pasta in sorted(estrutura.keys()):
    nivel = 1 if pasta == "" else pasta.count("/") + 1
    header = "#" * nivel

    if pasta:
        titulo = pasta.split("/")[-1]
        print(f"\n{header} {titulo}")
    else:
        # raiz agora usa o nome real da pasta
        print(f"\n# {NOME_RAIZ}")

    for link in sorted(estrutura[pasta]):
        print(f"- [[{link}]]")

"""


"""

# -*- coding: utf-8 -*-
import os
import sys
from config import VAULT_PATH

PASTA_ARQUIVOS = os.path.join(
    VAULT_PATH,
    r"06 Work/01 Drafts"
)

EXTS_IMAGEM = [".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"]
EXT_MD = ".md"

if not os.path.exists(PASTA_ARQUIVOS):
    print(f"Erro: a pasta '{PASTA_ARQUIVOS}' não existe!")
    sys.exit(1)

links = []

for root, _, files in os.walk(PASTA_ARQUIVOS):
    for f in files:
        ext = os.path.splitext(f)[1].lower()

        # ---------- MARKDOWN ----------
        if ext == EXT_MD:
            nome_base = os.path.splitext(f)[0]  # remove .md
            links.append(nome_base)

        # ---------- IMAGENS ----------
        elif ext in EXTS_IMAGEM:
            caminho_completo = os.path.join(root, f)
            caminho_relativo = os.path.relpath(caminho_completo, VAULT_PATH)
            caminho_relativo = caminho_relativo.replace("\\", "/")
            links.append(caminho_relativo)

# Output Obsidian
for link in sorted(links):
    print(f"- [[{link}]]")
"""

