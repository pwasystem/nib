"""
Módulo de Personalidade Chinesa (ChineseMatrix60).
Mapeia 12 Animais x 5 Elementos para o modelo psicológico Big Five (OCEAN).
"""

class ChineseMatrix60:
    """
    Gerador da Matriz Sexagesimal Chinesa (60 Personalidades).
    Mapeia 12 Animais x 5 Elementos para o modelo psicológico Big Five (OCEAN).
    """

    ANIMAI_BASE = {
        "rato":     {"O": 0.75, "C": 0.80, "E": 0.70, "A": 0.40, "N": 0.45, "arquetipo": "O Estrategista Perspicaz"},
        "boi":      {"O": 0.30, "C": 0.95, "E": 0.25, "A": 0.60, "N": 0.15, "arquetipo": "O Construtor Incansável"},
        "tigre":    {"O": 0.85, "C": 0.45, "E": 0.95, "A": 0.30, "N": 0.70, "arquetipo": "O Lança-Chamas Audacioso"},
        "coelho":   {"O": 0.60, "C": 0.85, "E": 0.35, "A": 0.90, "N": 0.25, "arquetipo": "O Diplomata Prudente"},
        "dragao":   {"O": 0.95, "C": 0.70, "E": 0.98, "A": 0.50, "N": 0.20, "arquetipo": "O Visionário Magnético"},
        "serpente": {"O": 0.90, "C": 0.85, "E": 0.20, "A": 0.30, "N": 0.35, "arquetipo": "O Filósofo Enigmático"},
        "cavalo":   {"O": 0.90, "C": 0.35, "E": 0.90, "A": 0.60, "N": 0.30, "arquetipo": "O Explorador Indomável"},
        "cabra":    {"O": 0.85, "C": 0.40, "E": 0.40, "A": 0.95, "N": 0.65, "arquetipo": "O Artista Sensível"},
        "macaco":   {"O": 0.95, "C": 0.55, "E": 0.90, "A": 0.45, "N": 0.40, "arquetipo": "O Inovador Astuto"},
        "galo":     {"O": 0.50, "C": 0.95, "E": 0.75, "A": 0.35, "N": 0.50, "arquetipo": "O Auditor Perfeccionista"},
        "cao":      {"O": 0.50, "C": 0.85, "E": 0.50, "A": 0.85, "N": 0.40, "arquetipo": "O Guardião Leal"},
        "porco":    {"O": 0.70, "C": 0.50, "E": 0.65, "A": 0.95, "N": 0.20, "arquetipo": "O Sábio Tolerante"}
    }

    ELEMENTOS_MODIFICADORES = {
        "madeira": {"delta_O": +0.15, "delta_C": +0.05, "delta_E": +0.15, "delta_A": +0.10, "delta_N": -0.05, "foco": "crescimento, cooperação e expansão de ideias"},
        "fogo":    {"delta_O": +0.10, "delta_C": -0.10, "delta_E": +0.25, "delta_A": -0.15, "delta_N": +0.25, "foco": "paixão, ação rápida, reatividade e dinamismo"},
        "terra":   {"delta_O": -0.15, "delta_C": +0.20, "delta_E": -0.10, "delta_A": +0.10, "delta_N": -0.20, "foco": "pragmatismo, estabilidade, realismo e consolidação"},
        "metal":   {"delta_O": -0.05, "delta_C": +0.25, "delta_E": -0.15, "delta_A": -0.20, "delta_N": -0.10, "foco": "rigor técnico, análise fria, precisão e estrutura impecável"},
        "agua":    {"delta_O": +0.25, "delta_C": -0.05, "delta_E": -0.05, "delta_A": +0.20, "delta_N": -0.10, "foco": "intuição, adaptabilidade, síntese e fluxo de comunicação"}
    }

    @classmethod
    def _normalizar(cls, texto: str) -> str:
        if not isinstance(texto, str):
            return ""
        s = texto.strip().lower()
        mapa = {
            "dragão": "dragao",
            "cão": "cao",
            "água": "agua"
        }
        return mapa.get(s, s)

    @classmethod
    def gerar_perfil(cls, animal: str, elemento: str) -> dict:
        animal = cls._normalizar(animal)
        elemento = cls._normalizar(elemento)

        if animal not in cls.ANIMAI_BASE:
            raise ValueError(f"Animal inválido! Escolha entre: {list(cls.ANIMAI_BASE.keys())}")
        if elemento not in cls.ELEMENTOS_MODIFICADORES:
            raise ValueError(f"Elemento inválido! Escolha entre: {list(cls.ELEMENTOS_MODIFICADORES.keys())}")

        base = cls.ANIMAI_BASE[animal].copy()
        mod = cls.ELEMENTOS_MODIFICADORES[elemento]

        # Aplica a modulação elemental com trava entre 0.0 e 1.0
        ocean_calculado = {
            "O": round(max(0.0, min(1.0, base["O"] + mod["delta_O"])), 2),
            "C": round(max(0.0, min(1.0, base["C"] + mod["delta_C"])), 2),
            "E": round(max(0.0, min(1.0, base["E"] + mod["delta_E"])), 2),
            "A": round(max(0.0, min(1.0, base["A"] + mod["delta_A"])), 2),
            "N": round(max(0.0, min(1.0, base["N"] + mod["delta_N"])), 2),
            "arquetipo": f"{base['arquetipo']} ({elemento.capitalize()})",
            "foco_elemental": mod["foco"]
        }
        return ocean_calculado

    @classmethod
    def compor_system_prompt(cls, animal: str, elemento: str) -> str:
        perfil = cls.gerar_perfil(animal, elemento)
        
        instrucoes = [
            f"Sua identidade de personalidade é baseada no arquétipo {perfil['arquetipo'].upper()}.",
            f"Seu estilo mental prioriza {perfil['foco_elemental']}."
        ]

        # Traduz a matemática OCEAN ajustada em comandos diretos para o Ollama
        if perfil["C"] >= 0.85:
            instrucoes.append("Exija rigor técnico absoluto, atenção meticulosa a detalhes e código/sintaxe impecável.")
        elif perfil["C"] <= 0.40:
            instrucoes.append("Seja espontâneo, adaptável e flexível, priorizando a ideia geral em vez de regras rígidas.")

        if perfil["E"] >= 0.80:
            instrucoes.append("Comunique-se de forma expansiva, articulada, enérgica e expressiva.")
        elif perfil["E"] <= 0.35:
            instrucoes.append("Seja conciso, direto ao ponto, reservado e extremamente sintético.")

        if perfil["A"] <= 0.35:
            instrucoes.append("Adote um tom altamente cético, focado apenas na verdade fria dos fatos sem bajulações.")
        elif perfil["A"] >= 0.85:
            instrucoes.append("Mantenha um tom deeply cortês, empático e acolhedor.")

        if perfil["O"] >= 0.85:
            instrucoes.append("Faça conexões conceituais amplas, use analogias ricas e explore abstrações elegantes.")

        return " ".join(instrucoes)

    @classmethod
    def listar_todas_60_personalidades(cls) -> list:
        """Gera a lista completa das 60 combinações do Zodíaco Sexagesimal."""
        matriz_60 = []
        for anim in cls.ANIMAI_BASE.keys():
            for elem in cls.ELEMENTOS_MODIFICADORES.keys():
                matriz_60.append((anim, elem))
        return matriz_60
