# PyBox

Coleção de scripts Python organizados em módulos para rodar a partir de um menu central no terminal.

## Estrutura

- `pybox.py`: menu principal para escolher módulos e scripts
- `config.py`: define os módulos, caminhos e configurações globais do projeto
- `requirements.txt`: dependências básicas do ambiente
- `modules/`: scripts agrupados em pastas como `audio`, `file_tools`, `gallery_tools`, `index_notes`, `manga_reader`, `obsidian_tools`, `shell_tools`

## Setup

1. Entre na pasta do projeto:
   `cd /home/val/Github/PyBox`
2. Crie e ative um ambiente virtual (opcional, mas recomendado):
   `python3 -m venv .venv`
   `source .venv/bin/activate`
3. Instale as dependências básicas:
   `pip install -r requirements.txt`

### Dependências adicionais para recursos de áudio

Alguns módulos de áudio e transcrição precisam de pacotes extras, como `openai-whisper` e `torch`. Eles podem ser instalados separadamente quando necessário:

```bash
pip install openai-whisper torch
```

Além disso, o projeto depende de ferramentas de sistema como `ffmpeg` e `ffprobe` para processamento de áudio.

## Uso

1. Execute `python3 pybox.py`
2. Selecione um módulo
3. Escolha um script para rodar

## Configuração da API Gemini

O módulo de commit assistido usa as variáveis abaixo, definidas em `config.py`:

- `GEMINI_API_KEY`
- `GEMINI_MODEL`
- `GEMINI_API_URL`

Você pode definir a chave da API no ambiente antes de executar o script:

```bash
export GEMINI_API_KEY="sua_chave"
```

## Ambiente

O `pybox.py` exporta variáveis de ambiente antes de executar cada script:

- `PYBOX_ROOT`
- `PYBOX_MODULES`
- `PYBOX_SCRIPT`
- `PYBOX_CALL_DIR`
