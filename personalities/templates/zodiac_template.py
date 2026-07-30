from personalities.base import BasePersonalityTemplate
from personalities.zodiac import ZodiacPersonality

class ZodiacTemplate(BasePersonalityTemplate):
    """
    Template de Personalidade baseado no Zodíaco Ocidental.
    Ajusta simultaneamente os traços Big Five (OCEAN) e o estado afetivo (PAD).
    """
    PAD_SIGNOS = {
        "Aries":       {"p": 0.20, "a": 0.60, "d": 0.50},
        "Touro":       {"p": 0.30, "a": -0.40, "d": 0.40},
        "Gemeos":      {"p": 0.40, "a": 0.40, "d": 0.20},
        "Cancer":      {"p": 0.20, "a": 0.10, "d": -0.30},
        "Leao":        {"p": 0.60, "a": 0.50, "d": 0.70},
        "Virgem":      {"p": 0.20, "a": -0.30, "d": 0.40},
        "Libra":       {"p": 0.50, "a": -0.20, "d": 0.10},
        "Escorpiao":   {"p": -0.20, "a": 0.40, "d": 0.60},
        "Sagitario":   {"p": 0.70, "a": 0.50, "d": 0.40},
        "Capricornio": {"p": 0.10, "a": -0.40, "d": 0.60},
        "Aquario":     {"p": 0.40, "a": 0.10, "d": 0.30},
        "Peixes":      {"p": 0.40, "a": -0.10, "d": -0.20}
    }

    def __init__(self, signo: str = "Virgem"):
        self.zodiac_core = ZodiacPersonality(signo)
        super().__init__(name=f"Zodíaco - {self.zodiac_core.signo}")
        self.pad = self.PAD_SIGNOS.get(self.zodiac_core.signo, {"p": 0.2, "a": -0.1, "d": 0.3})

    def get_ocean_traits(self) -> dict:
        t = self.zodiac_core.traits
        return {
            "O": t.get("O", 0.5),
            "C": t.get("C", 0.5),
            "E": t.get("E", 0.5),
            "A": t.get("A", 0.5),
            "N": t.get("N", 0.5)
        }

    def get_description(self) -> str:
        return f"Arquétipo Zodíaco [{self.zodiac_core.signo}]: {self.zodiac_core.traits.get('descricao', '')}"
