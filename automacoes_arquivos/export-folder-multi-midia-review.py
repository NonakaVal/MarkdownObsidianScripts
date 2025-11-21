# -*- coding: utf-8 -*-
"""
index_midias_simples.py
Versão simplificada - gera listas limpas de mídias agrupadas por pasta.
Foca em nomes amigáveis sem informações técnicas.
"""

from __future__ import annotations
import os
import sys
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import argparse

MAIN_PATH = r"/mnt/windows/all/imagens/"

################################## Configuração ##################################

# Pastas para ignorar
PASTAS_IGNORAR = {".obsidian", ".git", "__pycache__", ".vscode"}

# Regex para limpar nomes de pastas
REGEX_PASTAS = [
    (r'your_instagram_activity/messages/inbox/([^_]+)_.*', r'\1'),  # allanajackselin_467949104603254 -> allanajackselin
    (r'your_instagram_activity/messages/inbox/(.+)', r'\1'),        # outros padrões de inbox
    (r'your_instagram_activity/(.+)', r'\1'),                       # remove your_instagram_activity/
    (r'([^/]+)/.*', r'\1'),                                         # pega apenas primeiro nível
]

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".heic", ".tiff", ".svg"}
VIDEO_EXT = { ".mov", ".mkv", ".webm", ".avi", ".flv", ".m4v"}
AUDIO_EXT = {".mp4",".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"}

################################## Utilitários ##################################

def deve_ignorar_pasta(nome_pasta: str) -> bool:
    """Verifica se a pasta deve ser ignorada."""
    return any(pasta_ignorar in nome_pasta for pasta_ignorar in PASTAS_IGNORAR)

def limpar_nome_pasta(nome_pasta: str) -> str:
    """Limpa o nome da pasta usando regex patterns."""
    if not nome_pasta or nome_pasta == '':
        return "📁 Raiz Principal"
    
    for pattern, replacement in REGEX_PASTAS:
        try:
            novo_nome = re.sub(pattern, replacement, nome_pasta)
            if novo_nome != nome_pasta:
                return novo_nome
        except:
            continue
    
    # Se não match em nenhum regex, retorna o último segmento
    if '/' in nome_pasta:
        return nome_pasta.split('/')[-1]
    return nome_pasta

def categorizar_arquivo(nome_arquivo: str) -> str:
    """Categoriza arquivo de forma simples."""
    ext = Path(nome_arquivo).suffix.lower()
    if ext in IMAGE_EXT:
        return "🖼️ Imagens"
    elif ext in VIDEO_EXT:
        return "🎬 Vídeos" 
    elif ext in AUDIO_EXT:
        return "🔊 Áudios"
    else:
        return "📄 Outros"

def obter_emoji_categoria(categoria: str) -> str:
    """Retorna emoji baseado na categoria."""
    emojis = {
        "🖼️ Imagens": "🖼️",
        "🎬 Vídeos": "🎬", 
        "🔊 Áudios": "🔊",
        "📄 Outros": "📄"
    }
    return emojis.get(categoria, "📄")

def formatar_link_obsidian(item: dict) -> str:
    """Formata o link para o Obsidian com ![[ ]] para mídias."""
    caminho = item['caminho_relativo']
    nome = item['nome']
    ext = Path(nome).suffix.lower()
    
    # Para imagens, vídeos e áudios usa ![[ ]]
    if ext in IMAGE_EXT | VIDEO_EXT | AUDIO_EXT:
        return f"![[{caminho}]]"
    else:
        # Para outros arquivos usa [[ ]] normal
        return f"[[{caminho}]]"

################################## Varredura ##################################

def scan_diretorio_simples(root: Path) -> dict:
    """
    Varre diretório e retorna estrutura simplificada.
    """
    root = root.resolve()
    conteudo_por_pasta = defaultdict(lambda: defaultdict(list))
    
    for dirpath, dirnames, filenames in os.walk(root):
        # Ignorar pastas específicas
        if deve_ignorar_pasta(dirpath):
            continue
            
        rel_dir = os.path.relpath(dirpath, root)
        if rel_dir == '.':
            rel_dir = ''
            
        nome_pasta_limpo = limpar_nome_pasta(rel_dir)
        
        for fname in filenames:
            file_path = Path(dirpath) / fname
            try:
                if not file_path.exists():
                    continue
                    
                categoria = categorizar_arquivo(fname)
                rel_path = os.path.relpath(file_path, root).replace(os.sep, '/')
                
                item = {
                    "nome": fname,
                    "caminho_relativo": rel_path
                }
                
                conteudo_por_pasta[nome_pasta_limpo][categoria].append(item)
                
            except Exception:
                continue
    
    return dict(conteudo_por_pasta)

################################## Geração da Lista ##################################

