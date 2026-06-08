"""
Agente Recuperador — ia-devassist
Responsável por buscar os trechos mais relevantes no banco vetorial
a partir da pergunta do usuário.
"""

from pathlib import Path
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

# ── Configuração ──────────────────────────────
CHROMA_DIR      = Path(__file__).parent.parent / "rag" / "chroma_db"
EMBEDDING_MODEL = "nomic-embed-text"
N_RESULTADOS    = 4  # quantos chunks retornar por busca


class AgenteRecuperador:
    """
    Agente responsável pela recuperação de contexto relevante.
    Busca no banco vetorial (ChromaDB) os trechos mais similares
    à pergunta do usuário.
    """

    def __init__(self):
        print("[Recuperador] Conectando ao banco vetorial...")
        embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
        self.vectorstore = Chroma(
            persist_directory=str(CHROMA_DIR),
            embedding_function=embeddings,
            collection_name="devassist",
        )
        print("[Recuperador] Pronto.\n")

    def buscar(self, pergunta: str, fonte: str = None) -> list[dict]:
        """
        Busca os chunks mais relevantes para a pergunta.

        Args:
            pergunta: A dúvida do usuário.
            fonte: Filtrar por 'docs_python' ou 'stackoverflow' (opcional).

        Returns:
            Lista de dicts com 'texto', 'fonte' e 'arquivo'.
        """
        filtro = {"fonte": fonte} if fonte else None

        resultados = self.vectorstore.similarity_search(
            query=pergunta,
            k=N_RESULTADOS,
            filter=filtro,
        )

        contextos = []
        for doc in resultados:
            contextos.append({
                "texto":   doc.page_content,
                "fonte":   doc.metadata.get("fonte", "desconhecida"),
                "arquivo": doc.metadata.get("arquivo", "desconhecido"),
            })

        return contextos

    def buscar_todos(self, pergunta: str) -> dict:
        """
        Busca em todas as fontes e retorna separado por origem.

        Returns:
            Dict com chaves 'docs_python' e 'stackoverflow'.
        """
        print(f"[Recuperador] Buscando contexto para: '{pergunta}'")

        docs = self.buscar(pergunta, fonte="docs_python")
        so   = self.buscar(pergunta, fonte="stackoverflow")

        print(f"[Recuperador] Encontrado: {len(docs)} da documentação, {len(so)} do Stack Overflow.")

        return {
            "docs_python":   docs,
            "stackoverflow": so,
        }


# ── Teste rápido ──────────────────────────────
if __name__ == "__main__":
    agente = AgenteRecuperador()
    resultados = agente.buscar_todos("Como usar list comprehension em Python?")

    print("\n── Resultados da Documentação ──")
    for i, ctx in enumerate(resultados["docs_python"], 1):
        print(f"\n[{i}] Arquivo: {ctx['arquivo']}")
        print(ctx["texto"][:300] + "...")

    print("\n── Resultados do Stack Overflow ──")
    for i, ctx in enumerate(resultados["stackoverflow"], 1):
        print(f"\n[{i}] Arquivo: {ctx['arquivo']}")
        print(ctx["texto"][:300] + "...")