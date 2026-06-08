"""Script de coleta de dados - ia-devassist

Baixa a documentacao oficial do Python e perguntas publicas do Stack
Overflow para montar a base local do projeto.
"""

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import requests
from requests import RequestException

from config import DOCS_DIR, SO_DIR

PYTHON_DOCS = {
    "built_in_functions": "https://docs.python.org/3/library/functions.html",
    "data_structures": "https://docs.python.org/3/tutorial/datastructures.html",
    "classes": "https://docs.python.org/3/tutorial/classes.html",
    "exceptions": "https://docs.python.org/3/tutorial/errors.html",
    "modules": "https://docs.python.org/3/tutorial/modules.html",
    "files_io": "https://docs.python.org/3/tutorial/inputoutput.html",
    "decorators": "https://docs.python.org/3/glossary.html",
    "list_comprehension": (
        "https://docs.python.org/3/tutorial/datastructures.html"
        "#list-comprehensions"
    ),
    "generators": "https://docs.python.org/3/tutorial/classes.html#generators",
    "context_managers": (
        "https://docs.python.org/3/reference/datamodel.html#context-managers"
    ),
}

TEMAS = [
    "list comprehension python",
    "decorator python",
    "exception handling python",
    "class inheritance python",
    "file read write python",
    "dictionary python",
    "lambda function python",
    "generator python",
    "context manager python",
    "virtual environment python",
]


def baixar_pagina(nome: str, url: str) -> None:
    """Baixa uma pagina HTML da documentacao do Python.

    Args:
        nome: Nome do arquivo de destino.
        url: URL da pagina a ser baixada.

    Returns:
        None.
    """
    print(f"  Baixando: {nome}...")
    try:
        resposta = requests.get(url, timeout=15)
        resposta.raise_for_status()
    except RequestException as exc:
        print(f"  ❌ Erro em {nome}: {exc}")
        return

    caminho = DOCS_DIR / f"{nome}.html"
    caminho.write_text(resposta.text, encoding="utf-8")
    print(f"  ✅ Salvo em {caminho}")


def buscar_stackoverflow(tema: str, max_resultados: int = 10) -> None:
    """Baixa perguntas publicas do Stack Overflow sobre um tema.

    Args:
        tema: Tema usado na consulta da API.
        max_resultados: Quantidade maxima de itens retornados.

    Returns:
        None.
    """
    url = "https://api.stackexchange.com/2.3/search/advanced"
    params = {
        "order": "desc",
        "sort": "votes",
        "q": tema,
        "tagged": "python",
        "site": "stackoverflow",
        "filter": "withbody",
        "pagesize": max_resultados,
    }

    print(f"  Buscando: '{tema}'...")
    try:
        resposta = requests.get(url, params=params, timeout=15)
        resposta.raise_for_status()
        dados = resposta.json()
    except RequestException as exc:
        print(f"  ❌ Erro em '{tema}': {exc}")
        return
    except ValueError as exc:
        print(f"  ❌ Resposta invalida da API para '{tema}': {exc}")
        return

    itens = [
        {
            "titulo": item.get("title", ""),
            "pergunta": item.get("body", ""),
            "tags": item.get("tags", []),
            "votos": item.get("score", 0),
            "link": item.get("link", ""),
        }
        for item in dados.get("items", [])
    ]
    caminho = SO_DIR / f"{tema.replace(' ', '_')}.json"
    caminho.write_text(
        json.dumps(itens, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"  ✅ {len(itens)} perguntas salvas em {caminho}")


def main() -> None:
    """Executa o download da documentacao e da base do Stack Overflow.

    Args:
        Nenhum.

    Returns:
        None.
    """
    DOCS_DIR.mkdir(exist_ok=True)
    SO_DIR.mkdir(exist_ok=True)

    print("\n📥 Baixando documentação do Python...")
    for nome, url in PYTHON_DOCS.items():
        baixar_pagina(nome, url)

    print("\n📥 Baixando perguntas do Stack Overflow...")
    for tema in TEMAS:
        buscar_stackoverflow(tema)

    docs_count = len(list(DOCS_DIR.glob("*.html")))
    so_count = len(list(SO_DIR.glob("*.json")))
    print(
        "\n✅ Base de conhecimento montada!\n"
        f"   📄 Documentação Python: {docs_count} arquivos em {DOCS_DIR}/\n"
        f"   💬 Stack Overflow:      {so_count} arquivos em {SO_DIR}/\n\n"
        "Próximo passo: execute `python3 rag/indexar.py` para gerar os "
        "embeddings.\n"
    )


if __name__ == "__main__":
    main()
