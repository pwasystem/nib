import os
import json
import math
import time
import requests
import urllib.parse
import chromadb
import networkx as nx
from bs4 import BeautifulSoup

import config
import logger_nib as logger

class NeuroInformatikBrain:
    """
    Núcleo Integrado Biológico (NIB) - Gerenciador Neocortical e Hipocampal.
    Suporta os modos:
      - 'human': Memória Humana (Força sináptica, reforço por acesso, poda hebbiana e busca acadêmica se desconhecido).
      - 'perfect': Memória Perfeita (WAL + ChromaDB + GraphRAG perpétuo + busca web/acadêmica).
    """
    def __init__(self):
        self.memory_mode = getattr(config, "DEFAULT_MEMORY_MODE", "human")
        
        # 1. HIPOCAMPO (Memória Episódica - Vetores/ChromaDB)
        self.chroma_client = chromadb.PersistentClient(path=config.HIPPOCAMPUS_DIR)
        self.hipocampo = self.chroma_client.get_or_create_collection(name="episodic_memory")

        # 2. NEOCÓRTEX (Memória Associativa e Semântica - GraphRAG/NetworkX)
        self.neocortex_path = config.NEOCORTEX_FILE
        self.neocortex = nx.DiGraph()
        self._carregar_neocortex()

        # 3. CONTROLES DE ESTADO NIB
        self.learning_enabled = False  # Inicia desligado (OFF) por padrão
        self.personality_enabled = True # Inicia ligado (ON) por padrão
        self.wal_path = config.SYNAPTIC_JOURNAL
        self.ollama_url = config.OLLAMA_URL
        self.model_name = config.OLLAMA_MODEL

        logger.log_nib("NIB INIT", f"Cérebro inicializado no Modo: [{self.memory_mode.upper()}]", logger.Colors.BRIGHT_CYAN)

    def set_memory_mode(self, mode: str) -> str:
        """Alterna o comportamento do sistema entre 'human' e 'perfect'."""
        mode_clean = mode.lower().strip()
        if mode_clean in ["human", "perfect"]:
            self.memory_mode = mode_clean
            logger.log_nib("SISTEMA NIB", f"Modo de Memória alterado para: {self.memory_mode.upper()}", logger.Colors.BRIGHT_YELLOW)
            return self.memory_mode
        return self.memory_mode

    def reset_memoria_completa(self):
        """
        Apaga totalmente a memória episódica (Hipocampo/ChromaDB), 
        o grafo semântico (Neocórtex) e o diário sináptico (WAL).
        """
        try:
            self.chroma_client.delete_collection(name="episodic_memory")
        except Exception:
            pass
        self.hipocampo = self.chroma_client.get_or_create_collection(name="episodic_memory")

        self.neocortex = nx.DiGraph()
        self._salvar_neocortex()

        try:
            with open(self.wal_path, "w", encoding="utf-8") as f:
                f.write("")
        except Exception:
            pass

        logger.log_warning("=" * 60)
        logger.log_warning("[NIB - REINÍCIO DE VIDA] Memória zerada! Hipocampo, Neocórtex e Diário limpos.")
        logger.log_warning("=" * 60)

    # --------------------------------------------------
    # NEOCÓRTEX (Grafo de Conexões)
    # --------------------------------------------------
    def _carregar_neocortex(self):
        if os.path.exists(self.neocortex_path):
            try:
                with open(self.neocortex_path, "r", encoding="utf-8") as f:
                    self.neocortex = nx.node_link_graph(json.load(f))
                logger.log_neocortex(f"Neocórtex carregado do disco: {len(self.neocortex.nodes)} nós, {len(self.neocortex.edges)} arestas.")
            except Exception:
                self.neocortex = nx.DiGraph()

    def _salvar_neocortex(self):
        with open(self.neocortex_path, "w", encoding="utf-8") as f:
            json.dump(nx.node_link_data(self.neocortex), f, ensure_ascii=False, indent=2)

    def consolidar_sinapse(self, sujeito: str, relacao: str, objeto: str, timestamp: int):
        s, r, o = sujeito.strip().lower(), relacao.strip().lower(), objeto.strip().lower()
        if not s or not o: 
            return
        
        self.neocortex.add_node(s, label=s)
        self.neocortex.add_node(o, label=o)
        
        if self.neocortex.has_edge(s, o):
            self.neocortex[s][o]["weight"] = self.neocortex[s][o].get("weight", 1) + 1
            self.neocortex[s][o]["updated_at"] = timestamp
            logger.log_neocortex(f"[Reforço] Sinapse: ({s}) --[{r}]--> ({o}) | Peso: {self.neocortex[s][o]['weight']}")
        else:
            self.neocortex.add_edge(s, o, relacao=r, created_at=timestamp, updated_at=timestamp, weight=1)
            logger.log_neocortex(f"[Nova Sinapse]: ({s}) --[{r}]--> ({o})")
            
        self._salvar_neocortex()

    # --------------------------------------------------
    # --------------------------------------------------
    # BUSCA EXTERNA EM CAMADAS (ACADÊMICA -> NOTÍCIAS -> TENDÊNCIAS/WEB GERAL)
    # --------------------------------------------------
    def buscar_diretorio_academico(self, query: str) -> list:
        resultados = []
        logger.log_busca_academica(f"Pesquisando em repositórios científicos/acadêmicos: '{query}'...")
        
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

        if resultados:
            logger.log_busca_academica(f"Encontrados {len(resultados)} resultados acadêmicos.")
        else:
            logger.log_busca_academica("Nenhum dado acadêmico encontrado.")

        return resultados

    def buscar_noticias(self, query: str) -> list:
        resultados = []
        logger.log_pesquisa_web(f"Pesquisa Web (Notícias) por: '{query}'")
        logger.log_busca_noticias(f"Buscando manchetes e notícias sobre: '{query}'...")
        try:
            url_news = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query + ' noticias news')}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            resp = requests.get(url_news, headers=headers, timeout=5)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            for a in soup.find_all('a', class_='result__snippet', limit=2):
                resultados.append(f"[Notícia]: {a.get_text().strip()}")
        except Exception:
            pass

        if resultados:
            logger.log_busca_noticias(f"Encontradas {len(resultados)} notícias relativas.")
        else:
            logger.log_busca_noticias("Nenhuma notícia encontrada.")

        return resultados

    def buscar_tendencias_e_web(self, query: str) -> list:
        resultados = []
        logger.log_pesquisa_web(f"Pesquisa Web Geral por: '{query}'")
        logger.log_busca_tendencias(f"Buscando tendências e informações gerais na web: '{query}'...")
        try:
            url_web = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            resp = requests.get(url_web, headers=headers, timeout=5)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            for a in soup.find_all('a', class_='result__snippet', limit=2):
                resultados.append(f"[Tendências/Web]: {a.get_text().strip()}")
        except Exception:
            pass

        if resultados:
            logger.log_busca_tendencias(f"Encontrados {len(resultados)} resultados na web/tendências.")
        else:
            logger.log_busca_tendencias("Nenhuma tendência ou resultado web encontrado.")

        return resultados

    def pesquisar_conhecimento_externo(self, query: str, apenas_academico: bool = False) -> str:
        """
        Pesquisa externa em camadas:
          1. Acadêmica (arXiv / OpenAlex)
          2. Notícias Recentes
          3. Tendências e Web Geral
        """
        logger.log_pesquisa_web(f"Pesquisa externa disparada na web para a consulta: '{query}'")
        # Camada 1: Busca Acadêmica
        resultados = self.buscar_diretorio_academico(query)
        
        # Camada 2: Busca de Notícias (se a acadêmica não trouxer resultados)
        if not resultados and not apenas_academico:
            resultados = self.buscar_noticias(query)
            
        # Camada 3: Tendências e Busca Geral na Web (se a busca de notícias não trouxer resultados)
        if not resultados and not apenas_academico:
            resultados = self.buscar_tendencias_e_web(query)
            
        if not resultados:
            return "Nenhuma informação externa encontrada."

        conteudo = "\n".join(resultados)
        
        # Salva o aprendizado na memória
        id_novo = f"ext_mem_{int(time.time())}"
        self.memorizar_experiencia(f"Conhecimento pesquisado sobre '{query}': {conteudo}")
        
        return conteudo

    # --------------------------------------------------
    # PODA SINÁPTICA HEBBIANA (MODO HUMANO)
    # --------------------------------------------------
    def aplicar_esquecimento_hebbiano(self, limiar_corte: float = 0.15):
        """
        Executa a poda de Ebbinghaus no Hipocampo e no Neocórtex (Válido para o Modo Humano).
        """
        if self.memory_mode != "human":
            logger.log_warning("A poda sináptica só é aplicável no MODO HUMANO.")
            return

        agora = time.time()
        logger.log_poda("--- Executando Poda Sináptica Hebbiana (Curva de Ebbinghaus) ---")
        
        # 1. Decaimento no Hipocampo (ChromaDB)
        try:
            todas_memorias = self.hipocampo.get(include=["metadatas", "documents"])
            ids_para_remover = []
            
            for i, m_id in enumerate(todas_memorias["ids"]):
                meta = todas_memorias["metadatas"][i]
                ultimo_acesso = meta.get("ultimo_acesso", meta.get("timestamp", agora))
                forca = meta.get("forca_sinaptica", 1.5)
                
                tempo_decorrido_dias = (agora - ultimo_acesso) / (24 * 3600)
                retencao = math.exp(-tempo_decorrido_dias / forca)
                
                if retencao < limiar_corte:
                    ids_para_remover.append(m_id)
                    logger.log_poda(f"Memória episódica '{todas_memorias['documents'][i][:60]}...' caducou (Retenção R={retencao:.2f}).")
                    
            if ids_para_remover:
                self.hipocampo.delete(ids=ids_para_remover)
        except Exception as e:
            logger.log_warning(f"Erro na poda episódica: {e}")

        # 2. Decaimento no Grafo Neocortical
        arestas_para_remover = []
        for u, v, data in self.neocortex.edges(data=True):
            ultimo_acesso = data.get("ultimo_acesso", data.get("updated_at", agora))
            peso = data.get("peso", data.get("weight", 1.0))
            
            tempo_decorrido_dias = (agora - ultimo_acesso) / (24 * 3600)
            retencao = math.exp(-tempo_decorrido_dias / peso)
            
            if retencao < limiar_corte:
                arestas_para_remover.append((u, v))
                logger.log_poda(f"Conexão no Neocórtex podada: ({u}) -> ({v})")
                
        for u, v in arestas_para_remover:
            self.neocortex.remove_edge(u, v)
        self._salvar_neocortex()

    # --------------------------------------------------
    # GRAVAÇÃO DE EXPERIÊNCIAS
    # --------------------------------------------------
    def memorizar_experiencia(self, texto: str):
        ts = int(time.time())
        id_unico = f"synapse_{ts}"
        agora = time.time()

        if self.memory_mode == "human":
            logger.log_human(f"Memorizando experiência humana: '{texto[:80]}...'")
            metadata = {
                "timestamp_criacao": agora,
                "ultimo_acesso": agora,
                "forca_sinaptica": 1.5,
                "acessos": 1
            }
        else:
            logger.log_perfect(f"Memorizando experiência perfeita: '{texto[:80]}...'")
            metadata = {"timestamp": ts}

        # Log WAL (Journal)
        with open(self.wal_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"id": id_unico, "texto": texto, "timestamp": ts, "mode": self.memory_mode}, ensure_ascii=False) + "\n")
        logger.log_wal(f"Log WAL gravado para id: '{id_unico}'")

        # ChromaDB
        try:
            self.hipocampo.add(
                documents=[texto], 
                metadatas=[metadata], 
                ids=[id_unico]
            )
            logger.log_hipocampo("Nova memória gravada no ChromaDB.")
        except Exception as e:
            logger.log_warning(f"Erro no ChromaDB: {e}")
        
        # Extração de Triplas para Neocórtex
        sys_p = 'Extraia triplas de conhecimento no formato JSON estrito: {"triplas": [{"sujeito": "...", "relacao": "...", "objeto": "..."}]}. APENAS JSON.'
        try:
            r = requests.post(self.ollama_url, json={
                "model": self.model_name, 
                "prompt": f"Texto para consolidar: '{texto}'", 
                "system": sys_p, 
                "stream": False
            }, timeout=10).json().get("response", "")
            
            i, f = r.find("{"), r.rfind("}") + 1
            if i != -1 and f != -1 and f > i:
                data = json.loads(r[i:f])
                if isinstance(data, dict):
                    for t in data.get("triplas", []):
                        if isinstance(t, dict) and "sujeito" in t and "relacao" in t and "objeto" in t:
                            self.consolidar_sinapse(t["sujeito"], t["relacao"], t["objeto"], ts)
        except Exception:
            pass

    def solicitou_pesquisa_ou_correcao(self, consulta: str) -> bool:
        """Verifica se a consulta do usuário contém pedidos explícitos de busca ou sinalização de erro/correção."""
        c_lower = consulta.lower()
        gatilhos = [
            "pesquise", "pesquisar", "pesquisa", "busque", "buscar", "busca", 
            "procure", "procurar", "procura", "google", "está errado", "esta errado", 
            "tá errado", "ta errado", "está errada", "esta errada", "tá errada", "ta errada", 
            "errado", "errada", "errou", "você errou", "voce errou", "não é isso", "nao e isso", 
            "não é essa", "nao e essa", "está incorreto", "esta incorreto", "incorreto", 
            "não está certo", "nao esta certo", "está enganado", "esta enganado", "corrija", 
            "corrigir", "atualize seus conhecimentos", "atualize seu conhecimento"
        ]
        for g in gatilhos:
            if g in c_lower:
                return True
        return False

    # --------------------------------------------------
    # RESGATE DE MEMÓRIA
    # --------------------------------------------------
    def resgatar_memoria_relevante(self, consulta: str) -> str:
        contexto = []
        agora = time.time()
        tag_modo = "MEMÓRIA HUMANA" if self.memory_mode == "human" else "MEMÓRIA PERFEITA"
        
        logger.log_nib(tag_modo, f"Consultando memória para: '{consulta}'", logger.Colors.BRIGHT_YELLOW if self.memory_mode == "human" else logger.Colors.BRIGHT_CYAN)

        # 1. Consulta Episódica Vetorial no Hipocampo
        try:
            res_vec = self.hipocampo.query(query_texts=[consulta], n_results=2)
            if res_vec and res_vec.get("documents") and res_vec["documents"][0]:
                for i, doc in enumerate(res_vec["documents"][0]):
                    m_id = res_vec["ids"][0][i]
                    meta = res_vec["metadatas"][0][i]

                    # Se estiver no MODO HUMANO, aplica REFORÇO SINÁPTICO por acesso!
                    if self.memory_mode == "human":
                        forca_atual = meta.get("forca_sinaptica", 1.5)
                        nova_forca = forca_atual + 0.5
                        acessos = meta.get("acessos", 1) + 1
                        ts_criacao = meta.get("timestamp_criacao", agora)
                        
                        try:
                            self.hipocampo.update(
                                ids=[m_id],
                                metadatas=[{
                                    "timestamp_criacao": ts_criacao,
                                    "ultimo_acesso": agora,
                                    "forca_sinaptica": nova_forca,
                                    "acessos": acessos
                                }]
                            )
                            logger.log_reforco(f"Memória humana '{m_id}' reativada! Nova Força S={nova_forca:.1f}")
                        except Exception:
                            pass

                    contexto.append(f"[Memória Episódica]: {doc}")
        except Exception as e:
            logger.log_warning(f"Erro ao consultar Hipocampo: {e}")

        # 2. Consulta Associativa no Neocórtex
        palavras = [p.strip().lower() for p in consulta.split() if len(p) > 3]
        for p in palavras:
            if self.neocortex.has_node(p):
                for vz in self.neocortex.neighbors(p):
                    edge = self.neocortex[p][vz]
                    rel = edge.get("relacao", "relacionado_a")

                    # Se estiver no MODO HUMANO, reforça o peso da aresta
                    if self.memory_mode == "human":
                        edge["peso"] = edge.get("peso", 1.0) + 0.3
                        edge["ultimo_acesso"] = agora

                    contexto.append(f"[Neocórtex]: {p} --({rel})--> {vz}")
                for ant in self.neocortex.predecessors(p):
                    edge = self.neocortex[ant][p]
                    rel = edge.get("relacao", "relacionado_a")

                    if self.memory_mode == "human":
                        edge["peso"] = edge.get("peso", 1.0) + 0.3
                        edge["ultimo_acesso"] = agora

                    contexto.append(f"[Neocórtex]: {ant} --({rel})--> {p}")

        if self.memory_mode == "human":
            self._salvar_neocortex()

        # 3. Forçar Pesquisa Web em caso de Solicitação Explícita ou Correção do Usuário
        forcar_pesquisa = self.solicitou_pesquisa_ou_correcao(consulta)
        if forcar_pesquisa:
            logger.log_nib("REQUISIÇÃO/CORREÇÃO", f"Solicitação explícita de busca/correção detectada: '{consulta}'", logger.Colors.BRIGHT_MAGENTA)
            conhecimento = self.pesquisar_conhecimento_externo(consulta, apenas_academico=False)
            if conhecimento and "Nenhuma informação" not in conhecimento:
                contexto.append(f"[Conhecimento Atualizado via Pesquisa Web (Solicitado/Correção)]: {conhecimento}")

        # 4. Tratamento de Lacuna de Conhecimento quando nada for encontrado na memória local
        elif not contexto or len("\n".join(contexto).strip()) < 15:
            logger.log_nib("SISTEMA NIB", "Informação ausente na memória local. Disparando pesquisa externa em camadas (Acadêmica ➔ Notícias ➔ Tendências/Web)...", logger.Colors.BRIGHT_YELLOW)
            conhecimento = self.pesquisar_conhecimento_externo(consulta, apenas_academico=False)
            if conhecimento and "Nenhuma informação" not in conhecimento:
                contexto.append(f"[Conhecimento Externo Adquirido]: {conhecimento}")

        return "\n".join(list(set(contexto)))