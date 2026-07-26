# Ingestão e Busca Semântica com LangChain e PostgreSQL (pgvector)

Este projeto implementa um **sistema completo de busca semântica baseado em PDF**,
utilizando **LangChain**, **PostgreSQL com pgvector** e **LLMs (OpenAI ou Google
Gemini)**.

O sistema permite:

* Ingerir um arquivo PDF
* Armazenar embeddings vetoriais no banco de dados
* Realizar perguntas via CLI
* Obter respostas **exclusivamente com base no conteúdo do PDF**
* Evitar qualquer tipo de alucinação ou uso de conhecimento externo

---

## 📌 Funcionalidades

### Ingestão

* Leitura de um arquivo PDF local (`PyPDFLoader`)
* Divisão do texto em *chunks* de **1000 caracteres com overlap de 150**
* Geração de embeddings (OpenAI ou Gemini)
* Persistência dos vetores no PostgreSQL (pgvector), via `langchain-postgres`

### Busca e Resposta

* Interface de linha de comando (CLI)
* Vetorização da pergunta do usuário
* Busca dos **10 trechos mais relevantes (k=10)** no banco vetorial
  (`similarity_search_with_score`)
* Montagem de prompt restritivo com base **exclusiva** no contexto recuperado
* Geração de resposta via LLM
* Perguntas fora do contexto retornam sempre a mesma resposta padrão

---

## 🧠 Tecnologias utilizadas

* **Python 3.11+**
* **LangChain** (`langchain`, `langchain-community`, `langchain-text-splitters`)
* **PostgreSQL + pgvector** (`langchain-postgres`, `psycopg`)
* **Docker & Docker Compose**
* **OpenAI** (`langchain-openai`) **ou Google Gemini** (`langchain-google-genai`)

---

## 📂 Estrutura do projeto

```
├── docker-compose.yml     # Sobe o Postgres com a extensão pgvector
├── requirements.txt       # Dependências Python
├── .env.example           # Template das variáveis de ambiente
├── document.pdf           # PDF para ingestão (padrão)
├── src/
│   ├── providers.py       # Seleção do provedor de embeddings/LLM (OpenAI ou Google)
│   ├── ingest.py          # Ingestão do PDF
│   ├── search.py          # Busca semântica + montagem do prompt + chamada à LLM
│   └── chat.py            # CLI interativo (end-to-end)
└── README.md
```

---

## ⚙️ Pré-requisitos

* Python 3.11 ou superior
* Docker Desktop instalado e em execução
* Conta na OpenAI **e/ou** no Google (Gemini) para gerar uma API Key

---

## 🐍 Ambiente Python

Crie e ative um ambiente virtual:

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

---

## 🐘 Banco de dados (PostgreSQL + pgvector)

Suba o banco via Docker:

```bash
docker compose up -d
```

Isso sobe o container `postgres_rag` (banco `rag`, usuário/senha `postgres`) e
cria automaticamente a extensão `vector` nesse banco.

Verifique se está saudável:

```bash
docker compose ps
```

O serviço `postgres` deve aparecer como `healthy`.

Para parar o banco depois:

```bash
docker compose down
```

(adicione `-v` ao final se quiser também apagar os dados persistidos).

---

## 🔐 Configuração do `.env`

Crie o arquivo `.env` a partir do template:

```bash
copy .env.example .env
```

### Exemplo de configuração (OpenAI)

```env
# === Provedor ativo (openai | google) ===
LLM_PROVIDER=openai

# === OpenAI ===
OPENAI_API_KEY=<API_KEY>
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-5-nano

# === Google Gemini (opcional) ===
GOOGLE_API_KEY=<API_KEY>
GOOGLE_EMBEDDING_MODEL=models/embedding-001
GOOGLE_CHAT_MODEL=gemini-2.5-flash-lite

# === Postgres (Docker rodando localmente) ===
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag

# === Nome da coleção/tabela vetorial ===
PG_VECTOR_COLLECTION_NAME=documents

# === Caminho do PDF a ser ingerido ===
PDF_PATH=document.pdf
```

---

### 🔄 Alternar entre OpenAI e Gemini

