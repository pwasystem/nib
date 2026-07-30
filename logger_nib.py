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

def _safe_print(msg: str):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('ascii', errors='replace').decode('ascii'))

def log_nib(tag: str, msg: str, color: str = Colors.BRIGHT_CYAN):
    _safe_print(f"{color}[{tag}]{Colors.RESET} {msg}")

def log_human(msg: str):
    _safe_print(f"{Colors.BRIGHT_YELLOW}[MEMÓRIA HUMANA]{Colors.RESET} {msg}")

def log_perfect(msg: str):
    _safe_print(f"{Colors.BRIGHT_CYAN}[MEMÓRIA PERFEITA]{Colors.RESET} {msg}")

def log_hipocampo(msg: str):
    _safe_print(f"{Colors.BRIGHT_GREEN}[HIPOCAMPO]{Colors.RESET} {msg}")

def log_neocortex(msg: str):
    _safe_print(f"{Colors.BRIGHT_MAGENTA}[NEOCÓRTEX]{Colors.RESET} {msg}")

def log_poda(msg: str):
    _safe_print(f"{Colors.BRIGHT_RED}[PODA SINÁPTICA]{Colors.RESET} {msg}")

def log_reforco(msg: str):
    _safe_print(f"{Colors.BRIGHT_GREEN}[REFORÇO SINÁPTICO]{Colors.RESET} {msg}")

def log_busca(msg: str):
    _safe_print(f"{Colors.BRIGHT_BLUE}[BUSCA ACADÊMICA/WEB]{Colors.RESET} {msg}")

def log_busca_academica(msg: str):
    _safe_print(f"{Colors.BRIGHT_BLUE}🎓 [BUSCA ACADÊMICA]{Colors.RESET} {msg}")

def log_busca_noticias(msg: str):
    _safe_print(f"{Colors.BRIGHT_YELLOW}📰 [BUSCA NOTÍCIAS]{Colors.RESET} {msg}")

def log_busca_tendencias(msg: str):
    _safe_print(f"{Colors.BRIGHT_CYAN}🔥 [BUSCA TENDÊNCIAS/WEB]{Colors.RESET} {msg}")

def log_wal(msg: str):
    _safe_print(f"{Colors.BRIGHT_WHITE}[LOG WAL]{Colors.RESET} {msg}")

def log_criatividade(msg: str):
    _safe_print(f"{Colors.BRIGHT_MAGENTA}🎨 [CRIATIVIDADE NIB]{Colors.RESET} {msg}")

def log_success(msg: str):
    _safe_print(f"{Colors.BRIGHT_GREEN}✓ {msg}{Colors.RESET}")

def log_warning(msg: str):
    _safe_print(f"{Colors.BRIGHT_YELLOW}⚠️ {msg}{Colors.RESET}")

def log_error(msg: str):
    _safe_print(f"{Colors.BRIGHT_RED}❌ {msg}{Colors.RESET}")
