"""Tool verificar_coerencia - ia-devassist

Valida se a resposta gerada esta coerente com os contextos
recuperados.
"""

import logging
from typing import Dict, List, Optional, Union

from agents.revisor import AgenteRevisor

logger = logging.getLogger(__name__)

_revisor: Optional[AgenteRevisor] = None


def get_revisor() -> AgenteRevisor:
    """Retorna uma instancia singleton do agente revisor.

    Args:
        Nenhum.

    Returns:
        Instancia pronta do agente revisor.
    """
    global _revisor
    if _revisor is None:
        logger.info("Criando instancia singleton do agente revisor.")
        _revisor = AgenteRevisor()
    return _revisor


def verificar_coerencia(
    resposta: str,
    contextos: Dict[str, List[Dict[str, str]]],
) -> Dict[str, Union[bool, str]]:
    """Verifica se a resposta gerada e coerente com os contextos.

    Args:
        resposta: Texto gerado pelo sintetizador.
        contextos: Contextos agrupados por fonte.

    Returns:
        Resultado da revisao com aprovacao e motivo.
    """
    return get_revisor().revisar(resposta, contextos)
