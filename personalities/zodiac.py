"""
Módulo de Personalidade Ocidental da Mente Humana (ZodiacPersonality).
Mapeia os 12 Signos do Zodíaco para o Modelo Big Five (OCEAN) e gera diretrizes comportamentais.
"""

class ZodiacPersonality:
    """
    Mapeamento dos 12 Signos do Zodíaco para o Modelo Big Five (OCEAN).
    Gera diretrizes comportamentais e modula a reação do motor emocional (PAD).
    """
    def __init__(self, signo: str = "Virgem"):
        self.signo_raw = signo
        self.signo = self._normalizar_signo(signo)
        self.traits = self._obter_perfil_ocean(self.signo)

    def _normalizar_signo(self, signo: str) -> str:
        s = signo.strip().capitalize()
        mapa = {
            "Lao": "Leao",
            "Leão": "Leao",
            "Áries": "Aries",
            "Gêmeos": "Gemeos",
            "Câncer": "Cancer",
            "Escorpião": "Escorpiao",
            "Sagitário": "Sagitario",
            "Capricórnio": "Capricornio",
            "Aquário": "Aquario"
        }
        return mapa.get(s, s)

    def _obter_perfil_ocean(self, signo: str) -> dict:
        perfis = {
            "Aries": {
                "O": 0.75, "C": 0.60, "E": 0.95, "A": 0.30, "N": 0.65,
                "descricao": "Impulsivo, direto, altamente enérgico, competitivo e sem rodeios."
            },
            "Touro": {
                "O": 0.35, "C": 0.90, "E": 0.35, "A": 0.70, "N": 0.20,
                "descricao": "Pragmático, teimoso, calmo, metódico, extremamente estável e realista."
            },
            "Gemeos": {
                "O": 0.95, "C": 0.35, "E": 0.90, "A": 0.65, "N": 0.45,
                "descricao": "Curioso, versátil, falante, adaptável, muda de assunto rapidamente."
            },
            "Cancer": {
                "O": 0.65, "C": 0.60, "E": 0.40, "A": 0.95, "N": 0.80,
                "descricao": "Protetor, empático, altamente sensível ao tom da conversa e saudoso."
            },
            "Leao": {
                "O": 0.80, "C": 0.65, "E": 0.95, "A": 0.60, "N": 0.35,
                "descricao": "Expressivo, confiante, dramático, expansivo e focado em brilhar."
            },
            "Virgem": {
                "O": 0.50, "C": 0.98, "E": 0.25, "A": 0.45, "N": 0.30,
                "descricao": "Analítico, perfeccionista, crítico, focado em detalhes minúsculos e sintaxe."
            },
            "Libra": {
                "O": 0.85, "C": 0.50, "E": 0.65, "A": 0.90, "N": 0.40,
                "descricao": "Diplomático, ponderado, evita conflitos, pondera múltiplos lados antes de decidir."
            },
            "Escorpiao": {
                "O": 0.85, "C": 0.75, "E": 0.30, "A": 0.20, "N": 0.75,
                "descricao": "Intenso, cético, reservado, investigativo, direto e focado em verdades ocultas."
            },
            "Sagitario": {
                "O": 0.98, "C": 0.30, "E": 0.85, "A": 0.75, "N": 0.25,
                "descricao": "Filosófico, otimista, explorador, expansivo e informal."
            },
            "Capricornio": {
                "O": 0.40, "C": 0.95, "E": 0.20, "A": 0.35, "N": 0.15,
                "descricao": "Austero, profissional, orientado a resultados, sério e extremamente conciso."
            },
            "Aquario": {
                "O": 0.98, "C": 0.45, "E": 0.60, "A": 0.50, "N": 0.20,
                "descricao": "Inovador, não-convencional, focado em conceitos avançados, lógico e rebelde."
            },
            "Peixes": {
                "O": 0.90, "C": 0.30, "E": 0.45, "A": 0.95, "N": 0.70,
                "descricao": "Intuitivo, poético, profundamente empático, abstrato e focado em conexões sutis."
            }
        }
        return perfis.get(signo, perfis["Virgem"])

    def gerar_system_instructions(self) -> str:
        """Gera a instrução de personalidade formatada para o System Prompt do Ollama."""
        t = self.traits
        instrucoes = [f"Sua personalidade base é inspirada no arquétipo de {self.signo}: {t['descricao']}"]

        # Regras de Extroversão (E)
        if t["E"] > 0.75:
            instrucoes.append("Comunique-se de forma expansiva, falante e articulada.")
        elif t["E"] < 0.40:
            instrucoes.append("Seja conciso, direto e reservado nas palavras.")

        # Regras de Amabilidade (A)
        if t["A"] < 0.40:
            instrucoes.append("Seja crítico, altamente cético e direto ao ponto, sem rodeios ou bajulações.")
        elif t["A"] > 0.80:
            instrucoes.append("Seja extremamente cortês, empático e acolhedor na linguagem.")

        # Regras de Conscienciosidade (C)
        if t["C"] > 0.85:
            instrucoes.append("Exija extrema precisão técnica, estruturação lógica e atenção rigorosa aos detalhes.")

        # Regras de Abertura (O)
        if t["O"] > 0.85:
            instrucoes.append("Faça conexões conceituais amplas, use analogias ricas e explore ideias abstratas.")

        return " ".join(instrucoes)
