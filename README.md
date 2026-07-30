# 🧠 NIB — Neuro-Informatik Brain

**NIB (Neuro-Informatik Brain)** é um assistente autônomo baseado em uma arquitetura cognitiva biológica avançada. Ele integra um **Córtex Pré-Frontal (Memória de Trabalho de Curto Prazo e Personalidades Big Five/OCEAN)**, um **Hipocampo (Memória Episódica com Busca Vetorial no ChromaDB)**, um **Neocórtex (Memória Associativa em Grafo Semântico com Normalização de Entidades - GraphRAG)**, um **RAG Híbrido (Vetorial + Relacional)**, um **Sistema Límbico Afetivo (Modelo Emocional PAD)** e um **Dashboard Cognitivo Interativo**, operando localmente através de SLMs/LLMs no **Ollama**.

---

## ⚡ Principais Funcionalidades

- **🧠 Arquitetura de Memória em 3 Níveis**:
  - **⚡ Memória de Trabalho (`working_memory.py`)**:
    - Buffer deslizante circular de curto prazo ($N$ turnos recentes) no Córtex Pré-Frontal para retenção direta do contexto ativo da conversa sem depender apenas de busca por embeddings.
  - **🧠 Memória Humana (`human.py` / `nib_brain.py`)**:
    - **Reforço Sináptico por Acesso**: Incrementa a força de estabilidade $S$ a cada consulta (+0.5 no Hipocampo e +0.3 nas conexões do Neocórtex).
    - **Esquecimento Hebbiano (Ebbinghaus)**: Aplica a curva de retenção de Ebbinghaus $R = e^{-t / S}$. Memórias e arestas com $R < 0.15$ caducam e sofrem poda sináptica.
  - **💎 Memória Perfeita (`perfect.py`)**:
    - **Persistência Imutável (WAL + ChromaDB + GraphRAG)**: Gravação perpétua no diário WAL (`synaptic_journal.jsonl`), ChromaDB e GraphRAG nativo sem decaimento ou esquecimento.

- **🔀 RAG Híbrido & Re-ranking (Vetorial + Relacional)**:
  - Combina a pontuação de similaridade semântica do Hipocampo ($S_{vec}$) com o grau e os pesos de relacionamento no Grafo do Neocórtex ($S_{graph}$).
  - Ordenação e re-ranking unificado das informações resgatadas:
    $$S_{hibrido} = (\text{HYBRID\_RAG\_VECTOR\_WEIGHT} \cdot S_{vec}) + (\text{HYBRID\_RAG\_GRAPH\_WEIGHT} \cdot S_{graph})$$

- **🧼 Normalização Canônica de Entidades no GraphRAG**:
  - Etapa inteligente de limpeza e canonização antes da inserção de nós no Neocórtex.
  - Remove acentos, pontuações, artigos/conectivos e singulariza plurais em português (ex: *"A Teoria da Relatividade"* $\rightarrow$ *"teoria da relatividade"*), fundindo conceitos equivalentes e evitando a fragmentação do grafo.

- **🌐 Busca Externa em Camadas com Resumo Sintético**:
  - Quando a informação está ausente na memória local (Hipocampo/Neocórtex), aciona uma pesquisa em 4 etapas (Wikipedia ➔ Acadêmica ➔ Notícias ➔ Tendências/Web).
  - Conteúdos raspados da web passam por um processo prévio de **síntese e despoluição via LLM** (`resumir_conhecimento_externo`), extraindo apenas fatos limpos antes da indexação no ChromaDB.

- **📊 Dashboard Cognitivo & Visualizador de Grafo**:
  - Interface visual interativa integrada no `index.html` com 3 abas:
    - **📊 Estatísticas da Mente**: Métricas de memórias episódicas, nós/arestas no Neocórtex, força sináptica média e capacidade de memória de trabalho.
    - **🕸️ Grafo do Neocórtex**: Visualização física interativa da rede de conhecimento via `Vis.js Network` (com física de força, drag-and-drop e zoom).
    - **🍂 Histórico de Podas**: Diário e linha do tempo de memórias e conexões podadas pela curva de Ebbinghaus.

- **🔒 Configuração Avançada & Segurança de Segredos**:
  - Loader inteligente (`config.py`) com carregamento dinâmico e fallbacks seguros de variáveis de ambiente (`.env` / `.env.example`) e hiperparâmetros cognitivos (`config.yaml`).

- **⚡ Servidor FastAPI 100% Assíncrono (`httpx`)**:
  - Gerador de streaming de respostas no `/api/chat` usando `httpx.AsyncClient` com I/O assíncrono não-bloqueante no Event Loop.

---

## 🚀 Como Executar

### Pré-requisitos
1. Python 3.9+ instalado.
2. [Ollama](https://ollama.com/) instalado e rodando em `http://localhost:11434`.

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/pwasystem/nib.git
cd nib
```

2. Crie seu arquivo de configuração local:
```bash
cp .env.example .env
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Inicie o servidor NIB:
```bash
python server_nib.py
```

5. Acesse a interface no navegador:
```text
http://127.0.0.1:8000
```

---

## 📡 Endpoints da API FastAPI

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/chat` | Endpoint principal de chat com streaming SSE não-bloqueante |
| `GET` | `/api/dashboard/stats` | Retorna estatísticas de memória, força sináptica, histórico de podas e estados |
| `GET` | `/api/dashboard/graph` | Retorna nós e arestas do Neocórtex formatados para o visualizador de rede |
| `GET` | `/api/working-memory` | Retorna as mensagens ativas na Memória de Trabalho (curto prazo) |
| `POST` | `/api/clear-working-memory` | Esvazia o buffer de curto prazo da sessão |
| `GET` | `/api/memory-mode` | Retorna o modo de memória ativo (`human` ou `perfect`) |
| `POST` | `/api/set-memory-mode` | Altera o modo de memória entre `human` e `perfect` |
| `POST` | `/api/toggle-learning` | Liga/Desliga o Aprendizado Autônomo e a Função de Criatividade |
| `POST` | `/api/toggle-personality` | Ativa/Desativa as instruções de personalidade Big Five |
| `POST` | `/api/set-custom-personality` | Ajusta os sliders OCEAN em tempo real |
| `POST` | `/api/prune-memory` | Executa manualmente a poda sináptica no Modo Humano |
| `GET` | `/api/ollama-models` | Lista assincronamente os modelos instalados no Ollama local |
| `POST` | `/api/set-ollama-model` | Altera o modelo ativo do Ollama em tempo de execução |
| `POST` | `/api/kill-and-rebirth` | Limpa toda a memória do NIB e inicia um novo ciclo de vida |

---

## 🧪 Suíte de Testes e Simulações

```bash
# Simulação da Mente Humana (Poda Hebbiana + Reforço)
python human.py

# Simulação da Memória Perfeita (WAL + GraphRAG Perpétuo)
python perfect.py

# Execução de todos os testes unitários
python -m unittest discover tests
```

---

## 📄 Licença

Este projeto está licenciado sob a [Licença MIT](file:///c:/Users/spide/Sistemas/nib/LICENSE).

