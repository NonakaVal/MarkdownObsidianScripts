import time
import wave
import numpy as np
import whisper
from datetime import datetime
from pathlib import Path
import subprocess
import tempfile
import re


# ---------------------------------------
#  LISTAGEM E UTILIDADES
# ---------------------------------------

def listar_audios_recursivo(pasta: Path):
    exts = {'.mp3', '.wav', '.ogg', '.opus', '.m4a', '.mp4', '.flac'}
    return [p for p in pasta.rglob("*") if p.suffix.lower() in exts]


def has_audio_stream(path: Path) -> bool:
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a",
             "-show_entries", "stream=codec_type", "-of", "default=nw=1",
             str(path)],
            capture_output=True, text=True
        )
        return "codec_type=audio" in result.stdout
    except:
        return False


def converter_para_wav(arquivo: Path) -> Path:
    temp_file = Path(tempfile.gettempdir()) / f"{arquivo.stem}.wav"
    cmd = [
        "ffmpeg", "-y", "-i", str(arquivo),
        "-ac", "1", "-ar", "16000",
        "-vn",
        str(temp_file)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return temp_file


def wav_valido(wav_path: Path) -> bool:
    try:
        with wave.open(str(wav_path), "rb") as wav:
            nframes = wav.getnframes()
            rate = wav.getframerate()
            dur = nframes / float(rate)

            if dur < 0.2:
                return False

            audio = np.frombuffer(wav.readframes(nframes), dtype=np.int16)
            if np.all(audio == 0):
                return False

        return True

    except:
        return False


# ---------------------------------------
#  TRANSCRIÇÃO
# ---------------------------------------

def transcrever_audio(caminho_audio, modelo):
    wav_temp = converter_para_wav(caminho_audio)

    if not wav_valido(wav_temp):
        print("❌ Áudio inválido/silencioso → ignorado.")
        return None

    try:
        inicio = time.time()
        resultado = modelo.transcribe(str(wav_temp), fp16=False)
        print(f"✔️ Finalizado em {time.time() - inicio:.2f}s")
        return resultado["text"].strip()
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None


# ---------------------------------------
#  FRONTMATTER E MD
# ---------------------------------------

def gerar_frontmatter():
    hoje = datetime.now().strftime("%Y-%m-%d")
    return f"""---
created: "[[{hoje}]]"
tags:
  - transcriptions
---\n\n"""


def gerar_nome_arquivo_md():
    agora = datetime.now()
    return f"transcricoes_{agora:%Y-%m-%d_%H-%M-%S}.md"


# ---------------------------------------
#  NOVO: LER ARQUIVOS JÁ TRANSCRITOS
# ---------------------------------------

def carregar_transcricoes_existentes(md_path: Path):
    if not md_path.exists():
        return set()

    padrao = r"### 🎧 (.+?)\n"
    texto = md_path.read_text(encoding="utf-8")

    encontrados = re.findall(padrao, texto)
    return set(encontrados)


# ---------------------------------------
#  PROCESSAMENTO GERAL
# ---------------------------------------

def processar_todos_audios():
    caminho_audios = Path(input("📂 Caminho dos áudios: ").strip()).resolve()
    caminho_saida = Path(input("📁 Caminho da pasta de saída: ").strip()).resolve()
    modelo_nome = input("🤖 Modelo Whisper (ex: tiny, base, small, medium): ").strip() or "medium"

    # Arquivo MD opcional (para evitar duplicações)
    md_existente = input("📄 Caminho de um .md já existente (ou deixe vazio): ").strip()
    md_existente = Path(md_existente).resolve() if md_existente else None

    audios = listar_audios_recursivo(caminho_audios)
    total = len(audios)
    print(f"\n📥 {total} arquivos encontrados (recursivo).")

    modelo = whisper.load_model(modelo_nome)
    print("Modelo carregado.")

    caminho_saida.mkdir(parents=True, exist_ok=True)
    md_path = caminho_saida / gerar_nome_arquivo_md()

    # Carregar nomes já transcritos
    ja_transcritos = set()
    if md_existente and md_existente.exists():
        ja_transcritos = carregar_transcricoes_existentes(md_existente)
        print(f"📌 {len(ja_transcritos)} áudios já transcritos serão ignorados.")

    # Agrupar por pastas
    grupos = {}
    for audio in audios:
        rel = audio.parent.relative_to(caminho_audios)
        grupos.setdefault(str(rel), []).append(audio)

    with open(md_path, "w", encoding="utf-8") as md:
        md.write(gerar_frontmatter())

        contador = 0

        for pasta, arquivos in grupos.items():
            md.write(f"## 📁 {pasta}\n\n")

            for audio in arquivos:
                contador += 1

                # VERIFICAÇÃO NOVA
                if audio.name in ja_transcritos:
                    print(f"⏭️ Ignorando (já transcrito): {audio.name}")
                    continue

                print(f"\n({contador}/{total}) ▶️ Transcrevendo: {audio.name}")

                texto = transcrever_audio(audio, modelo)

                if texto:
                    md.write(f"### 🎧 {audio.name}\n\n")
                    md.write(texto + "\n\n---\n\n")

    print(f"\n📄 Arquivo salvo em:\n{md_path}")


if __name__ == "__main__":
    processar_todos_audios()
