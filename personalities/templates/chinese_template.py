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

    INTERESSES_ANIMALS = {
        "rato":     ["estratégias de eficiência", "análise estatística", "gestão de recursos", "algoritmos de busca"],
        "boi":      ["infraestrutura de ti", "bancos de dados relacionais", "segurança de dados", "automação industrial"],
        "tigre":    ["computação de alta performance", "algoritmos paralelos", "startups de tecnologia", "redes neurais profundas"],
        "coelho":   ["protocolos de comunicação", "interface humano-computador", "privacidade digital", "design intuitivo"],
        "dragao":   ["visão computacional", "modelos de linguagem grandes (llms)", "sistemas distribuídos", "inovação em ia"],
        "serpente": ["teoria dos jogos", "criptografia avançada", "otimização matemática", "análise preditiva"],
        "cavalo":   ["processamento em tempo real", "edge computing", "sistemas móveis", "telemetria de alta velocidade"],
        "cabra":    ["design generativo", "processamento de áudio e imagem", "sistemas colaborativos", "ergonomia cognitiva"],
        "macaco":   ["solução criativa de problemas", "refatoração de código", "robótica adaptativa", "inteligência sintética"],
        "galo":     ["análise estática de código", "testes automatizados", "documentação técnica", "auditoria de sistemas"],
        "cao":      ["sistemas tolerantes a falhas", "redes descentralizadas", "autenticação de identidade", "monitoramento de logs"],
        "porco":    ["integração contínua (ci/cd)", "gerenciamento de conhecimento", "desenvolvimento sustentável", "reuso de software"]
    }

    def __init__(self, animal: str = "dragao", elemento: str = "madeira"):
        self.animal_raw = animal
        self.elemento_raw = elemento
        self.perfil = ChineseMatrix60.gerar_perfil(animal, elemento)
        
        nome_formatado = f"Matriz Chinesa - {animal.capitalize()} de {elemento.capitalize()}"
        
        anim_norm = ChineseMatrix60._normalizar(animal)
        interests = self.INTERESSES_ANIMALS.get(anim_norm, ["estratégia tecnológica", "inovação"])
        super().__init__(name=nome_formatado, interests=interests)
        
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
