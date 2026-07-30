import os

# ==========================================
# 1. CARREGAMENTO DE VARIÁVEIS DE AMBIENTE (.env)
# ==========================================
try:
    from dotenv import load_dotenv
    _env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(_env_file):
        load_dotenv(_env_file)
except Exception:
    pass

# ==========================================
# 2. CARREGAMENTO DE CONFIGURAÇÃO YAML (config.yaml)
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
YAML_CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")

_yaml_config = {}
if os.path.exists(YAML_CONFIG_PATH):
    try:
        import yaml
        with open(YAML_CONFIG_PATH, "r", encoding="utf-8") as f:
            _yaml_config = yaml.safe_load(f) or {}
    except Exception:
        pass

# ==========================================
# 3. DIRETÓRIOS E BANCO DE DADOS (NIB)
# ==========================================
STORAGE_DIR = os.path.join(BASE_DIR, "nib_storage")
HIPPOCAMPUS_DIR = os.path.join(STORAGE_DIR, "hippocampus")
NEOCORTEX_FILE = os.path.join(STORAGE_DIR, "neocortex_graph.json")
SYNAPTIC_JOURNAL = os.path.join(STORAGE_DIR, "synaptic_journal.jsonl")

HUMAN_STORAGE_DIR = os.path.join(STORAGE_DIR, "memoria_humana")
PERFECT_STORAGE_DIR = os.path.join(BASE_DIR, "memoria_perfeita_db")

os.makedirs(STORAGE_DIR, exist_ok=True)
os.makedirs(HIPPOCAMPUS_DIR, exist_ok=True)
os.makedirs(HUMAN_STORAGE_DIR, exist_ok=True)
os.makedirs(PERFECT_STORAGE_DIR, exist_ok=True)

# ==========================================
# 4. PARÂMETROS COGNITIVOS E MODOS DE MEMÓRIA
# ==========================================
DEFAULT_MEMORY_MODE = os.getenv("DEFAULT_MEMORY_MODE", "human")

WORKING_MEMORY_CAPACITY = int(
    os.getenv("WORKING_MEMORY_CAPACITY", 
    _yaml_config.get("working_memory_capacity", 6))
)

_hybrid_rag_cfg = _yaml_config.get("hybrid_rag", {})
HYBRID_RAG_VECTOR_WEIGHT = float(
    os.getenv("HYBRID_RAG_VECTOR_WEIGHT", 
    _hybrid_rag_cfg.get("vector_weight", 0.6))
)
HYBRID_RAG_GRAPH_WEIGHT = float(
    os.getenv("HYBRID_RAG_GRAPH_WEIGHT", 
    _hybrid_rag_cfg.get("graph_weight", 0.4))
)

_web_sum_cfg = _yaml_config.get("web_summarization", {})
ENABLE_WEB_SUMMARIZATION = str(
    os.getenv("ENABLE_WEB_SUMMARIZATION", 
    _web_sum_cfg.get("enabled", True))
).lower() in ("true", "1", "yes")

_hebbian_cfg = _yaml_config.get("hebbian_pruning", {})
HEBBIAN_PRUNING_THRESHOLD = float(
    os.getenv("HEBBIAN_PRUNING_THRESHOLD", 
    _hebbian_cfg.get("threshold", 0.15))
)

EPISODIC_REINFORCEMENT_STEP = float(
    os.getenv("EPISODIC_REINFORCEMENT_STEP", 
    _hebbian_cfg.get("episodic_reinforcement_step", 0.5))
)

GRAPH_REINFORCEMENT_STEP = float(
    os.getenv("GRAPH_REINFORCEMENT_STEP", 
    _hebbian_cfg.get("graph_reinforcement_step", 0.3))
)

_temp_cfg = _yaml_config.get("temperature", {})
DEFAULT_TEMPERATURE = float(
    os.getenv("DEFAULT_TEMPERATURE", 
    _temp_cfg.get("default", 0.4))
)

# ==========================================
# 5. CHAVES DE API E SERVIÇOS EXTERNOS
# ==========================================
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
OPENALEX_EMAIL = os.getenv("OPENALEX_EMAIL", "")

# ==========================================
# 6. CONFIGURAÇÕES DO OLLAMA (MODELO LOCAL)
# ==========================================
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", 60.0))

def _detect_ollama_model():
    try:
        import requests
        tags_url = OLLAMA_URL.replace("/api/generate", "/api/tags")
        resp = requests.get(tags_url, timeout=2).json()
        models = [m["name"] for m in resp.get("models", [])]
        if models:
            if "qwen2.5-coder:latest" in models:
                return "qwen2.5-coder:latest"
            if "qwen2.5:3b" in models:
                return "qwen2.5:3b"
            return models[0]
    except Exception:
        pass
    return "qwen2.5:3b"

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", _detect_ollama_model())

# ==========================================
# 7. SERVIDOR FASTAPI
# ==========================================
SERVER_HOST = os.getenv("SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))