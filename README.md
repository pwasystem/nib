# 🧠 NIB — Neuro-Informatik Brain

**NIB (Neuro-Informatik Brain)** é um assistente autônomo baseado em arquitetura cognitiva biológica. Ele integra um **Hipocampo** (Memória Episódica com Busca Vetorial no ChromaDB), um **Neocórtex** (Memória Associativa em Grafo Semântico - GraphRAG), um **Sistema Límbico Afetivo** (Modelo Emocional PAD), um **Córtex Pré-Frontal** (Personalidades Big Five / OCEAN) e um **Módulo de Criatividade**, operando localmente através de SLMs/LLMs no **Ollama**.

---

## ⚡ Principais Funcionalidades

- **🧠 Arquitetura de Memória Dupla (Humana vs. Perfeita)**:
  - **🧠 Memória Humana (`human.py`)**:
    - **Reforço Sináptico por Acesso**: A cada consulta/resgate, a força de estabilidade $S$ é incrementada (+0.5 no Hipocampo e +0.3 nas arestas do Neocórtex).
    - **Esquecimento Hebbiano (Ebbinghaus)**: Aplica a curva de retenção de Ebbinghaus $R = e^{-t / S}$. Memórias com $R < 0.15$ caducam e sofrem poda sináptica.
  - **💎 Memória Perfeita (`perfect.py`)**:
    - **Persistência Imutável (WAL + ChromaDB + GraphRAG)**: Gravação perpétua no diário WAL (`events_wal.jsonl`), ChromaDB e GraphRAG nativo sem decaimento ou esquecimento.

- **🌐 Busca Externa em Camadas (Cascata de Fallback)**:
  - Quando a informação está ausente na memória local (Hipocampo e Neocórtex), a IA ativa um fluxo de pesquisa externa em 4 etapas:
    1. **📚 1ª Camada - Wikipedia (`buscar_wikipedia`)**: Consulta ativada em primeiro lugar para definições gerais, cultura, história, termos e conceitos gerais.
    2. **🎓 2ª Camada - Pesquisa Acadêmica (`buscar_diretorio_academico`)**: Caso o termo seja identificado como técnico/científico, a busca acadêmica (arXiv e OpenAlex) é priorizada; caso contrário, é acionada como fallback da Wikipedia.
    3. **📰 3ª Camada - Notícias Recentes (`buscar_noticias`)**: Acionada se não houver dados acadêmicos ou na Wikipedia, buscando manchetes de notícias.
    4. **🔥 4ª Camada - Tendências & Web Geral (`buscar_tendencias_e_web`)**: Fallback final para dados abertos na web e tendências.
  - Possui módulo inteligente de extração e limpeza do termo (`extrair_termo_busca`) para remover ruídos da linguagem natural antes de consultar APIs externas.
  - Todo conhecimento adquirido é automaticamente memorizado no NIB.

- **🔍 Detecção de Busca Direta & Correção de Erros**:
  - Quando o usuário solicita uma busca (ex: *"pesquise...", "busque na internet...", "procure..."*) ou sinaliza que a IA está errada (ex: *"você errou", "não é essa", "está errado"*), o NIB força imediatamente uma pesquisa na web para atualizar seus conhecimentos e responder com dados corretos.

- **🎨 Módulo de Criatividade & Aprendizado Autônomo (`curiosity_core.py`)**:
  - Quando o **Aprendizado Autônomo** está ativo (`learning_enabled = True`), a função de criatividade inspeciona o Neocórtex e Hipocampo para identificar conceitos de interesse e memórias passadas.
  - Formula pesquisas criativas e investigativas, consulta fontes externas e absorve novos aprendizados de forma contínua.

- **🎨 Sistema de Logs Coloridos no Terminal (`logger_nib.py`)**:
  - Formatação com códigos ANSI e suporte UTF-8 no console (`[MEMÓRIA HUMANA]`, `[MEMÓRIA PERFEITA]`, `[HIPOCAMPO]`, `[NEOCÓRTEX]`, `[PODA SINÁPTICA]`, `[REFORÇO SINÁPTICO]`, `🌐 [PESQUISA WEB]`, `📚 [BUSCA WIKIPEDIA]`, `🎓 [BUSCA ACADÊMICA]`, `📰 [BUSCA NOTÍCIAS]`, `🔥 [BUSCA TENDÊNCIAS/WEB]`, `🎨 [CRIATIVIDADE NIB]`, `[LOG WAL]`).

- **🧪 Sistema Límbico (Modelo PAD)**: Simulação emocional com modulação reativa automática ou manual (Prazer, Excitação e Dominância).
- **🎛️ Córtex Pré-Frontal (Big Five / OCEAN)**: Personalidade adaptável em tempo de execução via sliders (Abertura, Conscienciosidade, Extroversão, Amabilidade e Neuroticismo).
- **🖥️ Interface Web Moderna**: Chat interativo em tempo real (EventSource/SSE) com painel lateral de configurações ⚙️ para alterar o Modo de Memória, Aprendizado Autônomo, modelo do Ollama e parâmetros cognitivos.

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
| `POST` | `/api/toggle-learning` | Liga/Desliga o Aprendizado Autônomo e a Função de Criatividade |
| `POST` | `/api/prune-memory` | Executa a poda sináptica Hebbiana no Modo Humano |
| `GET` | `/api/ollama-models` | Lista os modelos instalados no Ollama local |
| `POST` | `/api/set-ollama-model` | Altera o modelo ativo do Ollama em tempo de execução |
| `POST` | `/api/kill-and-rebirth` | Limpa toda a memória do NIB e inicia um novo ciclo de vida |

---

## 🧪 Executando os Testes e Simulações

### Simulação da Mente Humana (Poda Hebbiana + Reforço)
```bash
python human.py
```

### Simulação da Memória Perfeita (WAL + GraphRAG Perpétuo)
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
