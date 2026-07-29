import os

# ==========================================
# DIRETIROS E CAMINHO DO BANCO DE DADOS (NIB)
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STORAGE_DIR = os.path.join(BASE_DIR, "nib_storage")

# Subpastas do Hipocampo e Neocórtex
HIPPOCAMPUS_DIR = os.path.join(STORAGE_DIR, "hippocampus")
NEOCORTEX_FILE = os.path.join(STORAGE_DIR, "neocortex_graph.json")
SYNAPTIC_JOURNAL = os.path.join(STORAGE_DIR, "synaptic_journal.jsonl")

# Garantia de criação do diretório físico
os.makedirs(STORAGE_DIR, exist_ok=True)
os.makedirs(HIPPOCAMPUS_DIR, exist_ok=True)

# ==========================================
# CONFIGURAÇÕES DO OLLAMA (MODELO LOCAL)
# ==========================================
OLLAMA_URL = "http://localhost:11434/api/generate"
def _detect_ollama_model():
    try:
        import requests
        resp = requests.get("http://localhost:11434/api/tags", timeout=2).json()
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

OLLAMA_MODEL = _detect_ollama_model()

# ==========================================
# SERVIDOR FASTAPI
# ==========================================
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000