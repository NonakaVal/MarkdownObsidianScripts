#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
EXTRATOR ZIP COM PRESERVAÇÃO TOTAL DA ESTRUTURA
-----------------------------------------------
• Mantém toda a estrutura original de pastas do ZIP.
• Extrai apenas arquivos únicos (hash SHA-256).
• Coloca arquivos únicos exatamente na mesma pasta original.
• Se há conflito de nome e o arquivo for diferente → cria variações nomeadas.
• Se o arquivo for igual → ignora duplicata real.
"""

import os
import zipfile
import hashlib
from pathlib import Path
import shutil


# ---------------------------------------------------------
# HASH
# ---------------------------------------------------------

def sha256sum(file_path: Path) -> str:
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------
# EXTRAÇÃO SEGURA
# ---------------------------------------------------------

def safe_extract(zip_file: zipfile.ZipFile, member: str, temp_root: Path) -> Path:
    """
    Extrai manualmente garantindo preservação total dos caminhos.
    Corrige problemas de separadores e caminhos profundos.
    """
    member = member.replace("\\", "/")

    dest_path = temp_root / member

    if member.endswith("/"):
        dest_path.mkdir(parents=True, exist_ok=True)
        return None

    dest_path.parent.mkdir(parents=True, exist_ok=True)

    with zip_file.open(member) as src, open(dest_path, "wb") as dst:
        shutil.copyfileobj(src, dst)

    return dest_path


# ---------------------------------------------------------
# EXTRAÇÃO PRINCIPAL
# ---------------------------------------------------------

def extract_preserving_structure(zip_path: Path, dest: Path, hash_db: dict):
    print(f"\n📦 Processando ZIP: {zip_path}")

    temp_root = dest / "_temp_extract"
    temp_root.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as z:

        for member in z.namelist():

            try:
                temp_file = safe_extract(z, member, temp_root)

                if temp_file is None or not temp_file.exists() or temp_file.is_dir():
                    continue

                file_hash = sha256sum(temp_file)

                # É duplicata real → ignorar
                if file_hash in hash_db:
                    print(f"⚠️ Duplicata ignorada: {member}")
                    temp_file.unlink()
                    continue

                hash_db[file_hash] = member

                # Caminho exato do arquivo pela estrutura original
                final_path = dest / member
                final_path.parent.mkdir(parents=True, exist_ok=True)

                # Conflito de nome dentro da mesma pasta → renomear mantendo pasta
                if final_path.exists():
                    stem, ext = final_path.stem, final_path.suffix
                    counter = 1
                    new_path = final_path

                    while new_path.exists():
                        new_path = final_path.parent / f"{stem}_{counter}{ext}"
                        counter += 1

                    final_path = new_path

                shutil.move(str(temp_file), str(final_path))
                print(f"✔️ Extraído: {final_path}")

            except Exception as e:
                print(f"❌ Erro ao processar {member}: {e}")

    shutil.rmtree(temp_root, ignore_errors=True)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():
    print("\n=== EXTRATOR ZIP — PRESERVAÇÃO DE ESTRUTURA ===\n")

    zip_dir = Path(input("📁 Caminho contendo os arquivos .zip: ").strip())
    dest_dir = Path(input("📂 Caminho destino da extração: ").strip())

    dest_dir.mkdir(parents=True, exist_ok=True)

    hash_db = {}

    zip_files = list(zip_dir.rglob("*.zip"))
    print(f"\n🔍 Encontrados {len(zip_files)} arquivos ZIP para processar.\n")

    for z in zip_files:
        extract_preserving_structure(z, dest_dir, hash_db)

    print("\n🎉 Finalizado! Toda a estrutura foi preservada e só arquivos únicos foram extraídos.\n")


if __name__ == "__main__":
    main()
