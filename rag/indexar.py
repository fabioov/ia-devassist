"""Script de indexacao - ia-devassist

Le os dados locais, gera embeddings e persiste a base vetorial.
"""

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

from config import (
    CHROMA_COLLECTION,
    CHROMA_DIR,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    DOCS_DIR,
    EMBEDDING_MODEL,
    SO_DIR,
)


def extrair_texto_html(caminho: Path) -> str:
    """Extrai texto limpo de um arquivo HTML.

    Args:
        caminho: Caminho do arquivo HTML.

    Returns:
        Texto limpo pronto para indexacao.
    """
    html = caminho.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)


def extrair_texto_json(caminho: Path) -> str:
    """Extrai texto consolidado de um arquivo JSON do Stack Overflow.

    Args:
        caminho: Caminho do arquivo JSON.

    Returns:
        Texto combinado das perguntas indexadas.
    """
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    textos: list[str] = []
    for item in dados:
        titulo = item.get("titulo", "")
        pergunta = BeautifulSoup(item.get("pergunta", ""), "html.parser").get_text()
        textos.append(f"Pergunta: {titulo}\n{pergunta}")
    return "\n\n---\n\n".join(textos)


def main() -> None:
    """Executa a indexacao completa da base de conhecimento.

    Args:
        Nenhum.

    Returns:
        None.
    """
    print("🚀 Iniciando indexação da base de conhecimento...\n")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    todos_chunks: list[str] = []
    todos_metadados: list[dict[str, str]] = []

    print("📄 Processando documentação do Python...")
    for arquivo in sorted(DOCS_DIR.glob("*.html")):
        texto = extrair_texto_html(arquivo)
        chunks = splitter.split_text(texto)
        for chunk in chunks:
            todos_chunks.append(chunk)
            todos_metadados.append(
                {
                    "fonte": "docs_python",
                    "arquivo": arquivo.stem,
                }
            )
        print(f"   ✅ {arquivo.stem} -> {len(chunks)} chunks")

    print("\n💬 Processando perguntas do Stack Overflow...")
    for arquivo in sorted(SO_DIR.glob("*.json")):
        texto = extrair_texto_json(arquivo)
        chunks = splitter.split_text(texto)
        for chunk in chunks:
            todos_chunks.append(chunk)
            todos_metadados.append(
                {
                    "fonte": "stackoverflow",
                    "arquivo": arquivo.stem,
                }
            )
        print(f"   ✅ {arquivo.stem} -> {len(chunks)} chunks")

    print(f"\n🔢 Gerando embeddings para {len(todos_chunks)} chunks...")
    print("   (isso pode levar alguns minutos na primeira vez)\n")

    Chroma.from_texts(
        texts=todos_chunks,
        embedding=embeddings,
        metadatas=todos_metadados,
        persist_directory=str(CHROMA_DIR),
        collection_name=CHROMA_COLLECTION,
    )

    print(
        "\n✅ Indexação concluída!\n"
        f"   Total de chunks indexados: {len(todos_chunks)}\n"
        f"   Banco vetorial salvo em:   {CHROMA_DIR}\n\n"
        "Próximo passo: python3 main.py\n"
    )


if __name__ == "__main__":
    main()
