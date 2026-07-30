import os
import json
import config
from personalities.base import BasePersonalityTemplate

CUSTOM_PERSONALITIES_FILE = os.path.join(config.STORAGE_DIR, "custom_personalities.json")

class CustomPersonalityTemplate(BasePersonalityTemplate):
    """
    Template de Personalidade Customizado pelo Usuário.
    Suporta personalização completa de OCEAN, PAD, descrição e interesses característicos.
    """
    def __init__(self, template_id: str, name: str, description: str, ocean: dict, pad: dict, interests: list = None):
        super().__init__(name=name, interests=interests or ["desenvolvimento de software", "inteligência artificial"])
        self.template_id = template_id
        self.description = description
        self.ocean = {
            "O": round(max(0.0, min(1.0, float(ocean.get("O", 0.8)))), 2),
            "C": round(max(0.0, min(1.0, float(ocean.get("C", 0.9)))), 2),
            "E": round(max(0.0, min(1.0, float(ocean.get("E", 0.4)))), 2),
            "A": round(max(0.0, min(1.0, float(ocean.get("A", 0.7)))), 2),
            "N": round(max(0.0, min(1.0, float(ocean.get("N", 0.2)))), 2),
        }
        self.pad = {
            "p": round(max(-1.0, min(1.0, float(pad.get("p", 0.2)))), 2),
            "a": round(max(-1.0, min(1.0, float(pad.get("a", -0.1)))), 2),
            "d": round(max(-1.0, min(1.0, float(pad.get("d", 0.3)))), 2),
        }

    def get_ocean_traits(self) -> dict:
        return self.ocean

    def get_description(self) -> str:
        return self.description or f"Perfil customizado [{self.name}]"

    def get_pad_vectors(self) -> dict:
        return self.pad


class CustomPersonalityStore:
    """
    Gerenciador de armazenamento e persistência de templates customizados.
    """
    @staticmethod
    def load_all() -> dict:
        if not os.path.exists(CUSTOM_PERSONALITIES_FILE):
            return {}
        try:
            with open(CUSTOM_PERSONALITIES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    @staticmethod
    def save(template_data: dict) -> dict:
        t_id = template_data.get("id") or template_data.get("name", "custom").lower().replace(" ", "_")
        store = CustomPersonalityStore.load_all()
        
        entry = {
            "id": t_id,
            "name": template_data.get("name", "Personalidade Customizada"),
            "description": template_data.get("description", "Perfil personalizado pelo usuário"),
            "ocean": {
                "O": float(template_data.get("ocean", {}).get("O", template_data.get("o", 80)) / (100.0 if template_data.get("o", 80) > 1 else 1.0)),
                "C": float(template_data.get("ocean", {}).get("C", template_data.get("c", 90)) / (100.0 if template_data.get("c", 90) > 1 else 1.0)),
                "E": float(template_data.get("ocean", {}).get("E", template_data.get("e", 40)) / (100.0 if template_data.get("e", 40) > 1 else 1.0)),
                "A": float(template_data.get("ocean", {}).get("A", template_data.get("a", 70)) / (100.0 if template_data.get("a", 70) > 1 else 1.0)),
                "N": float(template_data.get("ocean", {}).get("N", template_data.get("n", 20)) / (100.0 if template_data.get("n", 20) > 1 else 1.0))
            },
            "pad": {
                "p": float(template_data.get("pad", {}).get("p", template_data.get("p", 20)) / (100.0 if abs(template_data.get("p", 20)) > 1 else 1.0)),
                "a": float(template_data.get("pad", {}).get("a", template_data.get("a", -10)) / (100.0 if abs(template_data.get("a", -10)) > 1 else 1.0)),
                "d": float(template_data.get("pad", {}).get("d", template_data.get("d", 30)) / (100.0 if abs(template_data.get("d", 30)) > 1 else 1.0))
            },
            "interests": template_data.get("interests") or ["desenvolvimento de software", "ia autônoma"]
        }
        
        store[t_id] = entry
        os.makedirs(os.path.dirname(CUSTOM_PERSONALITIES_FILE), exist_ok=True)
        with open(CUSTOM_PERSONALITIES_FILE, "w", encoding="utf-8") as f:
            json.dump(store, f, ensure_ascii=False, indent=2)
            
        return entry

    @staticmethod
    def delete(template_id: str) -> bool:
        store = CustomPersonalityStore.load_all()
        if template_id in store:
            del store[template_id]
            with open(CUSTOM_PERSONALITIES_FILE, "w", encoding="utf-8") as f:
                json.dump(store, f, ensure_ascii=False, indent=2)
            return True
        return False
