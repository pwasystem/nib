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
  - Combina a pontuação de similaridade semântica do Hipocampo ($S_{\text{vetor}}$) com o grau e os pesos de relacionamento no Grafo do Neocórtex ($S_{\text{grafo}}$).
  - Ordenação e re-ranking unificado das informações resgatadas:
    $$S_{\text{híbrido}} = (w_{\text{vetor}} \cdot S_{\text{vetor}}) + (w_{\text{grafo}} \cdot S_{\text{grafo}})$$
    *(onde os pesos $w_{\text{vetor}}$ e $w_{\text{grafo}}$ são definidos pelas constantes `HYBRID_RAG_VECTOR_WEIGHT` e `HYBRID_RAG_GRAPH_WEIGHT` em `config.py`)*

- **🧼 Normalização Canônica de Entidades no GraphRAG**:
  - Etapa inteligente de limpeza e canonização antes da inserção de nós no Neocórtex.
  - Remove acentos, pontuações, artigos/conectivos e singulariza plurais em português (ex: *"A Teoria da Relatividade"* $\rightarrow$ *"teoria da relatividade"*), fundindo conceitos equivalentes e evitando a fragmentação do grafo.

- **🌐 Busca Externa em Camadas com Resumo Sintético**:
  - Quando a informação está ausente na memória local (Hipocampo/Neocórtex), aciona uma pesquisa em 4 etapas (Wikipedia ➔ Acadêmica ➔ Notícias ➔ Tendências/Web).
  - Conteúdos raspados da web passam por um processo prévio de **síntese e despoluição via LLM** (`resumir_conhecimento_externo`), extraindo apenas fatos limpos antes da indexação no ChromaDB.

- **🎭 Sistema Extensível de Templates de Personalidade & Emoção (`personalities/templates/`)**:
  - Modula simultaneamente a personalidade **Big Five (OCEAN)** e o estado de afeto **PAD (Prazer, Excitação, Dominância)**.
  - **🌟 Zodíaco Ocidental**: 12 Signos (Áries, Touro, Gêmeos, Câncer, Leão, Virgem, Libra, Escorpião, Sagitário, Capricórnio, Aquário, Peixes) com tópicos de interesse específicos.
  - **🐉 Matriz Sexagesimal Chinesa**: 60 Combinações de 12 Animais $\times$ 5 Elementos (Madeira, Fogo, Terra, Metal, Água) com interesses direcionados por animal/elemento.
  - **🎭 Presets Arquétipos Cognitivos**: Presets predefinidos (*Mentor Estóico*, *Cientista Entusiasmado*, *Auditor Crítico*, *Poeta Empático*).
  - **🛠️ Cadastro, Edição e Upload Customizado**: Suporte total para cadastro, edição de parâmetros (OCEAN/PAD/Descrição/Interesses), exclusão e upload de novos arquivos `.json` ou módulos Python `.py` em `personalities/templates/`.

- **🎯 Aprendizado Autônomo Guiado por Interesses**:
  - Cada personalidade possui uma lista de **interesses característicos**. Quando o **Aprendizado Autônomo** (`CuriosityCore`) está ativado, ele prioriza a pesquisa de tópicos alinhados aos interesses da personalidade ativa.

- **🪞 Plena Auto-Consciência de Capacidades, Emoções & Personalidade**:
  - Injeção dinâmica no prompt do sistema da auto-consciência total do NIB quanto ao seu modelo Ollama ativo, modo de memória, percentuais numéricos de Big Five (OCEAN), vetores emocionais PAD, tópicos de interesse e capacidades de aprendizado autônomo.

- **📊 Dashboard Cognitivo, Visualizador de Grafo & Agregador de Logs**:
  - **Página Independente (`/dashboard`)**: Acesso via modal ou em aba/janela exclusiva com o botão *"🔗 Nova Página"*.
  - **🖥️ Terminal de Logs em Tempo Real**: Agregador e visualizador de logs do terminal em tempo real com auto-refresh (2s), categorização visual de tags (`[HIPOCAMPO]`, `[NEOCÓRTEX]`, `[PODA SINÁPTICA]`, `[MEMÓRIA HUMANA]`, etc.) e auto-scroll.

- **💾 Persistência de Preferências**:
  - Memorização persistente do modelo Ollama selecionado em disco (`nib_storage/selected_model.txt`) e personalidades customizadas (`nib_storage/custom_personalities.json`).

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
Ou acesse o Dashboard Cognitivo em tela cheia:
```text
http://127.0.0.1:8000/dashboard
```

---

## 📡 Endpoints da API FastAPI

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/chat` | Endpoint principal de chat com streaming SSE não-bloqueante |
| `GET` | `/dashboard` | Interface do Dashboard Cognitivo exibida como página inteira |
| `GET` | `/personality-editor` | Editor de Personalidades standalone em janela/aba exclusiva |
| `GET` | `/api/dashboard/stats` | Retorna estatísticas de memória, força sináptica, histórico de podas e estados |
| `GET` | `/api/dashboard/graph` | Retorna nós e arestas do Neocórtex formatados para o visualizador de rede |
| `GET` | `/api/dashboard/logs` | Retorna o histórico recente de logs do terminal para agregação no Dashboard |
| `GET` | `/api/personality-templates` | Lista todos os templates de personalidade/emoção (Presets, Custom, Zodíaco, Matriz Chinesa) |
| `POST` | `/api/apply-personality-template` | Aplica um template reconfigurando simultaneamente OCEAN, vetores PAD e interesses |
| `POST` | `/api/personality/save-custom` | Cria ou edita um template de personalidade customizado (OCEAN, PAD, descrição, interesses) |
| `POST` | `/api/personality/delete-custom` | Remove um template de personalidade customizado cadastrado |
| `POST` | `/api/personality/upload-file` | Faz upload de arquivo `.json` ou módulo Python `.py` em `personalities/templates/` |
| `GET` | `/api/working-memory` | Retorna as mensagens ativas na Memória de Trabalho (curto prazo) |
| `POST` | `/api/clear-working-memory` | Esvazia o buffer de curto prazo da sessão |
| `GET` | `/api/memory-mode` | Retorna o modo de memória ativo (`human` ou `perfect`) |
| `POST` | `/api/set-memory-mode` | Altera o modo de memória entre `human` e `perfect` |
| `POST` | `/api/toggle-learning` | Liga/Desliga o Aprendizado Autônomo e a Função de Criatividade |
| `POST` | `/api/toggle-personality` | Ativa/Desativa as instruções de personalidade Big Five |
| `POST` | `/api/set-custom-personality` | Ajusta os sliders OCEAN em tempo real |
| `POST` | `/api/prune-memory` | Executa manualmente a poda sináptica no Modo Humano |
| `GET` | `/api/ollama-models` | Lista assincronamente os modelos instalados no Ollama local |
| `POST` | `/api/set-ollama-model` | Altera e memoriza o modelo ativo do Ollama |
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

