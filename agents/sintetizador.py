"""Agente Sintetizador - ia-devassist

Gera a resposta final a partir da pergunta do usuario e dos contextos
recuperados.
"""

from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM

from config import LLM_MODEL

PROMPT_TEMPLATE = """Você é um assistente técnico especializado em programação Python.
Use apenas os contextos abaixo para responder a pergunta do usuário.
Responda em português, de forma clara e didática.
Se possível, inclua um exemplo de código.
Se os contextos não forem suficientes para responder, diga que não encontrou informação suficiente.

=== CONTEXTOS DA DOCUMENTAÇÃO OFICIAL ===
{contexto_docs}

=== CONTEXTOS DO STACK OVERFLOW ===
{contexto_so}

=== PERGUNTA DO USUÁRIO ===
{pergunta}

=== RESPOSTA ==="""


class AgenteSintetizador:
    """Gera respostas com base nos contextos recuperados."""

    def __init__(self) -> None:
        """Inicializa o modelo de linguagem e o prompt da cadeia.

        Args:
            Nenhum.

        Returns:
            None.
        """
        try:
            self.llm = OllamaLLM(model=LLM_MODEL)
            self.prompt = PromptTemplate(
                input_variables=["contexto_docs", "contexto_so", "pergunta"],
                template=PROMPT_TEMPLATE,
            )
            self.chain = self.prompt | self.llm
        except (OSError, RuntimeError, ValueError) as exc:
            raise RuntimeError(
                "Nao foi possivel inicializar o modelo local. Verifique se "
                "o Ollama esta em execucao e se o modelo configurado existe."
            ) from exc

    def _formatar_contextos(self, contextos: list[dict[str, str]]) -> str:
        """Formata os contextos para o prompt do modelo."""
        if not contextos:
            return "Nenhum contexto encontrado."

        partes: list[str] = []
        for indice, contexto in enumerate(contextos, 1):
            partes.append(
                f"[{indice}] ({contexto['arquivo']})\n"
                f"{contexto['texto'][:600]}"
            )
        return "\n\n".join(partes)

    def gerar(
        self,
        pergunta: str,
        contextos: dict[str, list[dict[str, str]]],
    ) -> str:
        """Gera uma resposta com base na pergunta e nos contextos.

        Args:
            pergunta: Duvida enviada pelo usuario.
            contextos: Contextos agrupados por fonte.

        Returns:
            Resposta gerada pelo LLM como string.
        """
        if not pergunta.strip():
            raise ValueError("A pergunta para geracao nao pode estar vazia.")

        contexto_docs = self._formatar_contextos(
            contextos.get("docs_python", [])
        )
        contexto_so = self._formatar_contextos(
            contextos.get("stackoverflow", [])
        )

        try:
            resposta = self.chain.invoke(
                {
                    "contexto_docs": contexto_docs,
                    "contexto_so": contexto_so,
                    "pergunta": pergunta,
                }
            )
        except (OSError, RuntimeError, ValueError) as exc:
            raise RuntimeError(
                "Falha ao gerar resposta com o modelo local. Verifique a "
                "disponibilidade do Ollama e tente novamente."
            ) from exc

        return str(resposta).strip()
