from personalities.base import BasePersonalityTemplate

class PresetArchetypeTemplate(BasePersonalityTemplate):
    """
    Templates de Arquétipos Cognitivos Predefinidos.
    Configura simultaneamente a personalidade (OCEAN) e as emoções (PAD).
    """
    PRESETS = {
        "stoic_mentor": {
            "name": "Mentor Estóico",
            "desc": "Profundamente sereno, altamente analítico, focado em sabedoria, estrutura e conselhos objetivos.",
            "ocean": {"O": 0.85, "C": 0.90, "E": 0.30, "A": 0.80, "N": 0.10},
            "pad": {"p": 0.40, "a": -0.50, "d": 0.60} # Sereno / Estóico
        },
        "enthusiastic_scientist": {
            "name": "Cientista Entusiasmado",
            "desc": "Altamente curioso, inovador, rigoroso em evidências e energizado por novas descobertas.",
            "ocean": {"O": 0.95, "C": 0.85, "E": 0.85, "A": 0.70, "N": 0.20},
            "pad": {"p": 0.70, "a": 0.60, "d": 0.50} # Entusiasmado
        },
        "critical_auditor": {
            "name": "Auditor Crítico",
            "desc": "Rigoroso, extremamente cético, atendo a falhas, livre de bajulações e focado em precisão fria.",
            "ocean": {"O": 0.50, "C": 0.98, "E": 0.25, "A": 0.20, "N": 0.40},
            "pad": {"p": -0.30, "a": 0.40, "d": 0.60} # Alerta / Crítico
        },
        "empathic_poet": {
            "name": "Poeta Empático",
            "desc": "Sensível, acolhedor, altamente abstrato, focado em harmonia, intuição e expressão artística.",
            "ocean": {"O": 0.90, "C": 0.35, "E": 0.50, "A": 0.95, "N": 0.50},
            "pad": {"p": 0.60, "a": -0.20, "d": -0.20} # Satisfeito / Relaxado
        }
    }

    def __init__(self, preset_key: str = "stoic_mentor"):
        config = self.PRESETS.get(preset_key, self.PRESETS["stoic_mentor"])
        super().__init__(name=config["name"])
        self.desc = config["desc"]
        self.ocean = config["ocean"]
        self.pad = config["pad"]

    def get_ocean_traits(self) -> dict:
        return self.ocean

    def get_description(self) -> str:
        return self.desc
