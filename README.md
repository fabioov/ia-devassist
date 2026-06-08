# 🤖 ia-devassist

> Assistente técnico de programação com sistema multiagente, LLMs locais, RAG e MCP.  
> Responde dúvidas sobre Python diretamente no terminal — sem internet, sem API paga.

---

## 👤 Integrante

| Nome | Curso | Semestre |
|---|---|---|
| Fabio Santos | Bacharelado em Ciência da Computação — UPF | 5º Semestre |

---

## 📌 O Problema

Desenvolvedores perdem muito tempo buscando respostas técnicas espalhadas entre documentações oficiais e fóruns. O **ia-devassist** resolve isso: um sistema multiagente que recupera trechos relevantes de uma base de conhecimento local (documentação Python + Stack Overflow) e sintetiza uma resposta clara diretamente no terminal.

---

## 🎯 Objetivo

Construir uma aplicação onde múltiplos agentes baseados em LLMs atuem de forma coordenada para responder dúvidas técnicas de programação, utilizando:
- **RAG** para recuperação de contexto relevante
- **Tools** como ferramentas acionáveis pelos agentes
- **MCP** para padronizar a comunicação entre agentes e ferramentas
- **Modelos locais** via Ollama — sem dependência de APIs externas

---

## 🏗️ Arquitetura Multiagente

O sistema possui **3 agentes** que cooperam em sequência a cada pergunta:

```
Usuário (terminal)
      │
      ▼
┌─────────────────────┐
│  Agente Recuperador │  ← busca contexto relevante no ChromaDB via MCP
└─────────┬───────────┘
          │  contextos recuperados
          ▼
┌──────────────────────┐
│ Agente Sintetizador  │  ← gera resposta usando LLaMA 3.2 (Ollama)
└─────────┬────────────┘
          │  resposta gerada
          ▼
┌─────────────────────┐
│   Agente Revisor    │  ← verifica coerência; pede nova geração se reprovar
└─────────┬───────────┘
          │  resposta aprovada
          ▼
   Terminal + histórico local
```

### Papel de cada agente

| Agente | Arquivo | Responsabilidade |
|---|---|---|
| **Recuperador** | `agents/recuperador.py` | Busca os trechos mais relevantes no banco vetorial para a pergunta do usuário |
| **Sintetizador** | `agents/sintetizador.py` | Recebe a pergunta + contextos e gera uma resposta com o LLM local |
| **Revisor** | `agents/revisor.py` | Avalia se a resposta é coerente com os contextos; rejeita e pede nova geração se necessário |

---

## 🛠️ Tools Disponíveis

Os agentes não chamam funções diretamente — acessam tudo via **servidor MCP**.

| Tool | Arquivo | O que faz |
|---|---|---|
| `buscar_documentacao(query)` | `tools/buscar_documentacao.py` | Busca semântica na documentação oficial do Python indexada localmente |
| `buscar_stackoverflow(query)` | `tools/buscar_stackoverflow.py` | Busca semântica nas perguntas do Stack Overflow indexadas localmente |
| `verificar_coerencia(resposta, contextos)` | `tools/verificar_coerencia.py` | Verifica se a resposta gerada é coerente com os contextos recuperados |
| `salvar_historico(pergunta, resposta)` | `tools/salvar_historico.py` | Salva a conversa em `historico.json` para consulta posterior |

---

## 🔗 MCP — Model Context Protocol

O MCP (`mcp/servidor_mcp.py`) é a camada que padroniza a comunicação entre agentes e tools. Em vez de os agentes chamarem as funções diretamente, tudo passa pelo servidor MCP, que:

- Registra e expõe todas as tools disponíveis
- Valida os parâmetros antes de executar
- Retorna resultados padronizados com `sucesso` e `resultado`
- Facilita adicionar novas tools sem alterar os agentes

---

## 📚 RAG — Retrieval-Augmented Generation

Antes de gerar qualquer resposta, o sistema **recupera contexto relevante** da base de conhecimento local:

1. Os documentos em `data/` são divididos em chunks de 500 tokens (overlap de 50)
2. Cada chunk é transformado em embedding via `nomic-embed-text` (Ollama)
3. Os embeddings são indexados no ChromaDB
4. Na consulta, a pergunta vira embedding e é comparada por similaridade de cosseno
5. Os 4 chunks mais similares são injetados no prompt do Sintetizador como contexto

---

## 🗂️ Base de Conhecimento

