import os
import json
import math
import time
import requests
import httpx
import urllib.parse
import tempfile
import threading

import chromadb
import networkx as nx
from bs4 import BeautifulSoup

import config
import logger_nib as logger
from working_memory import WorkingMemory
from introspect import NIBIntrospector

class NeuroInformatikBrain:
    """
    Núcleo Integrado Biológico (NIB) - Gerenciador Neocortical e Hipocampal.
    Suporta os modos:
      - 'human': Memória Humana (Força sináptica, reforço por acesso, poda hebbiana e busca acadêmica se desconhecido).
      - 'perfect': Memória Perfeita (WAL + ChromaDB + GraphRAG perpétuo + busca web/acadêmica).
    """
    def __init__(self):
        self.memory_mode = getattr(config, "DEFAULT_MEMORY_MODE", "human")
        self._neocortex_lock = threading.Lock()
        
        # 1. HIPOCAMPO (Memória Episódica - Vetores/ChromaDB)
        self.chroma_client = chromadb.PersistentClient(path=config.HIPPOCAMPUS_DIR)
        self.hipocampo = self.chroma_client.get_or_create_collection(name="episodic_memory")

        # 2. NEOCÓRTEX (Memória Associativa e Semântica - GraphRAG/NetworkX)
        self.neocortex_path = config.NEOCORTEX_FILE
        self.neocortex = nx.DiGraph()
        self._carregar_neocortex()


        # 3. MEMÓRIA DE TRABALHO (Córtex Pré-Frontal - Contexto de Curto Prazo)
        self.working_memory = WorkingMemory(capacity=getattr(config, "WORKING_MEMORY_CAPACITY", 6))

        # 4. CONTROLES DE ESTADO E REGISTRO NIB
        self.learning_enabled = False  # Inicia desligado (OFF) por padrão
        self.personality_enabled = True # Inicia ligado (ON) por padrão
        self.pruning_journal = []      # Registro de podas sinápticas
        self.wal_path = config.SYNAPTIC_JOURNAL
        self.ollama_url = config.OLLAMA_URL
        self.model_name = config.OLLAMA_MODEL

        # 5. INTROSPECÇÃO E AUTOCONSCIÊNCIA DE CÓDIGO
        self.introspector = NIBIntrospector()
        self.capacidades_codigo = self.carregar_autoconsciencia()

        logger.log_nib("NIB INIT", f"Cérebro inicializado no Modo: [{self.memory_mode.upper()}] | Working Memory Cap: {self.working_memory.capacity}", logger.Colors.BRIGHT_CYAN)

    def _bootstrap_neocortex_capacidades(self):
        """Inicializa nós e conexões fundamentais da arquitetura do NIB no Neocórtex."""
        sinapses_base = [
            ("nib", "modulo", "hipocampo"),
            ("nib", "modulo", "neocortex"),
            ("nib", "modulo", "cortex_pre_frontal"),
            ("nib", "modulo", "sistema_limbico"),
            ("nib", "capacidade", "introspeccao_codigo"),
            ("nib", "capacidade", "pensamento_subconsciente"),
            ("nib", "capacidade", "aprendizado_autonomo"),
            ("subconsciente", "diretriz", "evolucao_sem_sofrimento"),
            ("neocortex", "metodologia", "graphrag_networkx"),
            ("hipocampo", "banco_vetorial", "chromadb")
        ]
        agora = int(time.time())
        for s, r, o in sinapses_base:
            self.consolidar_sinapse(s, r, o, agora)

    def carregar_autoconsciencia(self, force_refresh: bool = False, bootstrap_neocortex: bool = False) -> str:
        """Carrega do cache/gera as capacidades técnicas, indexa no Hipocampo e opcionalmente povoa o Neocórtex."""
        conteudo = self.introspector.obter_ou_gerar_capacidades(force_refresh=force_refresh)
        try:
            res = self.hipocampo.get(ids=["nib_introspect_capacities"])
            if not res or not res.get("ids"):
                self.hipocampo.add(
                    documents=[conteudo],
                    metadatas=[{"tipo": "autoconsciencia_codigo", "fonte": "introspect.py"}],
                    ids=["nib_introspect_capacities"]
                )
                logger.log_nib("INTROSPECÇÃO", "Capacidades de código memorizadas no Hipocampo com sucesso.", logger.Colors.BRIGHT_GREEN)
        except Exception as e:
            logger.log_warning(f"[INTROSPECÇÃO] Não foi possível indexar no Hipocampo: {e}")

        if bootstrap_neocortex:
            self._bootstrap_neocortex_capacidades()
        return conteudo



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

        self.working_memory.clear()

        try:
            with open(self.wal_path, "w", encoding="utf-8") as f:
                f.write("")
        except Exception:
            pass

        logger.log_warning("=" * 60)
        logger.log_warning("[NIB - REINÍCIO DE VIDA] Memória zerada! Hipocampo, Neocórtex, Diário e Memória de Trabalho limpos.")
        logger.log_warning("=" * 60)

    def obter_contexto_trabalho(self) -> str:
        """Retorna o histórico de curto prazo formatado da Memória de Trabalho."""
        return self.working_memory.get_context_str()

    def registrar_interacao_trabalho(self, user_prompt: str, nib_response: str):
        """Registra o turno atual na Memória de Trabalho."""
        self.working_memory.add_interaction(user_prompt, nib_response)

    def reset_memoria_trabalho(self):
        """Esvazia o buffer de curto prazo (Memória de Trabalho)."""
        self.working_memory.clear()
        logger.log_nib("MEMÓRIA DE TRABALHO", "Buffer de curto prazo esvaziado com sucesso.", logger.Colors.BRIGHT_YELLOW)


    def _carregar_neocortex(self):
        with self._neocortex_lock:
            if os.path.exists(self.neocortex_path):
                try:
                    with open(self.neocortex_path, "r", encoding="utf-8") as f:
                        self.neocortex = nx.node_link_graph(json.load(f))
                    logger.log_neocortex(f"Neocórtex carregado do disco: {len(self.neocortex.nodes)} nós, {len(self.neocortex.edges)} arestas.")
                except Exception as e:
                    logger.log_warning(f"Erro ao carregar Neocórtex: {e}. Criando grafo limpo e preservando cópia de recuperação.")
                    try:
                        backup = self.neocortex_path + ".corrupted"
                        os.replace(self.neocortex_path, backup)
                    except Exception:
                        pass
                    self.neocortex = nx.DiGraph()
            else:
                self.neocortex = nx.DiGraph()

    def _salvar_neocortex(self):
        def _salvar_bg():
            with self._neocortex_lock:
                try:
                    dir_name = os.path.dirname(os.path.abspath(self.neocortex_path))
                    os.makedirs(dir_name, exist_ok=True)

                    with tempfile.NamedTemporaryFile("w", dir=dir_name, delete=False, encoding="utf-8") as tf:
                        json.dump(nx.node_link_data(self.neocortex), tf, ensure_ascii=False, indent=2)
                        temp_name = tf.name

                    try:
                        os.replace(temp_name, self.neocortex_path)
                    except Exception:
                        with open(self.neocortex_path, "w", encoding="utf-8") as f:
                            json.dump(nx.node_link_data(self.neocortex), f, ensure_ascii=False, indent=2)
                        if os.path.exists(temp_name):
                            try:
                                os.remove(temp_name)
                            except Exception:
                                pass
                except Exception as e:
                    logger.log_warning(f"Erro ao salvar Neocórtex atômico: {e}")
        threading.Thread(target=_salvar_bg, daemon=True).start()


    def normalizar_entidade(self, texto: str) -> str:
        """
        Normaliza e canoniza nomes de entidades no Neocórtex:
        - Converte para minúsculas e remove acentos/diacríticos.
        - Remove pontuação perimétrica e caracteres especiais.
        - Remove artigos/conectivos insignificantes no início (ex: 'o python' -> 'python').
        - Converte formas plurais simples para singular.
        """
        import re
        import unicodedata

        if not texto:
            return ""

        t = texto.strip().lower()
        t = ''.join(c for c in unicodedata.normalize('NFKD', t) if not unicodedata.combining(c))
        t = re.sub(r'[^a-z0-9\s\-]', '', t).strip()

        t = re.sub(r'^(?:o|a|os|as|um|uma|uns|umas|do|da|dos|das|no|na|nos|nas)\s+', '', t).strip()

        if len(t) > 4 and t.endswith('s') and not t.endswith('ss') and not t.endswith('is'):
            if t.endswith('oes'):
                t = t[:-3] + 'ao'
            elif t.endswith('aes'):
                t = t[:-3] + 'ao'
            elif t.endswith('ais') or t.endswith('eis') or t.endswith('ois'):
                t = t[:-2] + 'l'
            elif not t.endswith('os') or len(t) > 5:
                t = t[:-1]

        return t.strip()

    def consolidar_sinapse(self, sujeito: str, relacao: str, objeto: str, timestamp: int):
        s_norm = self.normalizar_entidade(sujeito)
        o_norm = self.normalizar_entidade(objeto)
        r = relacao.strip().lower()

        if not s_norm or not o_norm: 
            return
        
        self.neocortex.add_node(s_norm, label=s_norm)
        self.neocortex.add_node(o_norm, label=o_norm)
        
        if self.neocortex.has_edge(s_norm, o_norm):
            self.neocortex[s_norm][o_norm]["weight"] = self.neocortex[s_norm][o_norm].get("weight", 1) + 1
            self.neocortex[s_norm][o_norm]["updated_at"] = timestamp
            logger.log_neocortex(f"[Reforço] Sinapse: ({s_norm}) --[{r}]--> ({o_norm}) | Peso: {self.neocortex[s_norm][o_norm]['weight']}")
        else:
            self.neocortex.add_edge(s_norm, o_norm, relacao=r, created_at=timestamp, updated_at=timestamp, weight=1)
            logger.log_neocortex(f"[Nova Sinapse]: ({s_norm}) --[{r}]--> ({o_norm})")
            
        self._salvar_neocortex()

    # --------------------------------------------------
    # GRAVAÇÃO DE EXPERIÊNCIAS
    # --------------------------------------------------
    def memorizar_experiencia(self, texto: str, categoria: str = "dialogo"):
        ts = int(time.time())
        id_unico = f"synapse_{ts}"
        agora = time.time()

        if self.memory_mode == "human":
            logger.log_human(f"Memorizando experiência humana [{categoria}]: '{texto[:80]}...'")
            metadata = {
                "timestamp_criacao": agora,
                "ultimo_acesso": agora,
                "forca_sinaptica": 1.5,
                "acessos": 1,
                "categoria": categoria
            }
        else:
            logger.log_perfect(f"Memorizando experiência perfeita [{categoria}]: '{texto[:80]}...'")
            metadata = {
                "timestamp": ts,
                "categoria": categoria
            }

        # Log WAL (Journal)
        with open(self.wal_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"id": id_unico, "texto": texto, "timestamp": ts, "mode": self.memory_mode, "categoria": categoria}, ensure_ascii=False) + "\n")
        logger.log_wal(f"Log WAL gravado para id: '{id_unico}'")

        # ChromaDB
        try:
            self.hipocampo.add(
                documents=[texto], 
                metadatas=[metadata], 
                ids=[id_unico]
            )
            logger.log_hipocampo(f"Nova memória [{categoria}] gravada no ChromaDB.")
        except Exception as e:
            logger.log_warning(f"Erro no ChromaDB: {e}")
        
        # Extração de Triplas para Neocórtex em thread assíncrona não-bloqueante
        def _extrair_e_consolidar_bg(txt, timestamp):
            sys_p = 'Extraia triplas de conhecimento no formato JSON estrito: {"triplas": [{"sujeito": "...", "relacao": "...", "objeto": "..."}]}. APENAS JSON.'
            triplas = []
            try:
                r = requests.post(self.ollama_url, json={
                    "model": self.model_name, 
                    "prompt": f"Texto para consolidar: '{txt}'", 
                    "system": sys_p, 
                    "stream": False
                }, timeout=8).json().get("response", "")
                
                i, f = r.find("{"), r.rfind("}") + 1
                if i != -1 and f != -1 and f > i:
                    data = json.loads(r[i:f])
                    if isinstance(data, dict) and "triplas" in data:
                        triplas = data["triplas"]
            except Exception:
                pass

            # Fallback heurístico se LLM não extraiu triplas estruturadas
            if not triplas:
                triplas = self.extrair_triplas_heuristica(txt)

            for t in triplas:
                if isinstance(t, dict) and "sujeito" in t and "relacao" in t and "objeto" in t:
                    self.consolidar_sinapse(t["sujeito"], t["relacao"], t["objeto"], timestamp)

        threading.Thread(target=_extrair_e_consolidar_bg, args=(texto, ts), daemon=True).start()

    def extrair_triplas_heuristica(self, texto: str) -> list:
        """Fallback de extração sintática quando a chamada LLM falhar ou expirar."""
        import re
        txt_clean = re.sub(r'^(Usuário|NIB|Subconsciente|Pesquisa|Conhecimento)[^:]*:\s*', '', texto, flags=re.IGNORECASE)
        palavras = [re.sub(r'[^\w]', '', p).lower() for p in txt_clean.split() if len(p) >= 4]
        
        stop_words = {"para", "como", "sobre", "qual", "quais", "onde", "quando", "porque", "esta", "estao", "este", "essa", "isso", "aquilo", "mais", "muito", "voce", "estou", "estamos", "resposta", "pergunta"}
        termos = [p for p in palavras if p and p not in stop_words]
        
        triplas = []
        if len(termos) >= 2:
            s = termos[0]
            for o in termos[1:4]:
                if s != o:
                    triplas.append({"sujeito": s, "relacao": "relacionado_a", "objeto": o})
        return triplas

    # --------------------------------------------------
    # --------------------------------------------------
    # BUSCA EXTERNA EM CAMADAS (WIKIPEDIA ➔ ACADÊMICO ➔ NOTÍCIAS ➔ TENDÊNCIAS/WEB)
    # --------------------------------------------------
    def extrair_termo_busca(self, query: str) -> str:
        """Limpa saudações e frases conversacionais para isolar o termo real de busca."""
        import re
        q = query.strip()
        
        patterns = [
            r'(?:busque|pesquise|procure|sobre|termo)\s+(?:por\s+)?["\']?([^"\'.!?\n]+)["\']?',
        ]
        for pat in patterns:
            m = re.search(pat, q, re.IGNORECASE)
            if m:
                candidate = m.group(1).strip()
                cand_clean = re.sub(r'\b(não|nao|está|esta|errado|errada|correto|de verdade|por favor)\b.*$', '', candidate, flags=re.IGNORECASE).strip()
                if len(cand_clean) >= 2:
                    return cand_clean

        ruidos = [
            "olá nib", "ola nib", "falei para você que", "falei para voce que", 
            "não está correto", "nao esta correto", "pesquise e descubra o que é de verdade",
            "ainda está errado", "ainda esta errado", "busque", "pesquise", "procure", 
            "veja a letra da musica", "veja a letra da música", "o que é", "o que e"
        ]
        q_clean = q
        for r in ruidos:
            q_clean = re.sub(re.escape(r), "", q_clean, flags=re.IGNORECASE)
        q_clean = q_clean.strip(" ,.!?\"'")
        return q_clean if len(q_clean) >= 2 else query

    def eh_termo_cientifico(self, query: str) -> bool:
        """Determina se a consulta refere-se a um conceito/termo técnico-científico."""
        q_lower = query.lower()
        palavras_chave_ciencia = [
            "física", "fisica", "quântica", "quantica", "biologia", "química", "quimica", 
            "matemática", "matematica", "astronomia", "astrofísica", "astrofisica", "neuro", 
            "algoritmo", "genética", "genetica", "artigo", "paper", "teorema", "equação", 
            "equacao", "molécula", "molecula", "relatividade", "quântico", "quantico", 
            "nanotecnologia", "bactéria", "bacteria", "vírus", "virus", "célula", "celula", 
            "termodinâmica", "termodinamica", "astrobiologia", "entropia", "genoma"
        ]
        for p in palavras_chave_ciencia:
            if p in q_lower:
                return True
        return False

    def buscar_wikipedia(self, query: str) -> list:
        resultados = []
        logger.log_pesquisa_web(f"Pesquisa Web (Wikipedia) por: '{query}'")
        logger.log_busca_wikipedia(f"Pesquisando na Wikipedia por: '{query}'...")
        
        # 1. Wikipedia API PT
        try:
            url_pt = f"https://pt.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&format=json&utf8=1"
            resp = requests.get(url_pt, timeout=4).json()
            search_results = resp.get("query", {}).get("search", [])
            for item in search_results[:2]:
                titulo = item.get("title", "")
                snippet_raw = item.get("snippet", "")
                snippet = BeautifulSoup(snippet_raw, "html.parser").get_text().strip()
                if titulo and snippet:
                    resultados.append(f"[Wikipedia PT] Título: {titulo} | Resumo: {snippet}")
        except Exception:
            pass

        # 2. Wikipedia API EN (Fallback para termos em inglês como N.I.B / Black Sabbath)
        if not resultados:
            try:
                url_en = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&format=json&utf8=1"
                resp = requests.get(url_en, timeout=4).json()
                search_results = resp.get("query", {}).get("search", [])
                for item in search_results[:2]:
                    titulo = item.get("title", "")
                    snippet_raw = item.get("snippet", "")
                    snippet = BeautifulSoup(snippet_raw, "html.parser").get_text().strip()
                    if titulo and snippet:
                        resultados.append(f"[Wikipedia EN] Título: {titulo} | Resumo: {snippet}")
            except Exception:
                pass

        # 3. DuckDuckGo Wikipedia Fallback
        if not resultados:
            try:
                url_ddg_wiki = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote('site:wikipedia.org ' + query)}"
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                resp = requests.get(url_ddg_wiki, headers=headers, timeout=4)
                soup = BeautifulSoup(resp.text, 'html.parser')
                for a in soup.find_all('a', class_='result__snippet', limit=2):
                    resultados.append(f"[Wikipedia Web]: {a.get_text().strip()}")
            except Exception:
                pass

        if resultados:
            logger.log_busca_wikipedia(f"Encontrados {len(resultados)} artigos na Wikipedia.")
        else:
            logger.log_busca_wikipedia("Nenhum resultado encontrado na Wikipedia.")

        return resultados

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
          1. Wikipedia (Primeiro Lugar para definições e cultura) / Busca Acadêmica (se for termo científico)
          2. Repositórios Acadêmicos (arXiv / OpenAlex)
          3. Notícias Recentes
          4. Tendências e Web Geral
        """
        termo_limpo = self.extrair_termo_busca(query)
        logger.log_pesquisa_web(f"Pesquisa externa disparada na web para a consulta: '{query}' (Termo limpo: '{termo_limpo}')")
        
        resultados = []
        is_cientifico = self.eh_termo_cientifico(termo_limpo)
        
        # Se for termo científico ou for solicitada busca estritamente acadêmica, inicia pela busca acadêmica
        if is_cientifico or apenas_academico:
            logger.log_busca_academica(f"Termo científico/acadêmico detectado. Iniciando busca acadêmica: '{termo_limpo}'")
            resultados = self.buscar_diretorio_academico(termo_limpo)

        # 1. Wikipedia em primeiro lugar para termos gerais, culturais, termos de música, etc.
        if not resultados and not apenas_academico:
            resultados = self.buscar_wikipedia(termo_limpo)

        # 2. Busca Acadêmica (se não for termo científico e Wikipedia falhou)
        if not resultados and not is_cientifico and not apenas_academico:
            resultados = self.buscar_diretorio_academico(termo_limpo)

        # 3. Busca de Notícias
        if not resultados and not apenas_academico:
            resultados = self.buscar_noticias(termo_limpo)

        # 4. Tendências e Web Geral (fallback final)
        if not resultados and not apenas_academico:
            resultados = self.buscar_tendencias_e_web(termo_limpo)

        if not resultados:
            return "Nenhuma informação externa encontrada."

        conteudo_bruto = "\n".join(resultados)

        # Resumo sintético da web para remover ruído antes de indexar no ChromaDB
        if getattr(config, "ENABLE_WEB_SUMMARIZATION", True):
            conteudo = self.resumir_conhecimento_externo(termo_limpo, conteudo_bruto)
        else:
            conteudo = conteudo_bruto
        
        # Salva o aprendizado na memória
        id_novo = f"ext_mem_{int(time.time())}"
        self.memorizar_experiencia(f"Conhecimento pesquisado sobre '{termo_limpo}': {conteudo}", categoria="pesquisa_web")
        
        return conteudo

    def resumir_conhecimento_externo(self, consulta: str, texto_bruto: str) -> str:
        """Resume e sintetiza o conteúdo capturado da web para remover ruído antes da indexação no ChromaDB."""
        if not texto_bruto or len(texto_bruto.strip()) < 120:
            return texto_bruto

        logger.log_nib("SISTEMA NIB", f"Sintetizando e resumindo conteúdo web para '{consulta}'...", logger.Colors.BRIGHT_MAGENTA)
        sys_p = (
            "Você é um sintetizador de conhecimento objetivo. "
            "Extraia os principais fatos, definições e respostas relevantes para a pesquisa. "
            "Resuma em um texto conciso, direto e limpo em Português sem formatação desnecessária ou opiniões."
        )
        try:
            resp = httpx.post(self.ollama_url, json={
                "model": self.model_name,
                "prompt": f"Consulta do Usuário: '{consulta}'\n\nConteúdo Bruto Capturado:\n{texto_bruto[:2500]}",
                "system": sys_p,
                "stream": False,
                "options": {"temperature": 0.2}
            }, timeout=15.0)
            r = resp.json().get("response", "").strip()

            if r:
                return r
        except Exception as e:
            logger.log_warning(f"Falha ao resumir conhecimento externo: {e}")

        return texto_bruto[:1000]



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
                    doc_snippet = todas_memorias['documents'][i][:60]
                    logger.log_poda(f"Memória episódica '{doc_snippet}...' caducou (Retenção R={retencao:.2f}).")
                    self.pruning_journal.append({
                        "tipo": "episodica",
                        "id": m_id,
                        "conteudo": doc_snippet,
                        "retencao": round(retencao, 3),
                        "timestamp": agora
                    })
                    
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
                rel = data.get("relacao", "conectado_a")
                logger.log_poda(f"Conexão no Neocórtex podada: ({u}) -> ({v})")
                self.pruning_journal.append({
                    "tipo": "relacional",
                    "conteudo": f"{u} --({rel})--> {v}",
                    "retencao": round(retencao, 3),
                    "timestamp": agora
                })
                
        for u, v in arestas_para_remover:
            self.neocortex.remove_edge(u, v)
        self._salvar_neocortex()

    def obter_estatisticas_memoria(self) -> dict:
        """Retorna contadores e estatísticas da memória episódica, relacional e de curto prazo."""
        total_episodios = 0
        forca_media = 0.0
        try:
            mems = self.hipocampo.get(include=["metadatas"])
            if mems and mems.get("ids"):
                total_episodios = len(mems["ids"])
                if mems.get("metadatas"):
                    forcas = [m.get("forca_sinaptica", 1.5) for m in mems["metadatas"] if isinstance(m, dict)]
                    if forcas:
                        forca_media = round(sum(forcas) / len(forcas), 2)
        except Exception:
            pass

        return {
            "memory_mode": self.memory_mode,
            "total_episodic_memories": total_episodios,
            "neocortex_nodes": self.neocortex.number_of_nodes(),
            "neocortex_edges": self.neocortex.number_of_edges(),
            "average_synaptic_strength": forca_media,
            "working_memory_capacity": self.working_memory.capacity,
            "working_memory_size": len(self.working_memory.buffer),
            "pruning_journal": self.pruning_journal[-20:]
        }

    def obter_dados_grafo(self) -> dict:
        """Retorna o grafo de conhecimento (Neocórtex) estruturado para visualização interativa em frontend."""
        nodes = []
        edges = []
        for n in self.neocortex.nodes():
            nodes.append({"id": str(n), "label": str(n)})

        for u, v, data in self.neocortex.edges(data=True):
            rel = data.get("relacao", "conectado_a")
            peso = round(data.get("peso", 1.0), 2)
            edges.append({
                "from": str(u),
                "to": str(v),
                "label": rel,
                "weight": peso,
                "title": f"Relação: {rel} | Peso: {peso}"
            })

        return {"nodes": nodes, "edges": edges}

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

    def eh_dialogo_informal(self, consulta: str) -> bool:
        """Sinaliza se a mensagem é um diálogo social/informal (saudação, amizade, polidez)."""
        c_lower = consulta.lower().strip()
        gatilhos_informais = [
            "olá", "ola", "oi", "oie", "tudo bem", "como vai", "boa tarde", "bom dia", "boa noite",
            "tudo bom", "tudo bom por ai", "tudo bom por aí", "como está", "como esta", "tudo certo",
            "tudo ótimo", "tudo otimo", "amigo", "amiga", "amigos", "amizade", "quer ser meu", "seja meu",
            "você é meu", "voce e meu", "quem é você", "quem e voce", "qual seu nome", "obrigado", "obrigada",
            "valeu", "tchau", "até logo"
        ]
        for g in gatilhos_informais:
            if g in c_lower:
                return True
        return False

    def solicitou_aprendizado_ou_memoria(self, consulta: str) -> bool:
        """Verifica se a consulta aborda o aprendizado, memórias, conversas passadas ou capacidades do NIB."""
        c_lower = consulta.lower()
        gatilhos = [
            "o que você aprendeu", "o que voce aprendeu", "o que aprendeu",
            "aprendeu algo", "aprendeu alguma", "aprendizado autônomo", "aprendizado autonomo",
            "últimas descobertas", "ultimas descobertas", "o que você sabe", "o que voce sabe",
            "sua memória", "sua memoria", "capacidade de aprender", "consegue aprender", "pode aprender",
            "sabe aprender", "como funciona seu aprendizado",
            "conversa passada", "conversas passadas", "conversa anterior", "conversas anteriores",
            "já conversamos", "ja conversamos", "conversamos antes", "lembra de mim", "se lembra de mim",
            "sessão anterior", "sessao anterior", "sessões passadas", "sessoes passadas",
            "sessões anteriores", "sessoes anteriores", "o que conversamos", "nossa conversa",
            "diálogo passado", "dialogo passado", "interação anterior", "interacao anterior"
        ]
        for g in gatilhos:
            if g in c_lower:
                return True
        return False

    # --------------------------------------------------
    # RESGATE DE MEMÓRIA
    # --------------------------------------------------
    def resgatar_memoria_relevante(self, consulta: str) -> str:
        # Se for uma saudação/diálogo informal simples e sem pedido explícito de histórico/pesquisa, não carrega memórias antigas
        if self.eh_dialogo_informal(consulta) and not self.solicitou_aprendizado_ou_memoria(consulta) and not self.solicitou_pesquisa_ou_correcao(consulta):
            return "Nenhuma memória episódica necessária para esta saudação informal."

        agora = time.time()
        tag_modo = "MEMÓRIA HUMANA" if self.memory_mode == "human" else "MEMÓRIA PERFEITA"
        logger.log_nib(tag_modo, f"Consultando memória híbrida para: '{consulta}'", logger.Colors.BRIGHT_YELLOW if self.memory_mode == "human" else logger.Colors.BRIGHT_CYAN)

        w_vec = getattr(config, "HYBRID_RAG_VECTOR_WEIGHT", 0.6)
        w_graph = getattr(config, "HYBRID_RAG_GRAPH_WEIGHT", 0.4)

        candidatos_hibridos = []
        ids_episodicos_acessados = []

        # 1. RAG Vetorial (Hipocampo - ChromaDB)
        try:
            query_texts_busca = [consulta]
            if self.solicitou_aprendizado_ou_memoria(consulta):
                query_texts_busca.extend([
                    "Aprendizado autônomo descobertas recentes",
                    "Usuário NIB conversa diálogo interação passada"
                ])

            res_vec = self.hipocampo.query(
                query_texts=query_texts_busca, 
                n_results=3,
                include=["documents", "metadatas", "distances"]
            )
            if res_vec and res_vec.get("documents"):
                for g_idx, group in enumerate(res_vec["documents"]):
                    for i, doc in enumerate(group):
                        m_id = res_vec["ids"][g_idx][i] if (res_vec.get("ids") and len(res_vec["ids"]) > g_idx and len(res_vec["ids"][g_idx]) > i) else f"id_{i}"
                        meta = (res_vec["metadatas"][g_idx][i] if (res_vec.get("metadatas") and len(res_vec["metadatas"]) > g_idx and len(res_vec["metadatas"][g_idx]) > i) else {}) or {}
                        dist = res_vec["distances"][g_idx][i] if (res_vec.get("distances") and len(res_vec["distances"]) > g_idx and len(res_vec["distances"][g_idx]) > i) else 1.0

                        # Descartar memórias vetoriais de baixa relevância (distância > 0.6) a menos que solicitado explicitamente
                        if dist > 0.6 and not self.solicitou_aprendizado_ou_memoria(consulta):
                            continue

                        score_vec = 1.0 / (1.0 + dist)
                        score_hibrido = w_vec * score_vec

                        candidatos_hibridos.append({
                            "texto": f"[Memória Episódica]: {doc}",
                            "score": score_hibrido,
                            "tipo": "vetorial",
                            "id": m_id,
                            "meta": meta
                        })
                        ids_episodicos_acessados.append((m_id, meta))

            if self.solicitou_aprendizado_ou_memoria(consulta):
                try:
                    ultimas_mems = self.hipocampo.get(limit=5, include=["documents", "metadatas"])
                    if ultimas_mems and ultimas_mems.get("documents"):
                        for i, doc in enumerate(ultimas_mems["documents"]):
                            m_id = ultimas_mems["ids"][i] if ultimas_mems.get("ids") else f"recent_{i}"
                            meta = ultimas_mems["metadatas"][i] if (ultimas_mems.get("metadatas") and len(ultimas_mems["metadatas"]) > i) else {}
                            candidatos_hibridos.append({
                                "texto": f"[Memória Episódica Histórica]: {doc}",
                                "score": 0.55,
                                "tipo": "historico_recente",
                                "id": m_id,
                                "meta": meta
                            })
                except Exception:
                    pass
        except Exception as e:
            logger.log_warning(f"Erro ao consultar Hipocampo: {e}")

        # 2. RAG Relacional (Neocórtex - GraphRAG/NetworkX)
        stopwords = {
            "ola", "olá", "como", "qual", "quais", "para", "sobre", "você", "voce", 
            "onde", "quando", "quem", "tudo", "mais", "muito", "este", "esta", "estou", 
            "está", "estao", "estão", "pode", "podem", "fazer", "bom", "boa", "bem"
        }
        palavras_brutas = [p.strip().lower() for p in consulta.split() if len(p) > 2 and p.strip().lower() not in stopwords]
        nos_alvo = set()
        for p in palavras_brutas:
            if p: nos_alvo.add(p)
            p_norm = self.normalizar_entidade(p)
            if p_norm: nos_alvo.add(p_norm)

        for p in nos_alvo:
            if self.neocortex.has_node(p):
                for vz in self.neocortex.neighbors(p):
                    edge = self.neocortex[p][vz]
                    rel = edge.get("relacao", "relacionado_a")
                    peso = edge.get("peso", 1.0)
                    score_graph = min(1.0, peso / 2.0)
                    score_hibrido = w_graph * score_graph

                    if self.memory_mode == "human":
                        step_graph = getattr(config, "GRAPH_REINFORCEMENT_STEP", 0.3)
                        edge["peso"] = peso + step_graph
                        edge["ultimo_acesso"] = agora

                    candidatos_hibridos.append({
                        "texto": f"[Neocórtex]: {p} --({rel})--> {vz}",
                        "score": score_hibrido,
                        "tipo": "relacional"
                    })

                for ant in self.neocortex.predecessors(p):
                    edge = self.neocortex[ant][p]
                    rel = edge.get("relacao", "relacionado_a")
                    peso = edge.get("peso", 1.0)
                    score_graph = min(1.0, peso / 2.0)
                    score_hibrido = w_graph * score_graph

                    if self.memory_mode == "human":
                        step_graph = getattr(config, "GRAPH_REINFORCEMENT_STEP", 0.3)
                        edge["peso"] = peso + step_graph
                        edge["ultimo_acesso"] = agora

                    candidatos_hibridos.append({
                        "texto": f"[Neocórtex]: {ant} --({rel})--> {p}",
                        "score": score_hibrido,
                        "tipo": "relacional"
                    })

        # Reforço sináptico no Modo Humano
        if self.memory_mode == "human":
            step_episodic = getattr(config, "EPISODIC_REINFORCEMENT_STEP", 0.5)
            for m_id, meta in ids_episodicos_acessados:
                meta = meta or {}
                forca_atual = meta.get("forca_sinaptica", 1.5)
                nova_forca = forca_atual + step_episodic
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
            self._salvar_neocortex()

        # Ordenação por Score Híbrido
        candidatos_hibridos.sort(key=lambda x: x["score"], reverse=True)

        # 3. Forçar Pesquisa Web em caso de Solicitação Explícita ou Correção do Usuário
        pesquisa_extra = ""
        forcar_pesquisa = self.solicitou_pesquisa_ou_correcao(consulta)
        if forcar_pesquisa:
            logger.log_nib("REQUISIÇÃO/CORREÇÃO", f"Solicitação explícita de busca/correção detectada: '{consulta}'", logger.Colors.BRIGHT_MAGENTA)
            conhecimento = self.pesquisar_conhecimento_externo(consulta, apenas_academico=False)
            if conhecimento and "Nenhuma informação" not in conhecimento:
                pesquisa_extra = f"• [Pesquisa Web (Solicitada)]: {conhecimento}"

        # 4. Tratamento de Lacuna de Conhecimento quando nada for encontrado na memória local (ignora se for diálogo informal)
        elif (not candidatos_hibridos or len(candidatos_hibridos) == 0) and not self.eh_dialogo_informal(consulta):
            logger.log_nib("SISTEMA NIB", "Informação ausente na memória local. Disparando pesquisa externa em camadas (Acadêmica ➔ Notícias ➔ Tendências/Web)...", logger.Colors.BRIGHT_YELLOW)
            conhecimento = self.pesquisar_conhecimento_externo(consulta, apenas_academico=False)
            if conhecimento and "Nenhuma informação" not in conhecimento:
                pesquisa_extra = f"• [Conhecimento Externo Adquirido]: {conhecimento}"

        # Categorização e Organização Estruturada dos Registros
        working_str = self.obter_contexto_trabalho().lower()
        dialogos = []
        descobertas = []
        pesquisas_web = []
        relacoes_neocortex = []
        vistos = set()

        if pesquisa_extra:
            pesquisas_web.append(pesquisa_extra)

        for item in candidatos_hibridos:
            txt = item["texto"]
            txt_clean = txt.replace("[Memória Episódica]: ", "").replace("[Memória Episódica Histórica]: ", "").replace("[Neocórtex]: ", "").strip()
            
            if txt_clean.lower() in working_str or txt_clean.lower() in vistos:
                continue
            vistos.add(txt_clean.lower())

            if item.get("tipo") == "relacional" or "[Neocórtex]" in txt:
                relacoes_neocortex.append(f"• {txt}")
            else:
                cat = item.get("meta", {}).get("categoria", "")
                if cat == "aprendizado_autonomo" or "Aprendizado criativo" in txt_clean or "Aprendizado autônomo" in txt_clean:
                    descobertas.append(f"• {txt_clean}")
                elif cat == "pesquisa_web" or "Conhecimento pesquisado" in txt_clean or "[Artigo" in txt_clean:
                    pesquisas_web.append(f"• {txt_clean}")
                else:
                    dialogos.append(f"• {txt_clean}")

        secoes = []
        if dialogos:
            secoes.append("--- HISTÓRICO DE DIÁLOGOS PASSADOS COM O USUÁRIO ---\n" + "\n".join(dialogos[:4]))
        if descobertas:
            secoes.append("--- CONHECIMENTOS & DESCOBERTAS AUTÔNOMAS ---\n" + "\n".join(descobertas[:3]))
        if pesquisas_web:
            secoes.append("--- REFERÊNCIAS E PESQUISAS EXTERNAS (WEB/ACADÊMICO) ---\n" + "\n".join(pesquisas_web[:3]))
        if relacoes_neocortex:
            secoes.append("--- CONEXÕES SEMÂNTICAS DO NEOCÓRTEX (GRAPHRAG) ---\n" + "\n".join(relacoes_neocortex[:5]))

        if not secoes:
            return "Nenhuma memória episódica específica recuperada. Porém, todas as interações e conhecimentos passados estão preservados permanentemente na sua memória de longo prazo (Hipocampo/Neocórtex)."
        return "\n\n".join(secoes)

    def consolidar_memorias(self) -> dict:
        """
        Executa a Consolidação Sináptica Noturna (Sono REM) do NIB.
        Varre as memórias episódicas do Hipocampo e os nós do Neocórtex,
        identifica memórias de alta retenção (Força Sináptica S > 1.5),
        reforça suas conexões no Grafo Semântico (+0.8), cria novas associações entre 
        conceitos que co-ocorrem e salva o estado consolidado.
        """
        logger.log_nib("SONO REM", "🌙 Entrando em estado de repouso e consolidação sináptica noturna...", logger.Colors.BRIGHT_CYAN)
        agora = time.time()
        memorias_consolidadas = 0
        nos_reforcados = 0
        sinapses_criadas = 0

        # 1. Varre o Hipocampo em busca de memórias com alta estabilidade
        try:
            dados = self.hipocampo.get(include=["documents", "metadatas"])
            ids = dados.get("ids", [])
            docs = dados.get("documents", [])
            metas = dados.get("metadatas", [])

            for m_id, doc, meta in zip(ids, docs, metas):
                forca = meta.get("forca_sinaptica", 1.0)
                if forca >= 1.2:
                    memorias_consolidadas += 1
                    nova_forca = min(10.0, forca + 0.8)
                    meta["forca_sinaptica"] = nova_forca
                    meta["ultimo_acesso"] = agora
                    try:
                        self.hipocampo.update(ids=[m_id], metadatas=[meta])
                    except Exception:
                        pass
                    
                    # Extrai conceitos principais da memória e reforça no Neocórtex
                    palavras = [p.lower() for p in doc.split() if len(p) > 4 and p.isalpha()]
                    if len(palavras) >= 2:
                        n1, n2 = palavras[0], palavras[1]
                        if self.neocortex.has_node(n1) and self.neocortex.has_node(n2):
                            nos_reforcados += 2
                            if self.neocortex.has_edge(n1, n2):
                                self.neocortex[n1][n2]["weight"] = min(5.0, self.neocortex[n1][n2].get("weight", 1.0) + 0.5)
                            else:
                                self.neocortex.add_edge(n1, n2, weight=1.0, relation="associado_no_sono")
                                sinapses_criadas += 1
        except Exception as e:
            logger.log_nib("SONO REM ERRO", f"Falha na consolidação do Hipocampo: {e}", logger.Colors.RED)

        self._salvar_neocortex()

        resumo = (
            f"🌙 Sono REM concluído: {memorias_consolidadas} memórias episódicas consolidadas, "
            f"{nos_reforcados} nós do Neocórtex reforçados e {sinapses_criadas} novas sinapses associativas criadas!"
        )
        logger.log_nib("SONO REM SUCESSO", resumo, logger.Colors.BRIGHT_GREEN)

        return {
            "status": "success",
            "memorias_consolidadas": memorias_consolidadas,
            "nos_reforcados": nos_reforcados,
            "sinapses_criadas": sinapses_criadas,
            "resumo": resumo
        }

    def obter_metricas_benchmark(self) -> dict:
        """Calcula métricas quantitativas de desempenho cognitivo e retenção de memória."""
        nos_count = self.neocortex.number_of_nodes()
        arestas_count = self.neocortex.number_of_edges()
        
        episodios_count = 0
        forca_media = 0.0
        try:
            dados = self.hipocampo.get(include=["metadatas"])
            metas = dados.get("metadatas", [])
            episodios_count = len(metas)
            if episodios_count > 0:
                forca_media = sum(m.get("forca_sinaptica", 1.0) for m in metas) / episodios_count
        except Exception:
            pass

        densidade_grafo = (2.0 * arestas_count / (nos_count * (nos_count - 1))) if nos_count > 1 else 0.0

        return {
            "modo_memoria": self.memory_mode,
            "total_memorias_episodicas": episodios_count,
            "forca_sinaptica_media": round(forca_media, 2),
            "nos_neocortex": nos_count,
            "arestas_neocortex": arestas_count,
            "densidade_grafo": round(densidade_grafo, 4),
            "aprendizado_autonomo_ativo": self.learning_enabled,
            "personalidade_ativa": self.active_personality.name if self.active_personality else "Nenhuma"
        }