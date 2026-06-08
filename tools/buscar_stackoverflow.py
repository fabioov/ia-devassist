"""
Tool: buscar_stackoverflow
Busca trechos relevantes nas perguntas do Stack Overflow indexadas.
"""

from agents.recuperador import AgenteRecuperador

_recuperador = None

def get_recuperador():
    global _recuperador
    if _recuperador is None:
        _recuperador = AgenteRecuperador()
    return _recuperador


def buscar_stackoverflow(query: str) -> list[dict]:
    """
    Busca os trechos mais relevantes no Stack Overflow (base local).

    Args:
        query: Pergunta ou termo a buscar.

    Returns:
        Lista de dicts com 'texto' e 'arquivo'.
    """
    recuperador = get_recuperador()
    resultados = recuperador.buscar(query, fonte="stackoverflow")
    return resultados


if __name__ == "__main__":
    resultados = buscar_stackoverflow("como usar generators em Python")
    for i, r in enumerate(resultados, 1):
        print(f"[{i}] {r['arquivo']}\n{r['texto'][:200]}\n")