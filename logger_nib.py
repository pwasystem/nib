import os
import sys

# Força o encoding UTF-8 no stdout e stderr para evitar UnicodeEncodeError no Windows (cp1252)
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Ativa o suporte a sequências de escape ANSI no terminal do Windows (cmd/powershell)
if os.name == 'nt':
    os.system('')

class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    # Cores de Texto
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Cores Brilhantes
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

import collections
import time

# Buffer em memória para agregação de logs no Dashboard
LOG_BUFFER = collections.deque(maxlen=300)

def _append_log(tag: str, msg: str, level: str = "info"):
    entry = {
        "timestamp": time.strftime("%H:%M:%S"),
        "tag": tag,
        "msg": msg,
        "level": level
    }
    LOG_BUFFER.append(entry)

def get_recent_logs(limit: int = 200):
    return list(LOG_BUFFER)[-limit:]

def clear_logs():
    LOG_BUFFER.clear()

def _safe_print(msg: str):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('ascii', errors='replace').decode('ascii'))

def log_nib(tag: str, msg: str, color: str = Colors.BRIGHT_CYAN):
    _append_log(tag, msg, "info")
    _safe_print(f"{color}[{tag}]{Colors.RESET} {msg}")

def log_human(msg: str):
    _append_log("MEMÓRIA HUMANA", msg, "info")
    _safe_print(f"{Colors.BRIGHT_YELLOW}[MEMÓRIA HUMANA]{Colors.RESET} {msg}")

def log_perfect(msg: str):
    _append_log("MEMÓRIA PERFEITA", msg, "info")
    _safe_print(f"{Colors.BRIGHT_CYAN}[MEMÓRIA PERFEITA]{Colors.RESET} {msg}")

def log_hipocampo(msg: str):
    _append_log("HIPOCAMPO", msg, "info")
    _safe_print(f"{Colors.BRIGHT_GREEN}[HIPOCAMPO]{Colors.RESET} {msg}")

def log_neocortex(msg: str):
    _append_log("NEOCÓRTEX", msg, "info")
    _safe_print(f"{Colors.BRIGHT_MAGENTA}[NEOCÓRTEX]{Colors.RESET} {msg}")

def log_poda(msg: str):
    _append_log("PODA SINÁPTICA", msg, "warning")
    _safe_print(f"{Colors.BRIGHT_RED}[PODA SINÁPTICA]{Colors.RESET} {msg}")

def log_reforco(msg: str):
    _append_log("REFORÇO SINÁPTICO", msg, "info")
    _safe_print(f"{Colors.BRIGHT_GREEN}[REFORÇO SINÁPTICO]{Colors.RESET} {msg}")

def log_busca(msg: str):
    _append_log("BUSCA ACADÊMICA/WEB", msg, "info")
    _safe_print(f"{Colors.BRIGHT_BLUE}[BUSCA ACADÊMICA/WEB]{Colors.RESET} {msg}")

def log_pesquisa_web(msg: str):
    _append_log("PESQUISA WEB", msg, "info")
    _safe_print(f"{Colors.BRIGHT_CYAN}🌐 [PESQUISA WEB]{Colors.RESET} {msg}")

def log_busca_wikipedia(msg: str):
    _append_log("BUSCA WIKIPEDIA", msg, "info")
    _safe_print(f"{Colors.BRIGHT_MAGENTA}📚 [BUSCA WIKIPEDIA]{Colors.RESET} {msg}")

def log_busca_academica(msg: str):
    _append_log("BUSCA ACADÊMICA", msg, "info")
    _safe_print(f"{Colors.BRIGHT_BLUE}🎓 [BUSCA ACADÊMICA]{Colors.RESET} {msg}")

def log_busca_noticias(msg: str):
    _append_log("BUSCA NOTÍCIAS", msg, "info")
    _safe_print(f"{Colors.BRIGHT_YELLOW}📰 [BUSCA NOTÍCIAS]{Colors.RESET} {msg}")

def log_busca_tendencias(msg: str):
    _append_log("BUSCA TENDÊNCIAS", msg, "info")
    _safe_print(f"{Colors.BRIGHT_CYAN}🔥 [BUSCA TENDÊNCIAS/WEB]{Colors.RESET} {msg}")

def log_wal(msg: str):
    _append_log("LOG WAL", msg, "info")
    _safe_print(f"{Colors.BRIGHT_WHITE}[LOG WAL]{Colors.RESET} {msg}")

def log_criatividade(msg: str):
    _append_log("CRIATIVIDADE NIB", msg, "info")
    _safe_print(f"{Colors.BRIGHT_MAGENTA}🎨 [CRIATIVIDADE NIB]{Colors.RESET} {msg}")

def log_success(msg: str):
    _append_log("SUCESSO", msg, "success")
    _safe_print(f"{Colors.BRIGHT_GREEN}✓ {msg}{Colors.RESET}")

def log_warning(msg: str):
    _append_log("AVISO", msg, "warning")
    _safe_print(f"{Colors.BRIGHT_YELLOW}⚠️ {msg}{Colors.RESET}")

def log_error(msg: str):
    _append_log("ERRO", msg, "error")
    _safe_print(f"{Colors.BRIGHT_RED}❌ {msg}{Colors.RESET}")