O projeto suporta **apenas um provedor ativo por vez**, controlado pela
variável `LLM_PROVIDER`. Ela decide tanto o modelo de **embeddings** quanto o
**LLM de resposta** (ver `src/providers.py`).

#### Usando OpenAI

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-5-nano
```

#### Usando Gemini

```env
LLM_PROVIDER=google
GOOGLE_API_KEY=...
GOOGLE_EMBEDDING_MODEL=models/embedding-001
GOOGLE_CHAT_MODEL=gemini-2.5-flash-lite
```

> ⚠️ Não é necessário alterar o código para trocar o provedor — apenas o `.env`.
> Se você trocar de provedor **depois** de já ter ingerido o PDF, ingira
> novamente (`python src/ingest.py`): os embeddings de OpenAI e Gemini não são
> compatíveis entre si dentro da mesma coleção.

---

### 📄 Configuração do PDF

O caminho do PDF é definido pela variável:

```env
PDF_PATH=document.pdf
```

* Pode ser um caminho relativo (resolvido a partir da raiz do projeto)
* Ou um caminho absoluto:

  ```env
  PDF_PATH=/caminho/completo/para/arquivo.pdf
  ```

---

## 📥 Ingestão do PDF

Com o banco no ar e o `.env` configurado, execute:

```bash
python src/ingest.py
```

Esse passo:

* Lê o PDF configurado em `PDF_PATH`
* Divide o conteúdo em **chunks de 1000 caracteres com overlap de 150**
* Gera embeddings para cada chunk (via `LLM_PROVIDER`)
* Armazena os vetores na coleção `PG_VECTOR_COLLECTION_NAME` do PostgreSQL

---

## 💬 Chat via CLI (fluxo completo)

Inicie o chat interativo:

```bash
python src/chat.py
```

Exemplo:

```text
Faça sua pergunta (digite 'sair' para encerrar):

PERGUNTA: Qual o faturamento da Empresa SuperTechIABrazil?
RESPOSTA: O faturamento foi de 10 milhões de reais.
```

### Perguntas fora do contexto

```text
PERGUNTA: Quantos clientes temos em 2024?
RESPOSTA: Não tenho informações necessárias para responder sua pergunta.
```

Digite `sair`, `exit` ou `quit` para encerrar o chat.

---

## 📏 Regras de resposta

A LLM é instruída (via `PROMPT_TEMPLATE` em `src/search.py`) a:

* Responder **somente** com base no contexto recuperado do PDF
* Não usar conhecimento externo
* Não gerar opiniões ou interpretações
* Retornar a mensagem padrão caso a resposta não esteja explicitamente no
  contexto: `"Não tenho informações necessárias para responder sua pergunta."`

---

## 🚨 Observações importantes

* O arquivo `.env` **não deve ser commitado** (já está no `.gitignore`)
* Nunca compartilhe suas API Keys
* O custo de uso das APIs é baixo para PDFs pequenos
* PDFs escaneados (imagem, sem texto extraível) não funcionam com `PyPDFLoader`
* As dependências em `requirements.txt` foram fixadas nas versões testadas
  neste ambiente (Python 3.14); se você usar outra versão do Python e tiver
  problemas de instalação, tente `pip install` sem pinos de versão para os
  pacotes principais e gere seu próprio `pip freeze`

---

## ✅ Status do projeto

* [x] Estrutura definida
* [x] Banco com pgvector via Docker
* [x] Suporte a OpenAI e Gemini via `LLM_PROVIDER`
* [x] Implementação da ingestão
* [x] Implementação da busca semântica (top-k + prompt restritivo)
* [x] Implementação do chat CLI (end-to-end)

---

## 📌 Conclusão

Este projeto implementa um fluxo completo de **RAG (Retrieval-Augmented
Generation)** de forma explícita e auditável, atendendo aos requisitos do
desafio:

* ingestão controlada (chunks de 1000/150)
* armazenamento vetorial no PostgreSQL (pgvector)
* busca top-k (`k=10`)
* prompt restritivo, sem alucinações
* suporte a dois provedores de LLM intercambiáveis por variável de ambiente
