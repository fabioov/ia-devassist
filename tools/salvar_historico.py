"""
Tool: salvar_historico
Salva a pergunta e resposta em um arquivo local de histórico.
"""

import json
from datetime import datetime
from pathlib import Path

HISTORICO_PATH = Path(__file__).parent.parent / "historico.json"


def salvar_historico(pergunta: str, resposta: str) -> dict:
    """
    Salva a pergunta e resposta no histórico local.

    Args:
        pergunta: A dúvida do usuário.
        resposta: A resposta gerada pelo sistema.

    Returns:
        Dict com 'sucesso' (bool) e 'total_entradas' (int).
    """
    historico = []

    if HISTORICO_PATH.exists():
        try:
            historico = json.loads(HISTORICO_PATH.read_text(encoding="utf-8"))
        except Exception:
            historico = []

    entrada = {
        "data":     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "pergunta": pergunta,
        "resposta": resposta,
    }

    historico.append(entrada)
    HISTORICO_PATH.write_text(json.dumps(historico, ensure_ascii=False, indent=2), encoding="utf-8")

    return {"sucesso": True, "total_entradas": len(historico)}


def listar_historico() -> list[dict]:
    """Retorna todas as entradas do histórico."""
    if not HISTORICO_PATH.exists():
        return []
    try:
        return json.loads(HISTORICO_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []


if __name__ == "__main__":
    resultado = salvar_historico(
        pergunta="Como usar list comprehension?",
        resposta="List comprehension é uma forma compacta de criar listas..."
    )
    print(f"Salvo! Total de entradas: {resultado['total_entradas']}")
    print(f"Arquivo: {HISTORICO_PATH}")