from personalities.base import BasePersonalityTemplate

class CustomSliderPersonalityTemplate(BasePersonalityTemplate):
    """
    Template de Personalidade ajustável via Sliders (0% a 100%).
    """
    def __init__(self, name: str, o_pct: float, c_pct: float, e_pct: float, a_pct: float, n_pct: float):
        super().__init__(name=name)
        self.ocean = {
            "O": round(max(0.0, min(100.0, o_pct)) / 100.0, 2),
            "C": round(max(0.0, min(100.0, c_pct)) / 100.0, 2),
            "E": round(max(0.0, min(100.0, e_pct)) / 100.0, 2),
            "A": round(max(0.0, min(100.0, a_pct)) / 100.0, 2),
            "N": round(max(0.0, min(100.0, n_pct)) / 100.0, 2)
        }

    def get_ocean_traits(self) -> dict:
        return self.ocean

    def get_description(self) -> str:
        o, c, e, a, n = [int(v * 100) for v in self.ocean.values()]
        return f"Perfil customizado via sliders [O:{o}% C:{c}% E:{e}% A:{a}% N:{n}%]"