"""Tool buscar_documentacao - ia-devassist

Busca trechos relevantes na documentacao oficial do Python.
"""

import logging
from typing import Dict, List, Optional

from agents.recuperador import AgenteRecuperador

logger = logging.getLogger(__name__)

_recuperador: Optional[AgenteRecuperador] = None


def get_recuperador() -> AgenteRecuperador:
    """Retorna uma instancia singleton do agente recuperador.

    Args:
        Nenhum.

    Returns:
        Instancia pronta do agente recuperador.
    """
    global _recuperador
    if _recuperador is None:
        logger.info("Criando instancia singleton do agente recuperador.")
        _recuperador = AgenteRecuperador()
    return _recuperador


def buscar_documentacao(query: str) -> List[Dict[str, str]]:
    """Busca trechos relevantes na documentacao oficial do Python.

    Args:
        query: Pergunta ou termo a buscar.

    Returns:
        Lista de contextos encontrados na documentacao oficial.
    """
    return get_recuperador().buscar(query, fonte="docs_python")
