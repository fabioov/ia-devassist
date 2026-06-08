"""Tool salvar_historico - ia-devassist

Persiste e recupera o historico local de perguntas e respostas.
"""

import json
import logging
from datetime import datetime
from json import JSONDecodeError
from typing import Dict, List, Union

from config import HISTORICO_PATH

logger = logging.getLogger(__name__)


def _carregar_historico() -> List[Dict[str, str]]:
    """Carrega o historico do disco quando disponivel."""
    if not HISTORICO_PATH.exists():
        return []

    try:
        return json.loads(HISTORICO_PATH.read_text(encoding="utf-8"))
    except JSONDecodeError as exc:
        logger.warning(
            "Historico invalido em %s. Um novo arquivo sera criado.",
            HISTORICO_PATH,
        )
        raise ValueError(
            "O arquivo de historico esta corrompido. Remova-o ou corrija "
            "o JSON antes de continuar."
        ) from exc
    except OSError as exc:
        raise RuntimeError(
            "Nao foi possivel ler o arquivo de historico. Verifique as "
            "permissoes do projeto."
        ) from exc


def salvar_historico(
    pergunta: str,
    resposta: str,
) -> Dict[str, Union[int, bool]]:
    """Salva uma nova entrada no historico local.

    Args:
        pergunta: Pergunta enviada pelo usuario.
        resposta: Resposta gerada pelo sistema.

    Returns:
        Resultado da operacao com sucesso e total de entradas.
    """
    if not pergunta.strip():
        raise ValueError("A pergunta do historico nao pode estar vazia.")
    if not resposta.strip():
        raise ValueError("A resposta do historico nao pode estar vazia.")

    historico: List[Dict[str, str]] = []
    if HISTORICO_PATH.exists():
        try:
            historico = _carregar_historico()
        except ValueError:
            logger.warning(
                "Historico existente sera reiniciado por conter JSON invalido."
            )
            historico = []

    historico.append(
        {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "pergunta": pergunta,
            "resposta": resposta,
        }
    )

    try:
        HISTORICO_PATH.write_text(
            json.dumps(historico, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except OSError as exc:
        raise RuntimeError(
            "Nao foi possivel salvar o historico. Verifique espaco em "
            "disco e permissoes de escrita."
        ) from exc

    return {"sucesso": True, "total_entradas": len(historico)}


def listar_historico() -> List[Dict[str, str]]:
    """Lista todas as entradas do historico local.

    Args:
        Nenhum.

    Returns:
        Lista de entradas do historico.
    """
    try:
        return _carregar_historico()
    except ValueError:
        logger.warning(
            "Historico invalido detectado durante listagem. "
            "Retornando lista vazia."
        )
        return []
