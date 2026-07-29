import os
import sys

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

def log_nib(tag: str, msg: str, color: str = Colors.BRIGHT_CYAN):
    print(f"{color}[{tag}]{Colors.RESET} {msg}")

def log_human(msg: str):
    print(f"{Colors.BRIGHT_YELLOW}[MEMÓRIA HUMANA]{Colors.RESET} {msg}")

def log_perfect(msg: str):
    print(f"{Colors.BRIGHT_CYAN}[MEMÓRIA PERFEITA]{Colors.RESET} {msg}")

def log_hipocampo(msg: str):
    print(f"{Colors.BRIGHT_GREEN}[HIPOCAMPO]{Colors.RESET} {msg}")

def log_neocortex(msg: str):
    print(f"{Colors.BRIGHT_MAGENTA}[NEOCÓRTEX]{Colors.RESET} {msg}")

def log_poda(msg: str):
    print(f"{Colors.BRIGHT_RED}[PODA SINÁPTICA]{Colors.RESET} {msg}")

def log_reforco(msg: str):
    print(f"{Colors.BRIGHT_GREEN}[REFORÇO SINÁPTICO]{Colors.RESET} {msg}")

def log_busca(msg: str):
    print(f"{Colors.BRIGHT_BLUE}[BUSCA ACADÊMICA/WEB]{Colors.RESET} {msg}")

def log_wal(msg: str):
    print(f"{Colors.BRIGHT_WHITE}[LOG WAL]{Colors.RESET} {msg}")

def log_success(msg: str):
    print(f"{Colors.BRIGHT_GREEN}✓ {msg}{Colors.RESET}")

def log_warning(msg: str):
    print(f"{Colors.BRIGHT_YELLOW}⚠️ {msg}{Colors.RESET}")

def log_error(msg: str):
    print(f"{Colors.BRIGHT_RED}❌ {msg}{Colors.RESET}")
