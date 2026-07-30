import os
import json
import math
import time
import requests
import httpx
import urllib.parse

import chromadb
import networkx as nx
from bs4 import BeautifulSoup

import config
import logger_nib as logger
from working_memory import WorkingMemory

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

        # 3. MEMÓRIA DE TRABALHO (Córtex Pré-Frontal - Contexto de Curto Prazo)
        self.working_memory = WorkingMemory(capacity=getattr(config, "WORKING_MEMORY_CAPACITY", 6))

        # 4. CONTROLES DE ESTADO E REGISTRO NIB
        self.learning_enabled = False  # Inicia desligado (OFF) por padrão
        self.personality_enabled = True # Inicia ligado (ON) por padrão
        self.pruning_journal = []      # Registro de podas sinápticas
        self.wal_path = config.SYNAPTIC_JOURNAL
        self.ollama_url = config.OLLAMA_URL
        self.model_name = config.OLLAMA_MODEL

        logger.log_nib("NIB INIT", f"Cérebro inicializado no Modo: [{self.memory_mode.upper()}] | Working Memory Cap: {self.working_memory.capacity}", logger.Colors.BRIGHT_CYAN)



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
        self.memorizar_experiencia(f"Conhecimento pesquisado sobre '{termo_limpo}': {conteudo}")
        
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
        agora = time.time()
        tag_modo = "MEMÓRIA HUMANA" if self.memory_mode == "human" else "MEMÓRIA PERFEITA"
        logger.log_nib(tag_modo, f"Consultando memória híbrida para: '{consulta}'", logger.Colors.BRIGHT_YELLOW if self.memory_mode == "human" else logger.Colors.BRIGHT_CYAN)

        w_vec = getattr(config, "HYBRID_RAG_VECTOR_WEIGHT", 0.6)
        w_graph = getattr(config, "HYBRID_RAG_GRAPH_WEIGHT", 0.4)

        candidatos_hibridos = []
        ids_episodicos_acessados = []

        # 1. RAG Vetorial (Hipocampo - ChromaDB)
        try:
            res_vec = self.hipocampo.query(
                query_texts=[consulta], 
                n_results=3,
                include=["documents", "metadatas", "distances"]
            )
            if res_vec and res_vec.get("documents") and res_vec["documents"][0]:
                for i, doc in enumerate(res_vec["documents"][0]):
                    m_id = res_vec["ids"][0][i]
                    meta = res_vec["metadatas"][0][i] if res_vec.get("metadatas") else {}
                    dist = res_vec["distances"][0][i] if (res_vec.get("distances") and res_vec["distances"][0]) else 1.0

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
        except Exception as e:
            logger.log_warning(f"Erro ao consultar Hipocampo: {e}")

        # 2. RAG Relacional (Neocórtex - GraphRAG/NetworkX)
        palavras = [p.strip().lower() for p in consulta.split() if len(p) > 3]
        for p in palavras:
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
        contexto = [item["texto"] for item in candidatos_hibridos]

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

        # Remoção de duplicados preservando ordem de ranking
        vistos = set()
        contexto_unico = []
        for item in contexto:
            if item not in vistos:
                vistos.add(item)
                contexto_unico.append(item)

        return "\n".join(contexto_unico)