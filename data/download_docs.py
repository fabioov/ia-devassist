"""
Script para montar a base de conhecimento do ia-devassist.
Baixa documentação do Python e perguntas do Stack Overflow (Python).

Execute: python data/baixar_docs.py
"""

import os
import json
import requests
from pathlib import Path

# Pastas de destino
BASE_DIR = Path(__file__).parent
DOCS_DIR = BASE_DIR / "docs_python"
SO_DIR   = BASE_DIR / "stackoverflow"

DOCS_DIR.mkdir(exist_ok=True)
SO_DIR.mkdir(exist_ok=True)


# ─────────────────────────────────────────────
# 1. DOCUMENTAÇÃO OFICIAL DO PYTHON (texto puro)
# ─────────────────────────────────────────────

PYTHON_DOCS = {
    "built_in_functions": "https://docs.python.org/3/library/functions.html",
    "data_structures":    "https://docs.python.org/3/tutorial/datastructures.html",
    "classes":            "https://docs.python.org/3/tutorial/classes.html",
    "exceptions":         "https://docs.python.org/3/tutorial/errors.html",
    "modules":            "https://docs.python.org/3/tutorial/modules.html",
    "files_io":           "https://docs.python.org/3/tutorial/inputoutput.html",
    "decorators":         "https://docs.python.org/3/glossary.html",
    "list_comprehension": "https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions",
    "generators":         "https://docs.python.org/3/tutorial/classes.html#generators",
    "context_managers":   "https://docs.python.org/3/reference/datamodel.html#context-managers",
}

def baixar_pagina(nome, url):
    """Baixa uma página HTML e salva o texto limpo."""
    try:
        print(f"  Baixando: {nome}...")
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()

        # Salva HTML bruto — o LangChain vai extrair o texto depois
        caminho = DOCS_DIR / f"{nome}.html"
        caminho.write_text(resp.text, encoding="utf-8")
        print(f"  ✅ Salvo em {caminho}")
    except Exception as e:
        print(f"  ❌ Erro em {nome}: {e}")

print("\n📥 Baixando documentação do Python...")
for nome, url in PYTHON_DOCS.items():
    baixar_pagina(nome, url)


# ─────────────────────────────────────────────
# 2. STACK OVERFLOW — API pública (sem autenticação)
#    Busca perguntas populares de Python
# ─────────────────────────────────────────────

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

def buscar_stackoverflow(tema, max_resultados=10):
    """Busca perguntas + respostas aceitas no Stack Overflow via API pública."""
    url = "https://api.stackexchange.com/2.3/search/advanced"
    params = {
        "order":    "desc",
        "sort":     "votes",
        "q":        tema,
        "tagged":   "python",
        "site":     "stackoverflow",
        "filter":   "withbody",
        "pagesize": max_resultados,
    }

    try:
        print(f"  Buscando: '{tema}'...")
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        dados = resp.json()

        itens = []
        for item in dados.get("items", []):
            itens.append({
                "titulo":    item.get("title", ""),
                "pergunta":  item.get("body", ""),
                "tags":      item.get("tags", []),
                "votos":     item.get("score", 0),
                "link":      item.get("link", ""),
            })

        # Salva como JSON
        nome_arquivo = tema.replace(" ", "_") + ".json"
        caminho = SO_DIR / nome_arquivo
        caminho.write_text(json.dumps(itens, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  ✅ {len(itens)} perguntas salvas em {caminho}")

    except Exception as e:
        print(f"  ❌ Erro em '{tema}': {e}")

print("\n📥 Baixando perguntas do Stack Overflow...")
for tema in TEMAS:
    buscar_stackoverflow(tema)


# ─────────────────────────────────────────────
# RESUMO FINAL
# ─────────────────────────────────────────────

docs_count = len(list(DOCS_DIR.glob("*.html")))
so_count   = len(list(SO_DIR.glob("*.json")))

print(f"""
✅ Base de conhecimento montada!
   📄 Documentação Python: {docs_count} arquivos em data/docs_python/
   💬 Stack Overflow:      {so_count} arquivos em data/stackoverflow/

Próximo passo: execute python rag/indexar.py para gerar os embeddings.
""")