"""CLI principal - ia-devassist

Orquestra a interface de terminal e a execucao dos agentes via MCP.
"""

import logging
import os
import subprocess
import sys
from typing import Any

from config import HISTORICO_MAX_EXIBIR, MAX_TENTATIVAS_REVISOR

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

BANNER = """
╔══════════════════════════════════════════════╗
║       🤖  ia-devassist  v1.0               ║
║   Assistente Técnico de Programação         ║
║   Powered by LLaMA 3.2 + RAG + MCP         ║
╚══════════════════════════════════════════════╝
Digite sua dúvida técnica sobre Python.
Comandos especiais:
  historico  → ver perguntas anteriores
  limpar     → limpar a tela
  sair       → encerrar o programa
"""


def limpar_tela() -> None:
    """Limpa a tela do terminal.

    Args:
        Nenhum.

    Returns:
        None.
    """
    comando = ["clear"] if os.name == "posix" else ["cmd", "/c", "cls"]
    subprocess.run(comando, check=False)


def mostrar_historico(servidor_mcp: Any) -> None:
    """Exibe as entradas mais recentes do historico.

    Args:
        servidor_mcp: Instancia do servidor MCP inicializado.

    Returns:
        None.
    """
    resultado = servidor_mcp.executar("listar_historico", {})
    entradas = resultado.get("resultado", []) if resultado["sucesso"] else []
    if not entradas:
        print("\n📭 Nenhuma pergunta no histórico ainda.\n")
        return

    print(f"\n📚 Histórico — {len(entradas)} pergunta(s):\n")
    for indice, entrada in enumerate(entradas[-HISTORICO_MAX_EXIBIR:], 1):
        print(f"[{indice}] {entrada['data']}")
        print(f"     {entrada['pergunta']}")
        print()


def processar_pergunta(
    pergunta: str,
    sintetizador: Any,
    servidor_mcp: Any,
) -> str:
    """Processa uma pergunta com recuperacao, sintese e revisao.

    Args:
        pergunta: Duvida enviada pelo usuario.
        sintetizador: Instancia do agente sintetizador.
        servidor_mcp: Instancia do servidor MCP inicializado.

    Returns:
        Resposta final gerada para o usuario.
    """
    if not pergunta.strip():
        raise ValueError("A pergunta nao pode estar vazia.")

    resultado_docs = servidor_mcp.executar(
        "buscar_documentacao",
        {"query": pergunta},
    )
    resultado_so = servidor_mcp.executar(
        "buscar_stackoverflow",
        {"query": pergunta},
    )

    contextos = {
        "docs_python": (
            resultado_docs["resultado"] if resultado_docs["sucesso"] else []
        ),
        "stackoverflow": (
            resultado_so["resultado"] if resultado_so["sucesso"] else []
        ),
    }

    resposta = sintetizador.gerar(pergunta, contextos)
    for tentativa in range(1, MAX_TENTATIVAS_REVISOR + 1):
        resultado_revisao = servidor_mcp.executar(
            "verificar_coerencia",
            {"resposta": resposta, "contextos": contextos},
        )
        avaliacao = (
            resultado_revisao.get("resultado", {"aprovado": True})
            if resultado_revisao["sucesso"]
            else {"aprovado": True}
        )
        if avaliacao.get("aprovado", True):
            break
        if tentativa >= MAX_TENTATIVAS_REVISOR:
            logger.warning(
                "Resposta permaneceu reprovada apos %s tentativa(s).",
                tentativa,
            )
            break
        print("\n⚠️  Revisor solicitou nova geração...\n")
        resposta = sintetizador.gerar(pergunta, contextos)

    resultado_historico = servidor_mcp.executar(
        "salvar_historico",
        {"pergunta": pergunta, "resposta": resposta},
    )
    if not resultado_historico["sucesso"]:
        logger.warning(
            "Falha ao salvar historico: %s",
            resultado_historico["erro"],
        )

    return resposta


def main() -> None:
    """Inicializa a aplicacao e executa o loop principal.

    Args:
        Nenhum.

    Returns:
        None.
    """
    limpar_tela()
    print(BANNER)
    print("⏳ Inicializando agentes...\n")

    try:
        from agents.recuperador import AgenteRecuperador
        from agents.revisor import AgenteRevisor
        from agents.sintetizador import AgenteSintetizador
        from mcp.servidor_mcp import servidor_mcp

        recuperador = AgenteRecuperador()
        sintetizador = AgenteSintetizador()
        revisor = AgenteRevisor()
        servidor_mcp.init(recuperador, sintetizador, revisor)
    except (ImportError, RuntimeError, ValueError) as exc:
        print(f"❌ Erro ao inicializar: {exc}")
        print(
            "Verifique se o Ollama esta rodando e se a base foi indexada "
            "com `python3 rag/indexar.py`."
        )
        sys.exit(1)

    print("✅ Agentes prontos! Pode fazer sua pergunta.\n")
    print("─" * 48)

    while True:
        try:
            pergunta = input("\n🧑 Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 Encerrando ia-devassist. Até mais!\n")
            break

        if not pergunta:
            continue
        if pergunta.lower() == "sair":
            print("\n👋 Encerrando ia-devassist. Até mais!\n")
            break
        if pergunta.lower() == "historico":
            mostrar_historico(servidor_mcp)
            continue
        if pergunta.lower() == "limpar":
            limpar_tela()
            print(BANNER)
            continue

        print()
        try:
            resposta = processar_pergunta(pergunta, sintetizador, servidor_mcp)
        except (RuntimeError, ValueError) as exc:
            print(f"\n❌ Erro: {exc}")
            print(
                "Tente novamente ou verifique se o Ollama esta rodando "
                "corretamente.\n"
            )
            continue

        print("\n🤖 ia-devassist:")
        print("─" * 48)
        print(resposta)
        print("─" * 48)


if __name__ == "__main__":
    main()
