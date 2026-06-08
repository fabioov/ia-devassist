"""Agente Recuperador - ia-devassist

Recupera trechos relevantes do banco vetorial a partir da pergunta do
usuario.
"""

import logging

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

from config import CHROMA_COLLECTION, CHROMA_DIR, EMBEDDING_MODEL, N_RESULTADOS

logger = logging.getLogger(__name__)


class AgenteRecuperador:
    """Busca contexto relevante no banco vetorial do projeto."""

    def __init__(self) -> None:
        """Inicializa a conexao com o banco vetorial.

        Args:
            Nenhum.

        Returns:
            None.
        """
        logger.info("Conectando ao banco vetorial em %s.", CHROMA_DIR)
        try:
            embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
            self.vectorstore = Chroma(
                persist_directory=str(CHROMA_DIR),
                embedding_function=embeddings,
                collection_name=CHROMA_COLLECTION,
            )
        except (OSError, RuntimeError, ValueError) as exc:
            raise RuntimeError(
                "Nao foi possivel conectar ao banco vetorial. Verifique se "
                "a indexacao foi executada com `python3 rag/indexar.py`."
            ) from exc

    def buscar(
        self,
        pergunta: str,
        fonte: str | None = None,
    ) -> list[dict[str, str]]:
        """Busca os chunks mais relevantes para a pergunta.

        Args:
            pergunta: Duvida enviada pelo usuario.
            fonte: Origem opcional para filtrar os resultados.

        Returns:
            Lista com texto, fonte e arquivo de cada contexto recuperado.
        """
        if not pergunta.strip():
            raise ValueError("A pergunta para busca nao pode estar vazia.")

        filtro = {"fonte": fonte} if fonte else None
        resultados = self.vectorstore.similarity_search(
            query=pergunta,
            k=N_RESULTADOS,
            filter=filtro,
        )
        return [
            {
                "texto": doc.page_content,
                "fonte": doc.metadata.get("fonte", "desconhecida"),
                "arquivo": doc.metadata.get("arquivo", "desconhecido"),
            }
            for doc in resultados
        ]

    def buscar_todos(self, pergunta: str) -> dict[str, list[dict[str, str]]]:
        """Busca contextos nas duas fontes indexadas.

        Args:
            pergunta: Duvida enviada pelo usuario.

        Returns:
            Dicionario com resultados separados por origem.
        """
        logger.info("Buscando contexto para a pergunta recebida.")
        docs = self.buscar(pergunta, fonte="docs_python")
        stackoverflow = self.buscar(pergunta, fonte="stackoverflow")
        logger.info(
            "Recuperacao concluida com %s resultado(s) da documentacao e "
            "%s do Stack Overflow.",
            len(docs),
            len(stackoverflow),
        )
        return {
            "docs_python": docs,
            "stackoverflow": stackoverflow,
        }
