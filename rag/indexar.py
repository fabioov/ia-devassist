"""
Script de indexação da base de conhecimento do ia-devassist.
Lê os arquivos em data/, gera embeddings e salva no ChromaDB.

Execute: python3 rag/indexar.py
"""

import json
from pathlib import Path

from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

# ── Caminhos ──────────────────────────────────
BASE_DIR    = Path(__file__).parent.parent
DATA_DIR    = BASE_DIR / "data"
DOCS_DIR    = DATA_DIR / "docs_python"
SO_DIR      = DATA_DIR / "stackoverflow"
CHROMA_DIR  = Path(__file__).parent / "chroma_db"

# ── Configuração ──────────────────────────────
EMBEDDING_MODEL = "nomic-embed-text"
CHUNK_SIZE      = 500
CHUNK_OVERLAP   = 50


def extrair_texto_html(caminho: Path) -> str:
    """Extrai texto limpo de um arquivo HTML."""
    html = caminho.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    # Remove scripts e estilos
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)


def extrair_texto_json(caminho: Path) -> str:
    """Extrai texto de um arquivo JSON do Stack Overflow."""
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    textos = []
    for item in dados:
        titulo   = item.get("titulo", "")
        pergunta = BeautifulSoup(item.get("pergunta", ""), "html.parser").get_text()
        textos.append(f"Pergunta: {titulo}\n{pergunta}")
    return "\n\n---\n\n".join(textos)


def main():
    print("🚀 Iniciando indexação da base de conhecimento...\n")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

    todos_chunks = []
    todos_metadados = []

    # ── 1. Documentação Python ─────────────────
    print("📄 Processando documentação do Python...")
    for arquivo in sorted(DOCS_DIR.glob("*.html")):
        texto = extrair_texto_html(arquivo)
        chunks = splitter.split_text(texto)
        for chunk in chunks:
            todos_chunks.append(chunk)
            todos_metadados.append({
                "fonte": "docs_python",
                "arquivo": arquivo.stem,
            })
        print(f"   ✅ {arquivo.stem} → {len(chunks)} chunks")

    # ── 2. Stack Overflow ──────────────────────
    print("\n💬 Processando perguntas do Stack Overflow...")
    for arquivo in sorted(SO_DIR.glob("*.json")):
        texto = extrair_texto_json(arquivo)
        chunks = splitter.split_text(texto)
        for chunk in chunks:
            todos_chunks.append(chunk)
            todos_metadados.append({
                "fonte": "stackoverflow",
                "arquivo": arquivo.stem,
            })
        print(f"   ✅ {arquivo.stem} → {len(chunks)} chunks")

    # ── 3. Salva no ChromaDB ───────────────────
    print(f"\n🔢 Gerando embeddings para {len(todos_chunks)} chunks...")
    print("   (isso pode levar alguns minutos na primeira vez)\n")

    vectorstore = Chroma.from_texts(
        texts=todos_chunks,
        embedding=embeddings,
        metadatas=todos_metadados,
        persist_directory=str(CHROMA_DIR),
        collection_name="devassist",
    )

    print(f"""
✅ Indexação concluída!
   Total de chunks indexados: {len(todos_chunks)}
   Banco vetorial salvo em:   rag/chroma_db/

Próximo passo: python3 main.py
""")


if __name__ == "__main__":
    main()