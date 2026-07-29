import os
import json
import time
import requests
import urllib.parse
import chromadb
import networkx as nx
from bs4 import BeautifulSoup
import logger_nib as logger

# ==========================================
# 1. CONFIGURAÇÕES E MEMÓRIA PERSISTENTE
# ==========================================
DIR_BASE = "./memoria_perfeita_db"
DIR_CHROMA = os.path.join(DIR_BASE, "chroma")
ARQUIVO_GRAFO = os.path.join(DIR_BASE, "graphrag_memory.json")
ARQUIVO_WAL = os.path.join(DIR_BASE, "events_wal.jsonl")

os.makedirs(DIR_BASE, exist_ok=True)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO_OLLAMA = "qwen2.5:3b"

# --- A. ChromaDB (Memória Vetorial) ---
chroma_client = chromadb.PersistentClient(path=DIR_CHROMA)
colecao_vetorial = chroma_client.get_or_create_collection(name="memoria_episodica")

# --- B. GraphRAG NATIVO em Python (NetworkX + Persistência JSON) ---
class NativeGraphRAG:
    """Motor de GraphRAG leve em Python nativo com persistência garantida em disco."""
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.graph = nx.DiGraph()
        self.carregar_do_disco()

    def carregar_do_disco(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.graph = nx.node_link_graph(data)
                logger.log_neocortex(f"Grafo do GraphRAG carregado do disco: {len(self.graph.nodes)} nós, {len(self.graph.edges)} arestas.")
            except Exception as e:
                logger.log_warning(f"Aviso ao carregar o grafo: {e}. Criando novo grafo.")
                self.graph = nx.DiGraph()

    def salvar_no_disco(self):
        data = nx.node_link_data(self.graph)
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def adicionar_tripla(self, sujeito: str, relacao: str, objeto: str, timestamp: int):
        s = sujeito.strip().lower()
        r = relacao.strip().lower()
        o = objeto.strip().lower()

        if not s or not o:
            return

        self.graph.add_node(s, label=s)
        self.graph.add_node(o, label=o)

        if self.graph.has_edge(s, o):
            self.graph[s][o]["relacao"] = r
            self.graph[s][o]["updated_at"] = timestamp
            self.graph[s][o]["weight"] = self.graph[s][o].get("weight", 1) + 1
        else:
            self.graph.add_edge(s, o, relacao=r, created_at=timestamp, updated_at=timestamp, weight=1)

        self.salvar_no_disco()

    def buscar_subgrafo_relacionado(self, termos: list) -> list:
        """Navega no grafo a partir dos termos para recuperar o contexto associativo."""
        relacoes = []
        for termo in termos:
            t = termo.strip().lower()
            if self.graph.has_node(t):
                for vizinho in self.graph.neighbors(t):
                    edge = self.graph[t][vizinho]
                    relacoes.append(f"[Grafo/Relação]: {t} --({edge['relacao']})--> {vizinho}")
                for antecessor in self.graph.predecessors(t):
                    edge = self.graph[antecessor][t]
                    relacoes.append(f"[Grafo/Relação]: {antecessor} --({edge['relacao']})--> {t}")
        return list(set(relacoes))

# Inicializa o motor GraphRAG nativo
graph_rag = NativeGraphRAG(ARQUIVO_GRAFO)

# ==========================================
# 2. MOTOR DE BUSCA EM CAMADAS (ACADÊMICO -> WEB)
# ==========================================
def buscar_diretorio_academico(query: str) -> list:
    resultados = []
    logger.log_busca(f"Pesquisando em repositórios científicos/acadêmicos: '{query}'...")
    
    # 1. arXiv API
    try:
        url_arxiv = f"http://export.arxiv.org/api/query?search_query=all:{urllib.parse.quote(query)}&start=0&max_results=2"
        resp = requests.get(url_arxiv, timeout=5)
        if "<entry>" in resp.text:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(resp.text)
            for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
                titulo = entry.find("{http://www.w3.org/2005/Atom}title").text.strip().replace("\n", " ")
                resumo = entry.find("{http://www.w3.org/2005/Atom}summary").text.strip().replace("\n", " ")
                resultados.append(f"[Artigo arXiv] Título: {titulo} | Resumo: {resumo[:250]}...")
    except Exception:
        pass

    # 2. OpenAlex API (Fallback acadêmico)
    if not resultados:
        try:
            url_openalex = f"https://api.openalex.org/works?search={urllib.parse.quote(query)}&per-page=2"
            resp = requests.get(url_openalex, timeout=5).json()
            for item in resp.get("results", []):
                titulo = item.get("title", "")
                if titulo:
                    resultados.append(f"[Artigo OpenAlex] Título: {titulo}")
        except Exception:
            pass

    return resultados

def buscar_web_convencional(query: str) -> list:
    logger.log_busca(f"Fallback ativado. Pesquisando na web: '{query}'...")
    resultados = []
    try:
        url_ddg = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        resp = requests.get(url_ddg, headers=headers, timeout=5)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        for a in soup.find_all('a', class_='result__snippet', limit=2):
            resultados.append(f"[Web Result]: {a.get_text().strip()}")
    except Exception:
        pass
    return resultados

def pesquisar_conhecimento_externo(query: str) -> str:
    resultados = buscar_diretorio_academico(query)
    if not resultados:
        resultados = buscar_web_convencional(query)
        
    if not resultados:
        return "Nenhuma informação externa encontrada."

    conteudo = "\n".join(resultados)
    
    # Memoriza imediatamente no ChromaDB + GraphRAG
    id_novo = f"ext_mem_{int(time.time())}"
    salvar_memoria_perfeita(f"Conhecimento pesquisado sobre '{query}': {conteudo}", id_novo)
    
    return conteudo

# ==========================================
# 3. GRAVAÇÃO E RECUPERAÇÃO PERFEITA
# ==========================================
def salvar_memoria_perfeita(texto: str, id_unico: str):
    timestamp = int(time.time())
    
    # 1. Log WAL
    with open(ARQUIVO_WAL, "a", encoding="utf-8") as f:
        f.write(json.dumps({"id": id_unico, "texto": texto, "timestamp": timestamp}, ensure_ascii=False) + "\n")
    logger.log_wal(f"Registro WAL gravado: '{id_unico}'")
    
    # 2. ChromaDB (Vetor)
    colecao_vetorial.add(
        documents=[texto],
        metadatas=[{"timestamp": timestamp}],
        ids=[id_unico]
    )
    logger.log_hipocampo(f"Memória vetorial armazenada permanentemente.")
    
    # 3. GraphRAG (Grafo em Python)
    extrair_e_salvar_grafo(texto, timestamp)
    logger.log_perfect(f"Memória gravada e sincronizada no GraphRAG: '{texto[:60]}...'")

def extrair_e_salvar_grafo(texto: str, timestamp: int):
    system_prompt = (
        "Extraia triplas de conhecimento no formato JSON estrito:\n"
        '{"triplas": [{"sujeito": "...", "relacao": "...", "objeto": "..."}]}\n'
        "Use entidades em palavras únicas ou termos curtos. Retorne APENAS o JSON."
    )
    try:
        res = requests.post(OLLAMA_URL, json={
            "model": MODELO_OLLAMA,
            "prompt": f"Extraia triplas: '{texto}'",
            "system": system_prompt,
            "stream": False
        }, timeout=30).json().get("response", "")
        
        inicio, fim = res.find("{"), res.rfind("}") + 1
        if inicio != -1 and fim != -1:
            dados = json.loads(res[inicio:fim])
            for t in dados.get("triplas", []):
                graph_rag.adicionar_tripla(t["sujeito"], t["relacao"], t["objeto"], timestamp)
    except Exception as e:
        logger.log_warning(f"Erro ao extrair triplas para o GraphRAG: {e}")

def recuperar_memoria_local(query: str) -> str:
    contexto = []
    
    # 1. Recuperação Vetorial no ChromaDB
    res_vec = colecao_vetorial.query(query_texts=[query], n_results=2)
    if res_vec["documents"] and res_vec["documents"][0]:
        for doc in res_vec["documents"][0]:
            contexto.append(f"[Memória Episódica]: {doc}")
            
    # 2. Recuperação Relacional no GraphRAG
    palavras_chave = [p.strip().lower() for p in query.split() if len(p) > 3]
    relacoes_grafo = graph_rag.buscar_subgrafo_relacionado(palavras_chave)
    contexto.extend(relacoes_grafo)
    
    return "\n".join(contexto)

# ==========================================
# 4. PROCESSADOR PRINCIPAL
# ==========================================
def processar_pergunta(pergunta: str) -> str:
    contexto = recuperar_memoria_local(pergunta)
    
    if not contexto or len(contexto.strip()) < 15:
        logger.log_perfect("Dados ausentes localmente. Disparando pesquisa externa...")
        conhecimento = pesquisar_conhecimento_externo(pergunta)
        contexto = f"[Conhecimento Adquirido]: {conhecimento}"
    else:
        logger.log_perfect("Informação recuperada com sucesso do ChromaDB + GraphRAG!")

    prompt_final = f"Contexto disponível de memória:\n{contexto}\n\nPergunta do usuário: {pergunta}"
    
    resposta = requests.post(OLLAMA_URL, json={
        "model": MODELO_OLLAMA,
        "prompt": prompt_final,
        "system": "Você é um assistente atencioso. Responda de forma precisa com base no contexto fornecido.",
        "stream": False
    }, timeout=30).json().get("response", "")
    
    return resposta

# ==========================================
# 5. DEMONSTRAÇÃO
# ==========================================
if __name__ == "__main__":
    logger.log_perfect("=== TESTANDO SISTEMA DE MEMÓRIA PERFEITA (GRAPHRAG + CHROMADB + WAL) ===")
    
    if colecao_vetorial.count() == 0:
        salvar_memoria_perfeita("Luiz desenvolve sistemas em Python e atua como professor.", "mem_1")
        salvar_memoria_perfeita("GraphRAG unificado com ChromaDB gera persistência perfeita.", "mem_2")

    pergunta = "Qual a profissão do Luiz e o que ele desenvolve?"
    res = processar_pergunta(pergunta)
    logger.log_nib("Ollama", f"\n{res}", logger.Colors.BRIGHT_GREEN)