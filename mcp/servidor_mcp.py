"""
Servidor MCP — ia-devassist
Expõe as tools dos agentes via Model Context Protocol.
Os agentes acessam as ferramentas através deste servidor,
mantendo a comunicação padronizada e desacoplada.
"""

import json
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.buscar_documentacao import buscar_documentacao
from tools.buscar_stackoverflow import buscar_stackoverflow
from tools.verificar_coerencia  import verificar_coerencia
from tools.salvar_historico     import salvar_historico, listar_historico

# ── Registro de tools disponíveis ─────────────
TOOLS = {
    "buscar_documentacao": {
        "descricao": "Busca trechos relevantes na documentação oficial do Python.",
        "parametros": ["query"],
        "funcao":     buscar_documentacao,
    },
    "buscar_stackoverflow": {
        "descricao": "Busca trechos relevantes no Stack Overflow (base local).",
        "parametros": ["query"],
        "funcao":     buscar_stackoverflow,
    },
    "verificar_coerencia": {
        "descricao": "Verifica se uma resposta é coerente com os contextos recuperados.",
        "parametros": ["resposta", "contextos"],
        "funcao":     verificar_coerencia,
    },
    "salvar_historico": {
        "descricao": "Salva a pergunta e resposta no histórico local.",
        "parametros": ["pergunta", "resposta"],
        "funcao":     salvar_historico,
    },
    "listar_historico": {
        "descricao": "Lista todas as entradas do histórico.",
        "parametros": [],
        "funcao":     listar_historico,
    },
}


class ServidorMCP:
    """
    Servidor MCP simples que padroniza o acesso às tools.
    Implementa o padrão de comunicação agente ↔ ferramentas.
    """

    def listar_tools(self) -> list[dict]:
        """Retorna a lista de tools disponíveis."""
        return [
            {"nome": nome, "descricao": info["descricao"], "parametros": info["parametros"]}
            for nome, info in TOOLS.items()
        ]

    def executar(self, nome_tool: str, parametros: dict) -> dict:
        """
        Executa uma tool pelo nome com os parâmetros fornecidos.

        Args:
            nome_tool:  Nome da tool a executar.
            parametros: Dict com os parâmetros da tool.

        Returns:
            Dict com 'sucesso' (bool) e 'resultado' ou 'erro'.
        """
        if nome_tool not in TOOLS:
            return {
                "sucesso": False,
                "erro": f"Tool '{nome_tool}' não encontrada. Disponíveis: {list(TOOLS.keys())}",
            }

        try:
            funcao = TOOLS[nome_tool]["funcao"]
            resultado = funcao(**parametros)
            return {"sucesso": True, "resultado": resultado}
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}


# ── Instância global do servidor ──────────────
servidor_mcp = ServidorMCP()


if __name__ == "__main__":
    print("🔗 Servidor MCP — ia-devassist")
    print("=" * 40)

    print("\n📋 Tools disponíveis:")
    for tool in servidor_mcp.listar_tools():
        print(f"  • {tool['nome']}: {tool['descricao']}")

    print("\n🧪 Testando buscar_documentacao...")
    resultado = servidor_mcp.executar(
        "buscar_documentacao",
        {"query": "exception handling Python"}
    )
    if resultado["sucesso"]:
        print(f"  ✅ Retornou {len(resultado['resultado'])} resultados")
    else:
        print(f"  ❌ Erro: {resultado['erro']}")

    print("\n🧪 Testando salvar_historico...")
    resultado = servidor_mcp.executar(
        "salvar_historico",
        {"pergunta": "Teste MCP", "resposta": "Funcionando!"}
    )
    print(f"  ✅ {resultado}")

    print("\n✅ Servidor MCP funcionando corretamente!")