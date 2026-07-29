import os
import json
import time
import requests
import chromadb
import networkx as nx
import config

class NeuroInformatikBrain:
    """
    Núcleo Integrado Biológico (NIB) - Gerenciador Neocortical e Hipocampal.
    """
    def __init__(self):
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

    # --------------------------------------------------
    # NEOCÓRTEX (Grafo de Conexões)
    # --------------------------------------------------
    def _carregar_neocortex(self):
        if os.path.exists(self.neocortex_path):
            try:
                with open(self.neocortex_path, "r", encoding="utf-8") as f:
                    self.neocortex = nx.node_link_graph(json.load(f))
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
            print(f"   [NEOCORTEX - Reforco] Sinapse: ({s}) --[{r}]--> ({o}) | Peso: {self.neocortex[s][o]['weight']}")
        else:
            self.neocortex.add_edge(s, o, relacao=r, created_at=timestamp, updated_at=timestamp, weight=1)
            print(f"   [NEOCORTEX - Nova Sinapse]: ({s}) --[{r}]--> ({o})")
            
        self._salvar_neocortex()

    # --------------------------------------------------
    # HIPOCAMPO E GRAVAÇÃO PERPÉTUA
    # --------------------------------------------------
    def memorizar_experiencia(self, texto: str):
        ts = int(time.time())
        id_unico = f"synapse_{ts}"
        
        print("\n" + "=" * 60)
        print(f"[NIB MEMORIZANDO EXPERIENCIA]: {texto[:100]}...")
        
        # Log de Proteção (WAL)
        with open(self.wal_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"id": id_unico, "texto": texto, "timestamp": ts}, ensure_ascii=False) + "\n")

        # Inserção no Hipocampo (ChromaDB)
        try:
            self.hipocampo.add(
                documents=[texto], 
                metadatas=[{"timestamp": ts}], 
                ids=[id_unico]
            )
            print("   [HIPOCAMPO] Nova memoria episodica gravada no ChromaDB.")
        except Exception as e:
            print(f"   [HIPOCAMPO ERROR]: {e}")
        
        # Extração de Triplas para o Neocórtex
        sys_p = 'Extraia triplas de conhecimento no formato JSON estrito: {"triplas": [{"sujeito": "...", "relacao": "...", "objeto": "..."}]}. APENAS JSON.'
        try:
            r = requests.post(self.ollama_url, json={
                "model": self.model_name, 
                "prompt": f"Texto para consolidar: '{texto}'", 
                "system": sys_p, 
                "stream": False
            }, timeout=5).json().get("response", "")
            
            i, f = r.find("{"), r.rfind("}") + 1
            if i != -1 and f != -1 and f > i:
                data = json.loads(r[i:f])
                if isinstance(data, dict):
                    for t in data.get("triplas", []):
                        if isinstance(t, dict) and "sujeito" in t and "relacao" in t and "objeto" in t:
                            self.consolidar_sinapse(t["sujeito"], t["relacao"], t["objeto"], ts)
        except Exception:
            pass
        print("=" * 60 + "\n")

    def resgatar_memoria_relevante(self, consulta: str) -> str:
        contexto = []
        hipocampo_encontrado = []
        neocortex_encontrado = []

        print("\n" + "=" * 60)
        print(f"[NIB - CONSULTA DE MEMORIA] Prompt: '{consulta}'")
        print("=" * 60)
        
        # Busca por similaridade vetorial no Hipocampo
        try:
            res_vec = self.hipocampo.query(query_texts=[consulta], n_results=2)
            if res_vec and res_vec.get("documents") and res_vec["documents"][0]:
                for doc in res_vec["documents"][0]:
                    hipocampo_encontrado.append(doc)
                    contexto.append(f"[Lembrança Hipocampal]: {doc}")
        except Exception as e:
            print(f"   [HIPOCAMPO QUERY ERROR]: {e}")

        if hipocampo_encontrado:
            print(f"[HIPOCAMPO - Vetorial] {len(hipocampo_encontrado)} memorias episodicas encontradas:")
            for idx, item in enumerate(hipocampo_encontrado, 1):
                item_curto = item[:90] + ("..." if len(item) > 90 else "")
                print(f"   |- #{idx}: {item_curto}")
        else:
            print("[HIPOCAMPO - Vetorial] Nenhuma memoria episodica similar encontrada.")
            
        # Busca de grafos associativos no Neocórtex
        palavras = [p.strip().lower() for p in consulta.split() if len(p) > 3]
        for p in palavras:
            if self.neocortex.has_node(p):
                for vz in self.neocortex.neighbors(p):
                    rel = self.neocortex[p][vz].get("relacao", "relacionado_a")
                    item_str = f"{p} --({rel})--> {vz}"
                    neocortex_encontrado.append(item_str)
                    contexto.append(f"[Neocórtex]: {item_str}")
                for ant in self.neocortex.predecessors(p):
                    rel = self.neocortex[ant][p].get("relacao", "relacionado_a")
                    item_str = f"{ant} --({rel})--> {p}"
                    neocortex_encontrado.append(item_str)
                    contexto.append(f"[Neocórtex]: {item_str}")

        if neocortex_encontrado:
            uniques = list(set(neocortex_encontrado))
            print(f"[NEOCORTEX - Grafo] {len(uniques)} sinapses associativas encontradas:")
            for idx, item in enumerate(uniques, 1):
                print(f"   |- #{idx}: {item}")
        else:
            print("[NEOCORTEX - Grafo] Nenhuma sinapse associativa encontrada.")

        print("=" * 60 + "\n")
                    
        return "\n".join(list(set(contexto)))