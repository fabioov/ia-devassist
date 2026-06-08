"""Configuracao centralizada - ia-devassist

Define caminhos, modelos e constantes compartilhadas por todo o projeto.
"""

from pathlib import Path

ROOT_DIR = Path(__file__).parent
DATA_DIR = ROOT_DIR / "data"
DOCS_DIR = DATA_DIR / "docs_python"
SO_DIR = DATA_DIR / "stackoverflow"
CHROMA_DIR = ROOT_DIR / "rag" / "chroma_db"
LLM_MODEL = "llama3.2:3b"
EMBEDDING_MODEL = "nomic-embed-text"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
N_RESULTADOS = 4
CHROMA_COLLECTION = "devassist"
HISTORICO_PATH = ROOT_DIR / "historico.json"
HISTORICO_MAX_EXIBIR = 5
MAX_TENTATIVAS_REVISOR = 2
