"""Servidor MCP - ia-devassist

Centraliza o registro e a execucao das tools internas do projeto.
"""

from typing import Any, Callable, Dict, List, Union

from tools.salvar_historico import listar_historico, salvar_historico

ToolFunction = Callable[..., Any]


class ServidorMCP:
    """Registra e executa tools usando agentes ja inicializados."""

    def __init__(self) -> None:
        """Inicializa a estrutura interna do servidor MCP.

        Args:
            Nenhum.

        Returns:
            None.
        """
        self._recuperador: Any = None
        self._sintetizador: Any = None
        self._revisor: Any = None
        self._tools: Dict[str, Dict[str, Any]] = {}

    def init(self, recuperador: Any, sintetizador: Any, revisor: Any) -> None:
        """Recebe instancias prontas dos agentes e registra as tools.

        Args:
            recuperador: Agente de recuperacao inicializado.
            sintetizador: Agente de sintese inicializado.
            revisor: Agente de revisao inicializado.

        Returns:
            None.
        """
        self._recuperador = recuperador
        self._sintetizador = sintetizador
        self._revisor = revisor
        self._registrar_tools()

    def _registrar_tools(self) -> None:
        """Registra as tools disponiveis no servidor."""
        self._tools = {
            "buscar_documentacao": {
                "descricao": "Busca trechos relevantes na documentacao.",
                "parametros": ["query"],
                "funcao": self._buscar_documentacao,
            },
            "buscar_stackoverflow": {
                "descricao": "Busca trechos relevantes no Stack Overflow.",
                "parametros": ["query"],
                "funcao": self._buscar_stackoverflow,
            },
            "verificar_coerencia": {
                "descricao": "Verifica a coerencia entre resposta e contexto.",
                "parametros": ["resposta", "contextos"],
                "funcao": self._verificar_coerencia,
            },
            "salvar_historico": {
                "descricao": "Salva uma entrada no historico local.",
                "parametros": ["pergunta", "resposta"],
                "funcao": salvar_historico,
            },
            "listar_historico": {
                "descricao": "Lista as entradas do historico local.",
                "parametros": [],
                "funcao": listar_historico,
            },
        }

    def _buscar_documentacao(self, query: str) -> List[Dict[str, str]]:
        """Executa a busca na documentacao oficial."""
        if self._recuperador is None:
            raise RuntimeError("Agente recuperador nao foi inicializado.")
        return self._recuperador.buscar(query, fonte="docs_python")

    def _buscar_stackoverflow(self, query: str) -> List[Dict[str, str]]:
        """Executa a busca na base local do Stack Overflow."""
        if self._recuperador is None:
            raise RuntimeError("Agente recuperador nao foi inicializado.")
        return self._recuperador.buscar(query, fonte="stackoverflow")

    def _verificar_coerencia(
        self,
        resposta: str,
        contextos: Dict[str, List[Dict[str, str]]],
    ) -> Dict[str, Union[bool, str]]:
        """Executa a revisao de coerencia com o agente revisor."""
        if self._revisor is None:
            raise RuntimeError("Agente revisor nao foi inicializado.")
        return self._revisor.revisar(resposta, contextos)

    def listar_tools(self) -> List[Dict[str, Any]]:
        """Lista os metadados das tools registradas.

        Args:
            Nenhum.

        Returns:
            Lista com nome, descricao e parametros de cada tool.
        """
        return [
            {
                "nome": nome,
                "descricao": info["descricao"],
                "parametros": info["parametros"],
            }
            for nome, info in self._tools.items()
        ]

    def executar(self, nome_tool: str, parametros: Dict[str, Any]) -> Dict[str, Any]:
        """Executa uma tool registrada com os parametros informados.

        Args:
            nome_tool: Nome da tool registrada.
            parametros: Parametros esperados pela tool.

        Returns:
            Resultado padronizado com sucesso, erro ou payload.
        """
        if not self._tools:
            return {
                "sucesso": False,
                "erro": (
                    "Servidor MCP nao inicializado. Chame `init()` antes de "
                    "usar as tools."
                ),
            }

        if nome_tool not in self._tools:
            return {
                "sucesso": False,
                "erro": (
                    f"Tool '{nome_tool}' nao encontrada. Disponiveis: "
                    f"{list(self._tools.keys())}"
                ),
            }

        info_tool = self._tools[nome_tool]
        esperados = set(info_tool["parametros"])
        recebidos = set(parametros)
        faltantes = esperados - recebidos
        excedentes = recebidos - esperados

        if faltantes:
            return {
                "sucesso": False,
                "erro": (
                    f"Parametros ausentes para '{nome_tool}': "
                    f"{sorted(faltantes)}"
                ),
            }
        if excedentes:
            return {
                "sucesso": False,
                "erro": (
                    f"Parametros inesperados para '{nome_tool}': "
                    f"{sorted(excedentes)}"
                ),
            }

        funcao: ToolFunction = info_tool["funcao"]
        try:
            resultado = funcao(**parametros)
        except (RuntimeError, TypeError, ValueError, OSError) as exc:
            return {"sucesso": False, "erro": str(exc)}

        return {"sucesso": True, "resultado": resultado}


servidor_mcp = ServidorMCP()
