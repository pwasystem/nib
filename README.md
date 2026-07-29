# 🧠 NIB — Neuro-Informatik Brain

**NIB (Neuro-Informatik Brain)** é um assistente autônomo baseado em arquitetura cognitiva biológica. Ele integra um **Hipocampo** (Memória Episódica com Busca Vetorial no ChromaDB), um **Neocórtex** (Memória Associativa em Grafo Semântico - GraphRAG), um **Sistema Límbico Afetivo** (Modelo Emocional PAD) e um **Córtex Pré-Frontal** (Personalidades Big Five / OCEAN), operando localmente através de SLMs/LLMs no **Ollama**.

---

## ⚡ Principais Funcionalidades

- **🧠 Arquitetura de Memória Dupla (Humana vs. Perfeita)**:
  - **🧠 Memória Humana (`human.py`)**:
    - **Reforço Sináptico por Acesso**: A cada consulta/resgate, a força de estabilidade $S$ é incrementada (+0.5 no Hipocampo e +0.3 nas arestas do Neocórtex).
    - **Esquecimento Hebbiano (Ebbinghaus)**: Aplica a curva de retenção de Ebbinghaus $R = e^{-t / S}$. Memórias com $R < 0.15$ caducam e sofrem poda sináptica.
    - **Busca Científica em Repositórios Acadêmicos**: Quando a informação local é ausente, pesquisa ativamente em repositórios científicos (arXiv / OpenAlex) e assimila o fato.
  - **💎 Memória Perfeita (`perfect.py`)**:
    - **Persistência Imutável (WAL + ChromaDB + GraphRAG)**: Gravação perpétua no diário WAL (`events_wal.jsonl`), ChromaDB e GraphRAG nativo sem decaimento ou esquecimento.
    - **Pesquisa Externa em Camadas**: Busca acadêmica (arXiv / OpenAlex) e Web (DuckDuckGo) com consolidação imediata na memória.
- **🎨 Sistema de Logs Coloridos no Terminal (`logger_nib.py`)**:
  - Formatação com códigos ANSI coloridos no console (`[MEMÓRIA HUMANA]`, `[MEMÓRIA PERFEITA]`, `[HIPOCAMPO]`, `[NEOCÓRTEX]`, `[PODA SINÁPTICA]`, `[REFORÇO SINÁPTICO]`, `[BUSCA ACADÊMICA/WEB]`, `[LOG WAL]`).
- **🧪 Sistema Límbico (Modelo PAD)**: Simulação emocional com modulação reativa automática ou manual (Prazer, Excitação e Dominância).
- **🎛️ Córtex Pré-Frontal (Big Five / OCEAN)**: Personalidade adaptável em tempo de execução via sliders (Abertura, Conscienciosidade, Extroversão, Amabilidade e Neuroticismo).
- **💡 Aprendizado Autônomo (Módulo de Curiosidade)**: Varredura de nós órfãos no Neocórtex com pesquisa ativa na web.
- **🖥️ Interface Web Moderna**: Chat interativo em tempo real (EventSource/SSE) com painel lateral de configurações ⚙️ para alterar o Modo de Memória, modelo do Ollama, parâmetros de personalidade e emoção.

---

## 🚀 Como Executar

### Pré-requisitos
1. Python 3.10+ instalado.
2. [Ollama](https://ollama.com/) instalado e rodando em `http://localhost:11434`.

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/pwasystem/nib.git
cd nib
```

2. Instale as dependências:
```bash
pip install fastapi uvicorn requests chromadb networkx beautifulsoup4
```

3. Inicie o servidor NIB:
```bash
python server_nib.py
```

4. Acesse a interface no seu navegador:
```text
http://127.0.0.1:8000
```

---

## 📡 Endpoints da API FastAPI

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/memory-mode` | Retorna o modo de memória ativo (`human` ou `perfect`) |
| `POST` | `/api/set-memory-mode` | Altera o modo de memória entre `human` e `perfect` |
| `POST` | `/api/prune-memory` | Executa a poda sináptica Hebbiana no Modo Humano |
| `GET` | `/api/ollama-models` | Lista os modelos instalados no Ollama local |
| `POST` | `/api/set-ollama-model` | Altera o modelo ativo do Ollama em tempo de execução |
| `POST` | `/api/kill-and-rebirth` | Limpa toda a memória do NIB e inicia um novo ciclo de vida |

---

## 🧪 Executando os Testes e Simulações

### Simulação da Mente Humana (Poda Hebbiana + Reforço + Busca Acadêmica)
```bash
python human.py
```

### Simulação da Memória Perfeita (WAL + GraphRAG Perpétuo + Busca Web)
```bash
python perfect.py
```

### Suíte de Testes Unitários
```bash
python -m unittest discover tests
```

---

## 📄 Licença

Este projeto está licenciado sob a licença MIT.
