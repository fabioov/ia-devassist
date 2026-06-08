"""
Tool: buscar_documentacao
Busca trechos relevantes na documentação oficial do Python.
"""

from agents.recuperador import AgenteRecuperador

_recuperador = None

def get_recuperador():
    global _recuperador
    if _recuperador is None:
        _recuperador = AgenteRecuperador()
    return _recuperador


def buscar_documentacao(query: str) -> list[dict]:
    """
    Busca os trechos mais relevantes na documentação oficial do Python.

    Args:
        query: Pergunta ou termo a buscar.

    Returns:
        Lista de dicts com 'texto' e 'arquivo'.
    """
    recuperador = get_recuperador()
    resultados = recuperador.buscar(query, fonte="docs_python")
    return resultados


if __name__ == "__main__":
    resultados = buscar_documentacao("decorators em Python")
    for i, r in enumerate(resultados, 1):
        print(f"[{i}] {r['arquivo']}\n{r['texto'][:200]}\n")