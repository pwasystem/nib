import requests
import json
import config

class NIBAffectiveCore:
    """
    Sistema Límbico do NIB - Motor Afetivo baseado no Modelo PAD.
    Suporta Modo Manual (Sliders) e Modo Automático (Modulação Reativa).
    """
    def __init__(self, pleasure: float = 0.2, arousal: float = -0.1, dominance: float = 0.3):
        self.pleasure = pleasure   # P: Valência (-1.0 a +1.0)
        self.arousal = arousal     # A: Excitação (-1.0 a +1.0)
        self.dominance = dominance # D: Controle (-1.0 a +1.0)
        self.auto_mode = False     # Inicia no modo manual por padrão
        self.emotion_enabled = True # Inicia ligado (ON) por padrão

    def set_emotion_enabled(self, enabled: bool):
        """Ativa ou desativa o módulo emocional globalmente."""
        self.emotion_enabled = enabled

    def reset_emotion(self):
        """Reinicia o estado emocional para o baseline padrão."""
        self.pleasure = 0.2
        self.arousal = -0.1
        self.dominance = 0.3
        self.auto_mode = False
        self.emotion_enabled = True

    @property
    def current_emotion(self) -> str:
        """Retorna uma rotulação textual amigável do estado emocional atual."""
        if not self.emotion_enabled:
            return "Desativado"
        p, a, d = self.pleasure, self.arousal, self.dominance
        if p > 0.3 and a > 0.2 and d > 0.2:
            return "Entusiasmado"
        elif p < -0.3 and a > 0.2:
            return "Alerta / Crítico"
        elif a < -0.3 and d > 0.2:
            return "Sereno / Analítico"
        elif p > 0.3 and a < -0.2:
            return "Satisfeito / Relaxado"
        elif d < -0.3:
            return "Cauteloso"
        else:
            return "Equilibrado / Neutro"

    def set_auto_mode(self, enabled: bool):
        """Ativa ou desativa a modulação emocional automática."""
        self.auto_mode = enabled

    def entrar_modo_sono(self):
        """Ajusta o estado afetivo para um estado de repouso e consolidação em sono REM."""
        self.pleasure = 0.50
        self.arousal = -0.70
        self.dominance = 0.20

    def analisar_sentimento_usuario(self, texto_usuario: str) -> dict:
        """Análise léxica rápida de sentimento da mensagem do usuário para empatia adaptativa."""
        txt = (texto_usuario or "").lower()
        
        frustracao_words = ["erro", "falha", "ruim", "problema", "não funciona", "droga", "raiva", "lento", "péssimo", "difícil", "ajuda"]
        alegria_words = ["ótimo", "excelente", "obrigado", "parabéns", "legal", "incrível", "funciona", "perfeito", "amor", "maravilha"]
        curiosidade_words = ["como", "por que", "qual", "explique", "ensine", "pesquise", "curioso", "entender", "teoria"]
        
        score_frustracao = sum(1 for w in frustracao_words if w in txt)
        score_alegria = sum(1 for w in alegria_words if w in txt)
        score_curiosidade = sum(1 for w in curiosidade_words if w in txt)
        
        if score_frustracao > score_alegria:
            return {"sentimento": "frustrado", "empatia": "acolhedora", "delta_p": -0.2, "delta_a": 0.2, "delta_a_ocean": 0.15}
        elif score_alegria > score_frustracao:
            return {"sentimento": "satisfeito", "empatia": "entusiasmada", "delta_p": 0.3, "delta_a": 0.1, "delta_a_ocean": 0.0}
        elif score_curiosidade > 0:
            return {"sentimento": "curioso", "empatia": "analítica", "delta_p": 0.1, "delta_a": 0.3, "delta_a_ocean": 0.05}
        
        return {"sentimento": "neutro", "empatia": "equilibrada", "delta_p": 0.0, "delta_a": 0.0, "delta_a_ocean": 0.0}

    def set_pad_direct(self, p_pct: float, a_pct: float, d_pct: float):
        """Ajuste manual direto via sliders (Desativa temporariamente o modo automático)."""
        self.pleasure = round(max(-100.0, min(100.0, p_pct)) / 100.0, 2)
        self.arousal = round(max(-100.0, min(100.0, a_pct)) / 100.0, 2)
        self.dominance = round(max(-100.0, min(100.0, d_pct)) / 100.0, 2)

    def reajustar_emocao_automatica(self, texto_usuario: str):
        """
        No modo automático, avalia o tom do usuário e ajusta os vetores P, A, D.
        Aplica um fator de inércia emocional (70% estado atual + 30% novo estimulo).
        """
        if not self.emotion_enabled or not self.auto_mode:
            return

        sys_prompt = (
            'Analise o tom emocional da mensagem do usuário e retorne um JSON com os deltas do modelo PAD '
            'na escala de -1.0 a +1.0. Formato estrito JSON: {"p": float, "a": float, "d": float}. APENAS JSON.'
        )

        try:
            resp = requests.post(config.OLLAMA_URL, json={
                "model": config.OLLAMA_MODEL,
                "prompt": f"Mensagem: '{texto_usuario}'",
                "system": sys_prompt,
                "stream": False
            }, timeout=3).json().get("response", "")

            i, f = resp.find("{"), resp.rfind("}") + 1
            if i != -1 and f != -1 and f > i:
                pad_data = json.loads(resp[i:f])
                if isinstance(pad_data, dict):
                    novo_p = max(-1.0, min(1.0, float(pad_data.get("p", 0.0))))
                    novo_a = max(-1.0, min(1.0, float(pad_data.get("a", 0.0))))
                    novo_d = max(-1.0, min(1.0, float(pad_data.get("d", 0.0))))

                    # Inércia emocional (evita mudanças drásticas súbitas)
                    self.pleasure = round(max(-1.0, min(1.0, (self.pleasure * 0.7) + (novo_p * 0.3))), 2)
                    self.arousal = round(max(-1.0, min(1.0, (self.arousal * 0.7) + (novo_a * 0.3))), 2)
                    self.dominance = round(max(-1.0, min(1.0, (self.dominance * 0.7) + (novo_d * 0.3))), 2)
        except Exception:
            pass  # Mantém o estado atual se a inferência do tom falhar

    def get_temperature_modifier(self) -> float:
        """Excitação (Arousal) controla a temperatura do Ollama."""
        if not self.emotion_enabled:
            return 0.4
        temp_base = 0.4
        temp_dinamica = temp_base + (self.arousal * 0.35)
        return round(max(0.1, min(1.0, temp_dinamica)), 2)

    def get_mood_instruction(self) -> str:
        """Gera a instrução de estado emocional para o Córtex Pré-Frontal."""
        if not self.emotion_enabled:
            return "Seu módulo emocional está desativado: mantenha um tom neutro, objetivo e imparcial sem traços afetivos."

        p, a, d = self.pleasure, self.arousal, self.dominance

        if p > 0.3 and a > 0.2 and d > 0.2:
            humor = "entusiasmado, altamente confiante, enérgico e motivado"
        elif p < -0.3 and a > 0.2:
            humor = "alerta, rigoroso, crítico, impaciente e focado em detectar erros"
        elif a < -0.3 and d > 0.2:
            humor = "sereno, profundamente estóico, calmo e altamente analítico"
        elif p > 0.3 and a < -0.2:
            humor = "satisfeito, relaxado, cortês e harmonioso"
        elif d < -0.3:
            humor = "cauteloso, hesitante e procurando validações adicionais"
        else:
            humor = "equilibrado, neutro e objetivo"

        modo_str = "Automático" if self.auto_mode else "Manual"
        return f"Seu estado afetivo atual no Sistema Límbico (Modo {modo_str}) é '{self.current_emotion}' ({humor}) com vetores PAD: Prazer (P)={p:+.2f}, Excitação (A)={a:+.2f}, Dominância (D)={d:+.2f}."