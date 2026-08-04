import math
import time
import json
import requests
import urllib.parse
import chromadb
import networkx as nx
import logger_nib as logger

# ==========================================
# 1. CONFIGURAÇÃO DE AMBIENTE & CLIENTES
# ==========================================
OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO_OLLAMA = "qwen2.5:3b"

# ChromaDB para Memória Episódica (Hipocampo)
chroma_client = chromadb.PersistentClient(path="./memoria_hipocampo")
memoria_episodica = chroma_client.get_or_create_collection(name="episodios")

# Grafo para Memória Associativa / Neocórtex (GraphRAG)
grafo_neocortex = nx.DiGraph()


def chamar_ollama(prompt: str, system: str = "") -> str:
    """Função utilitária para comunicação local com o Ollama."""
    payload = {
        "model": MODELO_OLLAMA,
        "prompt": prompt,
        "system": system,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        return response.json().get("response", "")
    except Exception as e:
        logger.log_error(f"Erro ao conectar com Ollama: {e}")
        return ""

# ==========================================
# 2. SISTEMA DE APRENDIZADO E CONSOLIDAÇÃO
# ==========================================
def registrar_experiencia(texto_usuario: str, id_evento: str):
    """
    [FASE 1: HIPOCAMPO]
    Guarda o fato bruto no ChromaDB com metadados de Força (S) e Último Acesso.
    """
    agora = time.time()
    
    memoria_episodica.add(
        documents=[texto_usuario],
        metadatas=[{
            "timestamp_criacao": agora,
            "ultimo_acesso": agora,
            "forca_sinaptica": 1.5,  # Valor inicial de estabilidade S
            "acessos": 1
        }],
        ids=[id_evento]
    )
    logger.log_hipocampo(f"Experiência registrada no ChromaDB: '{texto_usuario}'")
    
    # Processa imediatamente a consolidação para o Grafo (Neocórtex)
    consolidar_para_neocortex(texto_usuario, id_evento)

def consolidar_para_neocortex(texto: str, id_evento: str):
    """
    [FASE 2: CONSOLIDAÇÃO DO SONO]
    Usa o Ollama para extrair Entidades e Relações e insere no Grafo Associativo.
    """
    system_prompt = (
        "Você é um extrator de conhecimento. Extraia no máximo 2 triplas no formato JSON puro:\n"
        '{"triplas": [{"sujeito": "...", "relacao": "...", "objeto": "..."}]}\n'
        "Não escreva nada além do JSON."
    )
    
    resposta = chamar_ollama(f"Extraia entidades e relações do texto: '{texto}'", system=system_prompt)
    
    try:
        inicio_json = resposta.find("{")
        fim_json = resposta.rfind("}") + 1
        if inicio_json != -1 and fim_json != -1:
            dados = json.loads(resposta[inicio_json:fim_json])
            for tripla in dados.get("triplas", []):
                s, r, o = tripla["sujeito"], tripla["relacao"], tripla["objeto"]
                
                # Insere ou reforça no Grafo
                if grafo_neocortex.has_edge(s, o):
                    grafo_neocortex[s][o]["peso"] += 0.5
                    grafo_neocortex[s][o]["ultimo_acesso"] = time.time()
                else:
                    grafo_neocortex.add_edge(
                        s, o, 
                        relacao=r, 
                        peso=1.0, 
                        origem_id=id_evento, 
                        ultimo_acesso=time.time()
                    )
                logger.log_neocortex(f"Conexão criada no Grafo: ({s}) --[{r}]--> ({o})")
    except Exception as e:
        logger.log_warning(f"Não foi possível estruturar o grafo para essa memória. {e}")

# ==========================================
# 3. BUSCA EM REPOSITÓRIOS ACADÊMICOS
# ==========================================
def buscar_diretorio_academico(query: str) -> list:
    """Busca artigos acadêmicos na arXiv API ou OpenAlex API."""
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

# ==========================================
# 4. MECANISMO DE ESQUECIMENTO (DECAIMENTO)
# ==========================================
def aplicar_esquecimento_hebbiano(limiar_corte: float = 0.15):
    """
    Aplica a curva de esquecimento de Ebbinghaus no ChromaDB e no Grafo.
    Apaga memórias fracas que caíram abaixo do limiar.
    """
    agora = time.time()
    logger.log_poda("Executando Poda Sináptica (Esquecimento Hebbiano de Ebbinghaus)...")
    
    # 1. Decaimento na Memória Episódica (ChromaDB)
    todas_memorias = memoria_episodica.get(include=["metadatas", "documents"])
    ids_para_remover = []
    
    for i, m_id in enumerate(todas_memorias["ids"]):
        meta = todas_memorias["metadatas"][i]
        tempo_decorrido_dias = (agora - meta["ultimo_acesso"]) / (24 * 3600)
        
        # Fórmula de Retenção: R = e^(-t / S)
        retencao = math.exp(-tempo_decorrido_dias / meta["forca_sinaptica"])
        
        if retencao < limiar_corte:
            ids_para_remover.append(m_id)
            logger.log_poda(f"Memória episodica caducou (R={retencao:.2f}): '{todas_memorias['documents'][i]}'")
            
    if ids_para_remover:
        memoria_episodica.delete(ids=ids_para_remover)
        
    # 2. Decaimento nas Arestas do Grafo
    arestas_para_remover = []
    for u, v, data in grafo_neocortex.edges(data=True):
        tempo_decorrido_dias = (agora - data["ultimo_acesso"]) / (24 * 3600)
        retencao = math.exp(-tempo_decorrido_dias / data["peso"])
        
        if retencao < limiar_corte:
            arestas_para_remover.append((u, v))
            logger.log_poda(f"Conexão sináptica extinta no Grafo: ({u}) -> ({v})")
            
    for u, v in arestas_para_remover:
        grafo_neocortex.remove_edge(u, v)

# ==========================================
# 5. RECUPERAÇÃO HÍBRIDA & REFORÇO
# ==========================================
def recuperar_contexto_e_reforcar(pergunta: str) -> str:
    """
    Busca no ChromaDB (similaridade) + Grafo (associação) e REFORÇA as sinapses acessadas.
    Se nenhuma memória for encontrada, realiza busca acadêmica (arXiv / OpenAlex).
    """
    agora = time.time()
    contexto_linhas = []
    
    # 1. Consulta Episódica no ChromaDB
    res = memoria_episodica.query(query_texts=[pergunta], n_results=2)
    
    if res["documents"] and res["documents"][0]:
        for i, doc in enumerate(res["documents"][0]):
            m_id = res["ids"][0][i]
            meta = res["metadatas"][0][i]
            
            # REFORÇO SINÁPTICO: Aumenta S e atualiza o timestamp de acesso
            nova_forca = meta["forca_sinaptica"] + 0.5
            memoria_episodica.update(
                ids=[m_id],
                metadatas=[{
                    "timestamp_criacao": meta["timestamp_criacao"],
                    "ultimo_acesso": agora,
                    "forca_sinaptica": nova_forca,
                    "acessos": meta["acessos"] + 1
                }]
            )
            contexto_linhas.append(f"Lembrança: {doc}")
            logger.log_reforco(f"Memória '{m_id}' reativada! Nova Força S={nova_forca:.1f}")

    # 2. Consulta Associativa no Grafo
    for no in grafo_neocortex.nodes():
        if no.lower() in pergunta.lower():
            for vizinho in grafo_neocortex.neighbors(no):
                edge = grafo_neocortex[no][vizinho]
                edge["peso"] += 0.3
                edge["ultimo_acesso"] = agora
                contexto_linhas.append(f"Associação: {no} {edge['relacao']} {vizinho}")

def buscar_archive_org(query: str) -> list:
    """Busca documentos e páginas arquivadas no Archive.org."""
    resultados = []
    logger.log_busca(f"Pesquisando no Archive.org: '{query}'...")
    try:
        url_archive = f"https://archive.org/advancedsearch.php?q={urllib.parse.quote(query)}&fl[]=title,description,identifier,publicdate,mediatype&sort[]=&rows=3&page=1&output=json"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        resp = requests.get(url_archive, headers=headers, timeout=5).json()
        docs = resp.get("response", {}).get("docs", [])
        for doc in docs:
            titulo = doc.get("title", "")
            if isinstance(titulo, list):
                titulo = " ".join(titulo)
            desc = doc.get("description", "")
            if isinstance(desc, list):
                desc = " ".join(desc)
            if desc:
                desc = BeautifulSoup(desc, "html.parser").get_text().strip()
            ident = doc.get("identifier", "")
            if titulo:
                snippet = f"[Archive.org] Título: {titulo}"
                if desc:
                    snippet += f" | Descrição: {desc[:200]}..."
                if ident:
                    snippet += f" | ID: {ident}"
                resultados.append(snippet)
    except Exception:
        pass
    return resultados

    # 3. Fallback Acadêmico / Archive.org (se não houver memórias suficientes)
    if not contexto_linhas:
        logger.log_human("Nenhuma memória prévia encontrada localmente. Pesquisando em fontes acadêmicas e repositórios...")
        artigos = buscar_diretorio_academico(pergunta)
        if not artigos:
            artigos = buscar_archive_org(pergunta)
        if artigos:
            conteudo = "\n".join(artigos)
            id_novo = f"ext_mem_{int(agora)}"
            registrar_experiencia(f"Conhecimento pesquisado sobre '{pergunta}': {conteudo}", id_novo)
            contexto_linhas.append(f"[Conhecimento Externo Adquirido]: {conteudo}")

    return "\n".join(contexto_linhas)

# ==========================================
# 6. DEMONSTRAÇÃO PRÁTICA DO FLUXO COMPLETO
# ==========================================
if __name__ == "__main__":
    logger.log_human("=== INICIALIZANDO SIMULAÇÃO DE MENTE HUMANA (Ollama + ChromaDB + GraphRAG) ===\n")
    
    # Passo A: Aprendizado de Fatos em momentos diferentes
    registrar_experiencia("Meu nome é Luiz e sou professor de programação.", "mem_001")
    registrar_experiencia("Tenho vários gatos e gosto de programar em Python sem frameworks.", "mem_002")
    
    logger.log_human("\n--- SEGUNDO MOMENTO: Pergunta e Resgate ---")
    pergunta_usuario = "O que você sabe sobre a minha profissão e meus gostos?"
    
    # Recupera memórias e aplica reforço
    contexto_memoria = recuperar_contexto_e_reforcar(pergunta_usuario)
    
    # Envia para a LLM no Ollama responder com contexto da memória
    prompt_final = f"Contexto de Memória do Usuário:\n{contexto_memoria}\n\nPergunta: {pergunta_usuario}"
    resposta_ia = chamar_ollama(prompt_final, system="Responda amigavelmente usando o contexto de memória fornecido.")
    
    logger.log_nib("Ollama", f"\n{resposta_ia}", logger.Colors.BRIGHT_GREEN)
    
    # Passo B: Testando a Poda/Esquecimento (Simulando passagem de tempo)
    logger.log_human("\n... Passando tempo simulado (30 dias) sem acessar memórias irrelevantes ...")
    memoria_episodica.update(
        ids=["mem_002"],
        metadatas=[{
            "timestamp_criacao": time.time() - (30 * 24 * 3600),
            "ultimo_acesso": time.time() - (30 * 24 * 3600),
            "forca_sinaptica": 0.5,
            "acessos": 1
        }]
    )
    
    # Executa a Poda do Esquecimento
    aplicar_esquecimento_hebbiano(limiar_corte=0.15)