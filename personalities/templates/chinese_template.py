from personalities.base import BasePersonalityTemplate
from personalities.chinese_matrix import ChineseMatrix60

class ChineseMatrixTemplate(BasePersonalityTemplate):
    """
    Template de Personalidade baseado na Matriz Sexagesimal Chinesa (60 Combinações).
    Ajusta simultaneamente os traços Big Five (OCEAN) e o estado afetivo (PAD).
    """
    MODIFICADORES_PAD_ELEMENTAIS = {
        "fogo":    {"p": 0.20, "a": 0.50, "d": 0.30},
        "metal":   {"p": 0.10, "a": -0.30, "d": 0.50},
        "terra":   {"p": 0.30, "a": -0.40, "d": 0.30},
        "agua":    {"p": 0.50, "a": 0.00, "d": -0.10},
        "madeira": {"p": 0.50, "a": 0.30, "d": 0.20}
    }

    def __init__(self, animal: str = "dragao", elemento: str = "madeira"):
        self.animal_raw = animal
        self.elemento_raw = elemento
        self.perfil = ChineseMatrix60.gerar_perfil(animal, elemento)
        
        nome_formatado = f"Matriz Chinesa - {animal.capitalize()} de {elemento.capitalize()}"
        super().__init__(name=nome_formatado)
        
        elem_norm = ChineseMatrix60._normalizar(elemento)
        self.pad = self.MODIFICADORES_PAD_ELEMENTAIS.get(elem_norm, {"p": 0.3, "a": 0.1, "d": 0.2})

    def get_ocean_traits(self) -> dict:
        return {
            "O": self.perfil.get("O", 0.5),
            "C": self.perfil.get("C", 0.5),
            "E": self.perfil.get("E", 0.5),
            "A": self.perfil.get("A", 0.5),
            "N": self.perfil.get("N", 0.5)
        }

    def get_description(self) -> str:
        return f"{self.perfil.get('arquetipo', '')} | Foco: {self.perfil.get('foco_elemental', '')}"
