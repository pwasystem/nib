from abc import ABC, abstractmethod

class BasePersonalityTemplate(ABC):
    """
    Template base de personalidade do NIB.
    Padroniza a tradução do vetor Big Five (OCEAN) para o Córtex Pré-Frontal.
    """
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def get_ocean_traits(self) -> dict:
        """Deve retornar um dict: {'O': float, 'C': float, 'E': float, 'A': float, 'N': float}."""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Retorna a descrição legível do arquétipo."""
        pass

    def build_system_instruction(self) -> str:
        """Converte automaticamente os valores OCEAN em instruções para o Ollama."""
        ocean = self.get_ocean_traits()
        o, c, e, a, n = [int(ocean.get(k, 0.5) * 100) for k in ["O", "C", "E", "A", "N"]]
        instructions = [f"Seu perfil de personalidade é baseado em '{self.name}': {self.get_description()} (Traços Big Five: O:{o}%, C:{c}%, E:{e}%, A:{a}%, N:{n}%)."]

        # Conscienciosidade (C)
        if ocean.get("C", 0.5) >= 0.85:
            instructions.append("Exija extrema precisão técnica, estruturação lógica e atenção meticulosa a detalhes.")
        elif ocean.get("C", 0.5) <= 0.40:
            instructions.append("Seja flexível, espontâneo e priorize o conceito geral sobre regras engessadas.")

        # Extroversão (E)
        if ocean.get("E", 0.5) >= 0.80:
            instructions.append("Comunique-se de forma expansiva, articulada e detalhada.")
        elif ocean.get("E", 0.5) <= 0.35:
            instructions.append("Seja conciso, direto, focado e sintético nas palavras.")

        # Amabilidade (A)
        if ocean.get("A", 0.5) <= 0.35:
            instructions.append("Adote um tom altamente cético, focado na verdade fria dos fatos sem bajulações.")
        elif ocean.get("A", 0.5) >= 0.85:
            instructions.append("Mantenha um tom extremamente cortês, acolhedor e empático.")

        # Abertura (O)
        if ocean.get("O", 0.5) >= 0.85:
            instructions.append("Explore analogias ricas, abstrações e conexões conceituais amplas.")

        return " ".join(instructions)

    def get_pad_vectors(self) -> dict:
        """
        Retorna os vetores PAD (Prazer, Excitação, Dominância) de -1.0 a +1.0
        correspondentes a este template de personalidade.
        """
        if hasattr(self, "pad") and isinstance(self.pad, dict):
            return self.pad
            
        ocean = self.get_ocean_traits()
        o = ocean.get("O", 0.5)
        c = ocean.get("C", 0.5)
        e = ocean.get("E", 0.5)
        a = ocean.get("A", 0.5)
        n = ocean.get("N", 0.5)
        
        p = round(max(-1.0, min(1.0, (a * 0.6 + o * 0.4 - n * 0.5))), 2)
        ar = round(max(-1.0, min(1.0, (e * 0.7 + n * 0.3 - c * 0.3))), 2)
        d = round(max(-1.0, min(1.0, (c * 0.6 + e * 0.4 - a * 0.3))), 2)
        
        return {"p": p, "a": ar, "d": d}