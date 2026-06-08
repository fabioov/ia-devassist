"""
ia-devassist — Assistente Técnico de Programação
Interface de terminal (CLI) que orquestra os três agentes.

Execute: python3 main.py
"""

import sys
import os

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
    os.system("clear" if os.name == "posix" else "cls")

def mostrar_historico(servidor_mcp):
    resultado = servidor_mcp.executar("listar_historico", {})
    entradas  = resultado.get("resultado", []) if resultado["sucesso"] else []
    if not entradas:
        print("\n📭 Nenhuma pergunta no histórico ainda.\n")
        return
    print(f"\n📚 Histórico — {len(entradas)} pergunta(s):\n")
    for i, entrada in enumerate(entradas[-5:], 1):
        print(f"[{i}] {entrada['data']}")
        print(f"     {entrada['pergunta']}")
        print()

def processar_pergunta(pergunta: str, sintetizador, servidor_mcp) -> str:
    """Orquestra o fluxo: Recuperador → Sintetizador → Revisor via MCP."""

    # Passo 1: Recuperar contexto via MCP
    r_docs = servidor_mcp.executar("buscar_documentacao", {"query": pergunta})
    r_so   = servidor_mcp.executar("buscar_stackoverflow", {"query": pergunta})

    contextos = {
        "docs_python":   r_docs["resultado"] if r_docs["sucesso"] else [],
        "stackoverflow": r_so["resultado"]   if r_so["sucesso"]   else [],
    }

    # Passo 2: Sintetizar resposta
    resposta = sintetizador.gerar(pergunta, contextos)

    # Passo 3: Revisar coerência via MCP
    r_rev     = servidor_mcp.executar("verificar_coerencia", {"resposta": resposta, "contextos": contextos})
    avaliacao = r_rev.get("resultado", {"aprovado": True}) if r_rev["sucesso"] else {"aprovado": True}

    # Se reprovado, tenta uma vez mais
    if not avaliacao.get("aprovado", True):
        print("\n⚠️  Revisor solicitou nova geração...\n")
        resposta = sintetizador.gerar(pergunta, contextos)

    # Passo 4: Salvar no histórico via MCP
    servidor_mcp.executar("salvar_historico", {"pergunta": pergunta, "resposta": resposta})

    return resposta


def main():
    limpar_tela()
    print(BANNER)

    # Inicializa os agentes uma única vez
    print("⏳ Inicializando agentes...\n")
    try:
        from agents.recuperador  import AgenteRecuperador
        from agents.sintetizador import AgenteSintetizador
        from agents.revisor      import AgenteRevisor
        from mcp.servidor_mcp   import servidor_mcp

        recuperador  = AgenteRecuperador()
        sintetizador = AgenteSintetizador()
        revisor      = AgenteRevisor()

        # Injeta as instâncias no servidor MCP — sem recriação!
        servidor_mcp.init(recuperador, sintetizador, revisor)

    except Exception as e:
        print(f"❌ Erro ao inicializar: {e}")
        print("Verifique se o Ollama está rodando e o banco vetorial foi indexado.")
        sys.exit(1)

    print("✅ Agentes prontos! Pode fazer sua pergunta.\n")
    print("─" * 48)

    # Loop principal
    while True:
        try:
            pergunta = input("\n🧑 Você: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Encerrando ia-devassist. Até mais!\n")
            break

        if not pergunta:
            continue

        if pergunta.lower() == "sair":
            print("\n👋 Encerrando ia-devassist. Até mais!\n")
            break
        elif pergunta.lower() == "historico":
            mostrar_historico(servidor_mcp)
            continue
        elif pergunta.lower() == "limpar":
            limpar_tela()
            print(BANNER)
            continue

        print()
        try:
            resposta = processar_pergunta(pergunta, sintetizador, servidor_mcp)
            print("\n🤖 ia-devassist:")
            print("─" * 48)
            print(resposta)
            print("─" * 48)
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            print("Tente novamente ou verifique se o Ollama está rodando.\n")


if __name__ == "__main__":
    main()