def gerar_lista_simples(conteudo_por_pasta: dict, output_path: Path) -> None:
    """
    Gera lista limpa e organizada em Markdown.
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 📸 Lista de Mídias - Instagram\n\n")
        f.write(f"*Atualizado em {datetime.now().strftime('%d/%m/%Y')}*\n\n")
        
        # Lista de Pastas Encontradas
        f.write("## 📂 Pastas Encontradas\n\n")
        pastas_ordenadas = sorted(conteudo_por_pasta.keys())
        
        for pasta in pastas_ordenadas:
            emoji = "📁" if pasta != "📁 Raiz Principal" else "🏠"
            f.write(f"- {emoji} **{pasta}**\n")
        f.write("\n---\n\n")
        
        # Conteúdo de Cada Pasta
        for pasta in pastas_ordenadas:
            conteudo = conteudo_por_pasta[pasta]
            
            if not any(conteudo.values()):
                continue
                
            f.write(f"## 📁 {pasta}\n\n")
            
            # Ordenar categorias: Imagens, Vídeos, Áudios, Outros
            ordem_categorias = ["🖼️ Imagens", "🎬 Vídeos", "🔊 Áudios", "📄 Outros"]
            
            for categoria in ordem_categorias:
                itens = conteudo.get(categoria, [])
                if not itens:
                    continue
                
                emoji = obter_emoji_categoria(categoria)
                f.write(f"### {emoji} {categoria.replace('️', '')} ({len(itens)})\n\n")
                
                # Layout diferente para cada categoria
                if categoria == "🖼️ Imagens":
                    # Grid para imagens
                    f.write("<div style='display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; margin: 20px 0;'>\n")
                    for item in sorted(itens, key=lambda x: x["nome"]):
                        link = formatar_link_obsidian(item)
                        f.write(f"<div style='text-align: center;'>{link}<br><small>{item['nome'][:20]}...</small></div>\n")
                    f.write("</div>\n\n")
                    
                elif categoria == "🎬 Vídeos":
                    # Lista com preview para vídeos
                    for item in sorted(itens, key=lambda x: x["nome"]):
                        link = formatar_link_obsidian(item)
                        f.write(f"{link}\n")
                        f.write(f"**Arquivo:** {item['nome']}\n\n")
                    
                elif categoria == "🔊 Áudios":
                    # Lista para áudios
                    for item in sorted(itens, key=lambda x: x["nome"]):
                        link = formatar_link_obsidian(item)
                        f.write(f"{link}\n")
                        f.write(f"**Arquivo:** {item['nome']}\n\n")
                    
                else:
                    # Lista simples para outros arquivos
                    for item in sorted(itens, key=lambda x: x["nome"]):
                        link = formatar_link_obsidian(item)
                        f.write(f"- {link}\n")
                
                f.write("\n")
            
            f.write("---\n\n")
        
        # Resumo Final
        f.write("## 📊 Resumo\n\n")
        total_pastas = len(conteudo_por_pasta)
        total_arquivos = sum(len(itens) for categorias in conteudo_por_pasta.values() 
                           for itens in categorias.values())
        
        f.write(f"- **Pastas com conteúdo:** {total_pastas}\n")
        f.write(f"- **Total de arquivos:** {total_arquivos}\n")
        f.write(f"- **Data da exportação:** {datetime.now().strftime('%d/%m/%Y')}\n")
        f.write(f"- **Pastas ignoradas:** {', '.join(sorted(PASTAS_IGNORAR))}\n")

    print(f"✅ Lista gerada: {output_path}")

################################## Execução ##################################

def main():
    parser = argparse.ArgumentParser(description="Gera lista limpa de mídias do Instagram")
    parser.add_argument("--pasta", "-p", type=str, default=None, help="Pasta para varrer")
    parser.add_argument("--saida", "-s", type=str, default="lista_midias.md", help="Arquivo de saída")
    
    args = parser.parse_args()
    
    if args.pasta:
        root = Path(args.pasta)
    elif MAIN_PATH:
        root = Path(MAIN_PATH)
    else:
        root = Path.cwd()

    output_path = Path(args.saida)
    if not output_path.is_absolute():
        output_path = root / output_path

    print(f"🔍 Varrendo pasta: {root}")
    print(f"🚫 Ignorando pastas: {', '.join(PASTAS_IGNORAR)}")
    conteudo = scan_diretorio_simples(root)
    
    print("📝 Gerando lista...")
    gerar_lista_simples(conteudo, output_path)
    
    # Mostrar resumo
    total_pastas = len(conteudo)
    total_arquivos = sum(len(itens) for categorias in conteudo.values() 
                       for itens in categorias.values())
    
    print(f"✅ Pronto!")
    print(f"   📁 Pastas encontradas: {total_pastas}")
    print(f"   📊 Arquivos listados: {total_arquivos}")
    print(f"   📄 Saída: {output_path}")

if __name__ == "__main__":
    main()