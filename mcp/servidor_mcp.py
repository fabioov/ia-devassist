"""
Servidor MCP — ia-devassist
Expõe as tools dos agentes via Model Context Protocol.
Recebe as instâncias dos agentes já inicializadas para evitar
múltiplas instanciações desnecessárias.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class ServidorMCP:
    """
    Servidor MCP que padroniza o acesso às tools.
    Recebe os agentes já inicializados via init().
    """

    def __init__(self):
        self._recuperador  = None
        self._sintetizador = None
        self._revisor      = None
        self._tools        = {}

    def init(self, recuperador, sintetizador, revisor):
        """Recebe as instâncias já criadas e registra as tools."""
        self._recuperador  = recuperador
        self._sintetizador = sintetizador
        self._revisor      = revisor
        self._registrar_tools()

    def _registrar_tools(self):
        from tools.salvar_historico import salvar_historico, listar_historico

        self._tools = {
            "buscar_documentacao": {
                "descricao":  "Busca trechos relevantes na documentação oficial do Python.",
                "parametros": ["query"],
                "funcao":     lambda query: self._recuperador.buscar(query, fonte="docs_python"),
            },
            "buscar_stackoverflow": {
                "descricao":  "Busca trechos relevantes no Stack Overflow (base local).",
                "parametros": ["query"],
                "funcao":     lambda query: self._recuperador.buscar(query, fonte="stackoverflow"),
            },
            "verificar_coerencia": {
                "descricao":  "Verifica se uma resposta é coerente com os contextos recuperados.",
                "parametros": ["resposta", "contextos"],
                "funcao":     lambda resposta, contextos: self._revisor.revisar(resposta, contextos),
            },
            "salvar_historico": {
                "descricao":  "Salva a pergunta e resposta no histórico local.",
                "parametros": ["pergunta", "resposta"],
                "funcao":     salvar_historico,
            },
            "listar_historico": {
                "descricao":  "Lista todas as entradas do histórico.",
                "parametros": [],
                "funcao":     listar_historico,
            },
        }

    def listar_tools(self) -> list[dict]:
        return [
            {"nome": nome, "descricao": info["descricao"], "parametros": info["parametros"]}
            for nome, info in self._tools.items()
        ]

    def executar(self, nome_tool: str, parametros: dict) -> dict:
        if not self._tools:
            return {"sucesso": False, "erro": "Servidor MCP não inicializado. Chame init() primeiro."}

        if nome_tool not in self._tools:
            return {
                "sucesso": False,
                "erro": f"Tool '{nome_tool}' não encontrada. Disponíveis: {list(self._tools.keys())}",
            }

        try:
            funcao    = self._tools[nome_tool]["funcao"]
            resultado = funcao(**parametros)
            return {"sucesso": True, "resultado": resultado}
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}


# Instância global
servidor_mcp = ServidorMCP()