| Fonte | O que contém | Chunks indexados |
|---|---|---|
| [docs.python.org](https://docs.python.org/3/) | Built-ins, classes, exceções, módulos, I/O, decorators, generators | ~1.000 |
| [Stack Overflow](https://stackoverflow.com/) | Perguntas e respostas reais filtradas por Python | ~380 |

**Total: 1.378 chunks** armazenados no ChromaDB em `rag/chroma_db/`.

Os documentos ficam em `data/docs_python/` (HTML) e `data/stackoverflow/` (JSON).  
Para baixar novamente: `python3 data/baixar_docs.py`

---

## 🧠 Embeddings e Banco Vetorial

| Item | Tecnologia |
|---|---|
| Modelo de embeddings | `nomic-embed-text` via Ollama (local, gratuito) |
| Banco vetorial | ChromaDB (local, sem servidor externo) |
| Chunking | `RecursiveCharacterTextSplitter` — 500 tokens, overlap 50 |
| Similaridade | Cosseno (padrão ChromaDB) |

---

## 💻 Modelo Local

| Item | Detalhe |
|---|---|
| Ferramenta | [Ollama](https://ollama.com) |
| Modelo LLM | `llama3.2:3b` |
| Modelo Embeddings | `nomic-embed-text` |
| Justificativa | Leve (3B parâmetros), roda em hardware comum sem GPU dedicada, 100% offline após download |

---

## 📦 Dependências

```
langchain
langchain-community
langchain-ollama
langchain-chroma
chromadb
beautifulsoup4
requests
python-dotenv
```

---

## ⚙️ Instalação — Passo a Passo

> Testado no macOS. Funciona também no Linux e Windows.

### 1. Pré-requisitos

- Python 3.10 ou superior
- [Ollama](https://ollama.com) instalado

### 2. Clone o repositório

```bash
git clone https://github.com/fabiosantos/ia-devassist.git
cd ia-devassist
```

### 3. Instale as dependências Python

```bash
pip install langchain langchain-community langchain-ollama langchain-chroma chromadb beautifulsoup4 requests python-dotenv
```

### 4. Baixe os modelos no Ollama

```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

> O download pode demorar alguns minutos dependendo da sua conexão.  
> Após isso, tudo funciona **sem internet**.

### 5. Baixe a base de conhecimento

```bash
python3 data/baixar_docs.py
```

Isso baixa a documentação do Python e perguntas do Stack Overflow para `data/`.

### 6. Indexe a base de conhecimento

```bash
python3 rag/indexar.py
```

Gera os embeddings e salva o banco vetorial em `rag/chroma_db/`.  
> Demora alguns minutos na primeira execução.

---

## ▶️ Execução

```bash
python3 main.py
```

O terminal vai inicializar os agentes e abrir o prompt interativo:

```
╔══════════════════════════════════════════════╗
║       🤖  ia-devassist  v1.0               ║
║   Assistente Técnico de Programação         ║
║   Powered by LLaMA 3.2 + RAG + MCP         ║
╚══════════════════════════════════════════════╝

⏳ Inicializando agentes...
✅ Agentes prontos! Pode fazer sua pergunta.

🧑 Você: Como usar list comprehension em Python?

[Recuperador] Buscando contexto relevante...
[Sintetizador] Gerando resposta...
[Revisor] Verificando coerência...
[Revisor] ✅ Aprovada

🤖 ia-devassist:
────────────────────────────────────────────────
List comprehension é uma forma compacta de criar listas em Python.
Exemplo: numeros_pares = [x for x in range(10) if x % 2 == 0]
...
────────────────────────────────────────────────
```

### Comandos especiais

| Comando | O que faz |
|---|---|
| `historico` | Exibe as últimas 5 perguntas feitas |
| `limpar` | Limpa a tela do terminal |
| `sair` | Encerra o programa |

---

## 💬 Exemplos de Perguntas

```
Como usar decorators em Python?
Qual a diferença entre list e tuple?
Como funciona o gerenciamento de exceções?
O que é um generator e quando usar?
Como ler e escrever arquivos em Python?
Qual a diferença entre append e extend?
Como usar context managers com with?
O que é herança em orientação a objetos?
```

---

## 📁 Estrutura do Repositório

```
ia-devassist/
├── agents/
│   ├── recuperador.py       ← Agente de busca vetorial
│   ├── sintetizador.py      ← Agente gerador de respostas (LLM)
│   └── revisor.py           ← Agente de revisão de coerência
├── tools/
│   ├── buscar_documentacao.py
│   ├── buscar_stackoverflow.py
│   ├── verificar_coerencia.py
│   └── salvar_historico.py
├── rag/
│   ├── indexar.py           ← Script de indexação da base
│   └── chroma_db/           ← Banco vetorial (gerado automaticamente)
├── mcp/
│   └── servidor_mcp.py      ← Servidor MCP com registro de tools
├── data/
│   ├── baixar_docs.py       ← Script para baixar a base de conhecimento
│   ├── docs_python/         ← Documentação oficial do Python (HTML)
│   └── stackoverflow/       ← Perguntas do Stack Overflow (JSON)
├── tests/
│   └── test_agentes.py
├── main.py                  ← Ponto de entrada — interface CLI
├── requirements.txt
├── historico.json           ← Gerado automaticamente ao usar o sistema
└── README.md
```

---

## 🎓 Disciplina

**Inteligência Artificial** — Universidade de Passo Fundo (UPF)  
Prof. Diego A. Lusa · Prof. Roberto Rabello · 2025/1