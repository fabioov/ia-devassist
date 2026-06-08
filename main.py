"""
ia-devassist — Assistente Técnico de Programação
Interface de terminal (CLI) que orquestra os três agentes.

Execute: python3 main.py
"""

import sys
from pathlib import Path

# ── Banner ────────────────────────────────────
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

def limpar_tela():
    import os
    os.system("clear" if os.name == "posix" else "cls")

def mostrar_historico():
    from tools.salvar_historico import listar_historico
    entradas = listar_historico()
    if not entradas:
        print("\n📭 Nenhuma pergunta no histórico ainda.\n")
        return
    print(f"\n📚 Histórico — {len(entradas)} pergunta(s):\n")
    for i, entrada in enumerate(entradas[-5:], 1):  # mostra as últimas 5
        print(f"[{i}] {entrada['data']}")
        print(f"     Pergunta: {entrada['pergunta']}")
        print()

def processar_pergunta(pergunta: str, recuperador, sintetizador, revisor) -> str:
    """Orquestra o fluxo completo: Recuperador → Sintetizador → Revisor."""
    from mcp.servidor_mcp import servidor_mcp

    # ── Passo 1: Recuperar contexto via MCP ───
    resultado = servidor_mcp.executar("buscar_documentacao", {"query": pergunta})
    docs = resultado["resultado"] if resultado["sucesso"] else []

    resultado = servidor_mcp.executar("buscar_stackoverflow", {"query": pergunta})
    so = resultado["resultado"] if resultado["sucesso"] else []

    contextos = {"docs_python": docs, "stackoverflow": so}

    # ── Passo 2: Sintetizar resposta ──────────
    resposta = sintetizador.gerar(pergunta, contextos)

    # ── Passo 3: Revisar coerência via MCP ────
    resultado = servidor_mcp.executar("verificar_coerencia", {
        "resposta":  resposta,
        "contextos": contextos,
    })

    avaliacao = resultado.get("resultado", {"aprovado": True, "motivo": ""})

    # Se reprovado, tenta uma vez mais
    if not avaliacao.get("aprovado", True):
        print("\n⚠️  Revisor solicitou nova geração...\n")
        resposta = sintetizador.gerar(pergunta, contextos)

    # ── Passo 4: Salvar no histórico via MCP ──
    servidor_mcp.executar("salvar_historico", {
        "pergunta": pergunta,
        "resposta": resposta,
    })

    return resposta


def main():
    limpar_tela()
    print(BANNER)

    # ── Inicializa os agentes ─────────────────
    print("⏳ Inicializando agentes...\n")
    try:
        from agents.recuperador  import AgenteRecuperador
        from agents.sintetizador import AgenteSintetizador
        from agents.revisor      import AgenteRevisor

        recuperador  = AgenteRecuperador()
        sintetizador = AgenteSintetizador()
        revisor      = AgenteRevisor()
    except Exception as e:
        print(f"❌ Erro ao inicializar agentes: {e}")
        print("Verifique se o Ollama está rodando e o banco vetorial foi indexado.")
        sys.exit(1)

    print("✅ Agentes prontos! Pode fazer sua pergunta.\n")
    print("─" * 48)

    # ── Loop principal ────────────────────────
    while True:
        try:
            pergunta = input("\n🧑 Você: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Encerrando ia-devassist. Até mais!\n")
            break

        if not pergunta:
            continue

        # Comandos especiais
        if pergunta.lower() == "sair":
            print("\n👋 Encerrando ia-devassist. Até mais!\n")
            break
        elif pergunta.lower() == "historico":
            mostrar_historico()
            continue
        elif pergunta.lower() == "limpar":
            limpar_tela()
            print(BANNER)
            continue

        # Processa a pergunta
        print()
        try:
            resposta = processar_pergunta(pergunta, recuperador, sintetizador, revisor)
            print("\n🤖 ia-devassist:")
            print("─" * 48)
            print(resposta)
            print("─" * 48)
        except Exception as e:
            print(f"\n❌ Erro ao processar pergunta: {e}")
            print("Tente novamente ou verifique se o Ollama está rodando.\n")


if __name__ == "__main__":
    main()
