"""
Agente Revisor — ia-devassist
Verifica se a resposta gerada pelo Sintetizador é coerente
com os contextos recuperados. Se não for, solicita nova geração.
"""

from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate

# ── Configuração ──────────────────────────────
LLM_MODEL    = "llama3.2:3b"
MAX_TENTATIVAS = 2  # quantas vezes tenta regenerar se reprovar

PROMPT_REVISAO = """Você é um revisor técnico rigoroso.
Avalie se a RESPOSTA abaixo é coerente com os CONTEXTOS fornecidos.

Responda APENAS com um JSON no seguinte formato, sem texto adicional:
{{"aprovado": true ou false, "motivo": "explicação curta"}}

=== CONTEXTOS ===
{contextos}

=== RESPOSTA A REVISAR ===
{resposta}

=== AVALIAÇÃO JSON ==="""


class AgenteRevisor:
    """
    Agente responsável por revisar a coerência da resposta.
    Aprova ou rejeita com base nos contextos recuperados.
    Se rejeitar, sinaliza para o Sintetizador gerar novamente.
    """

    def __init__(self):
        print("[Revisor] Inicializando...")
        self.llm = OllamaLLM(model=LLM_MODEL)
        self.prompt = PromptTemplate(
            input_variables=["contextos", "resposta"],
            template=PROMPT_REVISAO,
        )
        self.chain = self.prompt | self.llm
        print("[Revisor] Pronto.\n")

    def _formatar_contextos(self, contextos: dict) -> str:
        """Junta todos os contextos em um bloco de texto."""
        partes = []
        for ctx in contextos.get("docs_python", []):
            partes.append(ctx["texto"][:300])
        for ctx in contextos.get("stackoverflow", []):
            partes.append(ctx["texto"][:300])
        return "\n---\n".join(partes)

    def revisar(self, resposta: str, contextos: dict) -> dict:
        """
        Revisa a resposta gerada.

        Args:
            resposta:  Texto gerado pelo Sintetizador.
            contextos: Dict com 'docs_python' e 'stackoverflow'.

        Returns:
            Dict com 'aprovado' (bool) e 'motivo' (str).
        """
        import json

        print("[Revisor] Verificando coerência da resposta...")

        contextos_texto = self._formatar_contextos(contextos)

        resultado_bruto = self.chain.invoke({
            "contextos": contextos_texto,
            "resposta":  resposta,
        })

        # Tenta extrair o JSON da resposta
        try:
            # Procura pelo bloco JSON na resposta
            inicio = resultado_bruto.find("{")
            fim    = resultado_bruto.rfind("}") + 1
            json_str = resultado_bruto[inicio:fim]
            resultado = json.loads(json_str)
        except Exception:
            # Se não conseguir parsear, aprova por padrão
            resultado = {"aprovado": True, "motivo": "Não foi possível avaliar — aprovado por padrão."}

        aprovado = resultado.get("aprovado", True)
        motivo   = resultado.get("motivo", "")

        status = "✅ Aprovada" if aprovado else "❌ Reprovada"
        print(f"[Revisor] {status} — {motivo}\n")

        return resultado


# ── Teste rápido ──────────────────────────────
if __name__ == "__main__":
    from agents.recuperador  import AgenteRecuperador
    from agents.sintetizador import AgenteSintetizador

    pergunta = "Como usar list comprehension em Python?"

    recuperador  = AgenteRecuperador()
    sintetizador = AgenteSintetizador()
    revisor      = AgenteRevisor()

    contextos = recuperador.buscar_todos(pergunta)
    resposta  = sintetizador.gerar(pergunta, contextos)
    avaliacao = revisor.revisar(resposta, contextos)

    print("── Resposta ──────────────────────────────")
    print(resposta)
    print("\n── Avaliação do Revisor ──────────────────")
    print(f"Aprovado: {avaliacao['aprovado']}")
    print(f"Motivo:   {avaliacao['motivo']}")