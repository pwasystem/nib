from collections import deque
import threading

class WorkingMemory:
    """
    Memória de Trabalho (Working Memory / Córtex Pré-Frontal).
    Mantém uma janela deslizante circular das últimas N interações da conversa ativa.
    """
    def __init__(self, capacity: int = 6):
        self.capacity = capacity
        self.buffer = deque(maxlen=capacity)
        self._lock = threading.Lock()

    def add_interaction(self, user_prompt: str, nib_response: str):
        """Adiciona uma nova interação (turno) à memória de trabalho."""
        if not user_prompt or not nib_response:
            return
        with self._lock:
            self.buffer.append({
                "user": user_prompt.strip(),
                "nib": nib_response.strip()
            })

    def get_context_str(self) -> str:
        """Formata as interações recentes para injeção direta no prompt do LLM."""
        with self._lock:
            if not self.buffer:
                return "Nenhuma interação recente na conversa atual."
            
            linhas = []
            for i, turno in enumerate(self.buffer, 1):
                linhas.append(f"Usuário ({i}): {turno['user']}")
                linhas.append(f"NIB ({i}): {turno['nib']}")
            return "\n".join(linhas)

    def clear(self):
        """Limpa o buffer de curto prazo da sessão atual."""
        with self._lock:
            self.buffer.clear()

    def to_list(self) -> list:
        """Retorna uma cópia em lista do histórico recente."""
        with self._lock:
            return list(self.buffer)
