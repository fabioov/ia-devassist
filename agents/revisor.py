"""Agente Revisor - ia-devassist

Avalia se a resposta gerada esta coerente com os contextos
recuperados.
"""

import json
from json import JSONDecodeError
from typing import Dict, List, Union

from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM

from config import LLM_MODEL

PROMPT_REVISAO = """Você é um revisor técnico rigoroso.
Avalie se a RESPOSTA abaixo é coerente com os CONTEXTOS fornecidos.

Responda APENAS com um JSON no seguinte formato, sem texto adicional:
{{"aprovado": true ou false, "motivo": "explicacao curta"}}

=== CONTEXTOS ===
{contextos}

=== RESPOSTA A REVISAR ===
{resposta}

=== AVALIAÇÃO JSON ==="""


class AgenteRevisor:
    """Valida a coerencia entre a resposta e os contextos usados."""

    def __init__(self) -> None:
        """Inicializa o modelo usado para revisar respostas.

        Args:
            Nenhum.

        Returns:
            None.
        """
        try:
            self.llm = OllamaLLM(model=LLM_MODEL)
            self.prompt = PromptTemplate(
                input_variables=["contextos", "resposta"],
                template=PROMPT_REVISAO,
            )
            self.chain = self.prompt | self.llm
        except (OSError, RuntimeError, ValueError) as exc:
            raise RuntimeError(
                "Nao foi possivel inicializar o agente revisor. Verifique "
                "se o Ollama esta disponivel."
            ) from exc

    def _formatar_contextos(
        self,
        contextos: Dict[str, List[Dict[str, str]]],
    ) -> str:
        """Consolida os contextos em um unico bloco de texto."""
        partes: List[str] = []
        for contexto in contextos.get("docs_python", []):
            partes.append(contexto["texto"][:300])
        for contexto in contextos.get("stackoverflow", []):
            partes.append(contexto["texto"][:300])
        return "\n---\n".join(partes)

    def revisar(
        self,
        resposta: str,
        contextos: Dict[str, List[Dict[str, str]]],
    ) -> Dict[str, Union[bool, str]]:
        """Revisa a resposta gerada.

        Args:
            resposta: Texto gerado pelo sintetizador.
            contextos: Contextos agrupados por fonte.

        Returns:
            Dict com 'aprovado' e 'motivo'.
        """
        if not resposta.strip():
            raise ValueError("A resposta para revisao nao pode estar vazia.")

        contextos_texto = self._formatar_contextos(contextos)
        try:
            resultado_bruto = self.chain.invoke(
                {
                    "contextos": contextos_texto,
                    "resposta": resposta,
                }
            )
        except (OSError, RuntimeError, ValueError) as exc:
            raise RuntimeError(
                "Falha ao revisar a resposta com o modelo local. Tente "
                "novamente apos validar a disponibilidade do Ollama."
            ) from exc

        return self._interpretar_resultado(str(resultado_bruto))

    def _interpretar_resultado(
        self,
        resultado_bruto: str,
    ) -> Dict[str, Union[bool, str]]:
        """Interpreta o JSON retornado pelo modelo revisor."""
        try:
            return json.loads(resultado_bruto)
        except JSONDecodeError:
            inicio = resultado_bruto.find("{")
            fim = resultado_bruto.rfind("}") + 1
            if inicio == -1 or fim <= 0:
                return {
                    "aprovado": True,
                    "motivo": "Nao foi possivel avaliar automaticamente.",
                }

            try:
                return json.loads(resultado_bruto[inicio:fim])
            except (JSONDecodeError, TypeError, ValueError):
                return {
                    "aprovado": True,
                    "motivo": "Nao foi possivel avaliar automaticamente.",
                }
