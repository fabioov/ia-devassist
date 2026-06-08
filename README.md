# 🤖 ia-devassist

> Assistente técnico de programação baseado em sistema multiagente com LLMs locais, RAG e MCP.

---

## 👤 Integrante

| Nome | Curso | Semestre |
|---|---|---|
| Fabio Santos | Bacharelado em Ciência da Computação — UPF | 5º Semestre |

---

## 📌 Problema

Desenvolvedores perdem muito tempo buscando respostas técnicas espalhadas entre documentações oficiais e fóruns como o Stack Overflow. O **ia-devassist** resolve isso com um sistema multiagente que recupera trechos relevantes de uma base de conhecimento local (documentação Python/LangChain + Stack Overflow) e sintetiza uma resposta clara e explicada diretamente no terminal.

---

## 🎯 Objetivo

Construir uma aplicação em que múltiplos agentes baseados em LLMs atuem de forma coordenada para responder dúvidas técnicas de programação, utilizando recuperação de contexto (RAG), ferramentas acionáveis (tools) e comunicação padronizada entre agentes e recursos externos (MCP).

---

## 🏗️ Arquitetura Multiagente

O sistema é composto por três agentes com responsabilidades distintas que cooperam em sequência:

```
Usuário (terminal)
      │
      ▼
┌─────────────────────┐
│  Agente Recuperador │  ← busca contexto relevante na base vetorial
└─────────┬───────────┘
          │  contextos recuperados
          ▼
┌──────────────────────┐
│ Agente Sintetizador  │  ← gera resposta com LLM local (Ollama)
└─────────┬────────────┘
          │  resposta gerada
          ▼
┌─────────────────────┐
│   Agente Revisor    │  ← verifica coerência; rejeita se necessário
└─────────┬───────────┘
          │  resposta aprovada
          ▼
     Terminal + histórico
```

### Papel de cada agente

| Agente | Responsabilidade |
|---|---|
| **Recuperador** | Recebe a pergunta do usuário e busca os trechos mais relevantes no banco vetorial via `buscar_documentacao()` e `buscar_stackoverflow()` |
| **Sintetizador** | Recebe a pergunta + contextos e gera uma resposta clara com exemplo de código quando aplicável, usando o LLM local |
| **Revisor** | Verifica se a resposta é coerente com os contextos recuperados via `verificar_coerencia()`; se não, solicita nova geração |

---

## 🛠️ Tools Disponíveis

| Tool | Descrição |
|---|---|
| `buscar_documentacao(query)` | Busca semântica na base vetorial com a documentação do Python e LangChain. Retorna os 3 trechos mais relevantes. |
| `buscar_stackoverflow(query)` | Busca semântica na base vetorial com perguntas e respostas do Stack Overflow filtradas por Python. |
| `verificar_coerencia(resposta, contextos)` | Compara a resposta gerada com os contextos e retorna um score de coerência. Usado pelo Agente Revisor. |
| `salvar_historico(pergunta, resposta)` | Salva a conversa em um arquivo local de histórico para consulta posterior. |

---

## 🔗 Uso do MCP (Model Context Protocol)

O MCP é utilizado para padronizar a comunicação entre os agentes e as tools. Cada ferramenta é exposta como um recurso MCP, e os agentes acessam essas ferramentas por meio do protocolo, sem chamá-las diretamente. Isso desacopla a lógica dos agentes da implementação das ferramentas e facilita a extensão do sistema.

---

## 📚 Estratégia de RAG

O sistema utiliza **Retrieval-Augmented Generation (RAG)** para enriquecer o contexto dos agentes antes da geração de resposta:

1. Os documentos da base de conhecimento são divididos em chunks de ~500 tokens com sobreposição de 50 tokens
2. Cada chunk é transformado em um embedding via `nomic-embed-text` (Ollama)
3. Os embeddings são armazenados no ChromaDB
4. Na consulta, a pergunta do usuário é transformada em embedding e comparada com os chunks armazenados via similaridade de cosseno
5. Os N chunks mais relevantes são injetados no prompt do Agente Sintetizador como contexto

