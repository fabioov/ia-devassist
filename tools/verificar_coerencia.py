"""
Tool: verificar_coerencia
Verifica se uma resposta é coerente com os contextos recuperados.
"""

from agents.revisor import AgenteRevisor

_revisor = None

def get_revisor():
    global _revisor
    if _revisor is None:
        _revisor = AgenteRevisor()
    return _revisor


def verificar_coerencia(resposta: str, contextos: dict) -> dict:
    """
    Verifica se a resposta gerada é coerente com os contextos.

    Args:
        resposta:  Texto gerado pelo Sintetizador.
        contextos: Dict com 'docs_python' e 'stackoverflow'.

    Returns:
        Dict com 'aprovado' (bool) e 'motivo' (str).
    """
    revisor = get_revisor()
    return revisor.revisar(resposta, contextos)


if __name__ == "__main__":
    resultado = verificar_coerencia(
        resposta="List comprehension é uma forma compacta de criar listas em Python.",
        contextos={
            "docs_python":   [{"texto": "list comprehension: A compact way to process all or part of the elements in a sequence.", "arquivo": "decorators"}],
            "stackoverflow": [],
        }
    )
    print(f"Aprovado: {resultado['aprovado']}")
    print(f"Motivo:   {resultado['motivo']}")