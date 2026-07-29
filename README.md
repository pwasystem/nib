# 🧠 NIB — Neuro-Informatik Brain

**NIB (Neuro-Informatik Brain)** é um assistente autônomo baseado em arquitetura cognitiva biológica, que integra um **Hipocampo** (Memória Episódica com Busca Vetorial), um **Neocórtex** (Memória Associativa em Grafo Semântico - GraphRAG), um **Sistema Límbico Afetivo** (Modelo Emocional PAD) e um **Córtex Pré-Frontal** (Personalidades Big Five / OCEAN), operando localmente através de LLMs no **Ollama**.

---

## ⚡ Principais Funcionalidades

- **🧠 Memória Episódica (Hipocampo)**: Armazenamento vetorial permanente de experiências via ChromaDB.
- **🕸️ Memória Semântica (Neocórtex)**: Grafo de relações conceituais e sinapses extraídas automaticamente.
- **🧪 Sistema Límbico (Modelo PAD)**: Simulação emocional com modulação reativa automática ou manual (Prazer, Excitação e Dominância).
- **🎛️ Córtex Pré-Frontal (Big Five / OCEAN)**: Personalidade adaptável em tempo de execução via sliders (Abertura, Conscienciosidade, Extroversão, Amabilidade e Neuroticismo).
- **💡 Aprendizado Autônomo (Módulo de Curiosidade)**: Varredura de nós órfãos no Neocórtex com pesquisa ativa na web.
- **🖥️ Interface Web Moderna**: Chat interativo em tempo real (EventSource/SSE) com suporte a Markdown, tabelas e visualização de cartões de dados.
- **🎛️ Chaves Liga/Desliga**: Controles independentes para ativar/desativar o Módulo de Personalidade e o Módulo Emocional.

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
pip install -r install.bat # ou instale fastapi uvicorn requests chromadb networkx beautifulsoup4
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

## 🧪 Executando os Testes

Para rodar a suíte completa de testes unitários automatizados:

```bash
python -m unittest discover tests
```

---

## 📄 Licença

Este projeto está licenciado sob a licença MIT.
