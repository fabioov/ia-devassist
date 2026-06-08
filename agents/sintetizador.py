"""
Agente Sintetizador — ia-devassist
Recebe a pergunta do usuário + contextos recuperados e gera
uma resposta clara usando o LLM local (Ollama).
"""

from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate

# ── Configuração ──────────────────────────────
LLM_MODEL = "llama3.2:3b"

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
    """
    Agente responsável por gerar a resposta final.
    Usa o LLM local (Ollama) com os contextos recuperados pelo Agente Recuperador.
    """

    def __init__(self):
        print("[Sintetizador] Conectando ao modelo local...")
        self.llm = OllamaLLM(model=LLM_MODEL)
        self.prompt = PromptTemplate(
            input_variables=["contexto_docs", "contexto_so", "pergunta"],
            template=PROMPT_TEMPLATE,
        )
        self.chain = self.prompt | self.llm
        print("[Sintetizador] Pronto.\n")

    def _formatar_contextos(self, contextos: list[dict]) -> str:
        """Formata a lista de contextos em texto para o prompt."""
        if not contextos:
            return "Nenhum contexto encontrado."
        partes = []
        for i, ctx in enumerate(contextos, 1):
            partes.append(f"[{i}] ({ctx['arquivo']})\n{ctx['texto'][:600]}")
        return "\n\n".join(partes)

    def gerar(self, pergunta: str, contextos: dict) -> str:
        """
        Gera uma resposta com base na pergunta e nos contextos.

        Args:
            pergunta: A dúvida do usuário.
            contextos: Dict com 'docs_python' e 'stackoverflow' (saída do Recuperador).

        Returns:
            Resposta gerada pelo LLM como string.
        """
        print("[Sintetizador] Gerando resposta...")

        contexto_docs = self._formatar_contextos(contextos.get("docs_python", []))
        contexto_so   = self._formatar_contextos(contextos.get("stackoverflow", []))

        resposta = self.chain.invoke({
            "contexto_docs": contexto_docs,
            "contexto_so":   contexto_so,
            "pergunta":      pergunta,
        })

        print("[Sintetizador] Resposta gerada.\n")
        return resposta.strip()


# ── Teste rápido ──────────────────────────────
if __name__ == "__main__":
    from agents.recuperador import AgenteRecuperador

    pergunta = "Como usar list comprehension em Python?"

    recuperador  = AgenteRecuperador()
    sintetizador = AgenteSintetizador()

    contextos = recuperador.buscar_todos(pergunta)
    resposta  = sintetizador.gerar(pergunta, contextos)

    print("── Resposta ──────────────────────────────")
    print(resposta)