---

## 🗂️ Base de Conhecimento

| Fonte | Conteúdo | Formato | Acesso |
|---|---|---|---|
| [Documentação oficial Python](https://docs.python.org/3/) | Referência completa da linguagem | HTML/texto | Gratuito |
| [Documentação LangChain](https://python.langchain.com/docs/) | Guias e referência da lib | HTML/texto | Gratuito |
| [Stack Overflow Data Dump](https://archive.org/details/stackexchange) | Perguntas e respostas filtradas por Python | XML/texto | Gratuito |

Os documentos são processados e armazenados localmente em `data/` antes da indexação.

---

## 🧠 Embeddings e Armazenamento Vetorial

| Item | Tecnologia |
|---|---|
| Modelo de embeddings | `nomic-embed-text` via Ollama (local, sem custo) |
| Banco vetorial | ChromaDB (local, sem servidor externo) |
| Estratégia de chunking | RecursiveCharacterTextSplitter — 500 tokens, overlap 50 |

---

## 💻 Modelo Local

| Item | Detalhe |
|---|---|
| Ferramenta | [Ollama](https://ollama.com) |
| Modelo | `llama3.2:3b` |
| Justificativa | Modelo leve (3B parâmetros), roda em hardware comum sem GPU dedicada, gratuito e de código aberto |

---

## 📦 Dependências

```
langchain
langchain-community
langchain-ollama
chromadb
ollama
mcp
python-dotenv
```

Instale com:

```bash
pip install -r requirements.txt
```

---

## ⚙️ Instalação e Configuração

### 1. Clone o repositório

```bash
git clone https://github.com/fabiosantos/ia-devassist.git
cd ia-devassist
```

### 2. Instale o Ollama

Acesse [ollama.com](https://ollama.com) e instale para o seu sistema operacional. Em seguida, baixe os modelos necessários:

```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

### 3. Instale as dependências Python

```bash
pip install -r requirements.txt
```

### 4. Indexe a base de conhecimento

```bash
python rag/indexar.py
```

Este script processa os documentos em `data/`, gera os embeddings e salva o banco vetorial em `rag/chroma_db/`.

---

## ▶️ Execução

```bash
python main.py
```

O sistema iniciará no terminal com um prompt interativo:

```
🤖 ia-devassist — Assistente Técnico de Programação
Digite sua pergunta (ou 'sair' para encerrar):

> Como usar list comprehension em Python?

[Recuperador] Buscando contexto relevante...
[Sintetizador] Gerando resposta...
[Revisor] Verificando coerência...

✅ Resposta:
List comprehension é uma forma concisa de criar listas em Python...
```

---

## 💬 Exemplos de Uso

```bash
> Como funciona o decorator @property no Python?
> Qual a diferença entre append e extend em listas?
> Como criar um agente com LangChain?
> O que é um vector store e como usar com ChromaDB?
> Como fazer tratamento de exceções em Python?
```

---

## 📁 Estrutura do Repositório

```
ia-devassist/
├── agents/
│   ├── recuperador.py
│   ├── sintetizador.py
│   └── revisor.py
├── tools/
│   ├── buscar_documentacao.py
│   ├── buscar_stackoverflow.py
│   ├── verificar_coerencia.py
│   └── salvar_historico.py
├── rag/
│   ├── indexar.py
│   └── chroma_db/
├── mcp/
│   └── servidor_mcp.py
├── data/
│   ├── docs_python/
│   └── stackoverflow/
├── tests/
│   └── test_agentes.py
├── main.py
├── requirements.txt
└── README.md
```

---

## 🎓 Disciplina

**Inteligência Artificial** — Universidade de Passo Fundo (UPF)  
Prof. Diego A. Lusa · Prof. Roberto Rabello · 2025
