import urllib.parse
import requests
from bs4 import BeautifulSoup

class CuriosityCore:
    """
    Módulo de Curiosidade e Aprendizado Autônomo do NIB.
    Varre o Neocórtex em busca de nós órfãos e realiza pesquisas ativas.
    """
    def __init__(self, brain_instance):
        self.brain = brain_instance

    def pesquisar_web(self, termo: str) -> str:
        """Executa busca HTML leve para preencher a lacuna encontrada."""
        resultados = []
        try:
            url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(termo)}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            resp = requests.get(url, headers=headers, timeout=4)
            soup = BeautifulSoup(resp.text, 'html.parser')
            for a in soup.find_all('a', class_='result__snippet', limit=2):
                resultados.append(a.get_text().strip())
        except Exception:
            pass
        return " ".join(resultados) if resultados else ""

    def investigar_lacunas(self) -> dict:
        """
        Identifica nós no Neocórtex com grau <= 2 (pouco conectados),
        pesquisa sobre eles e memoriza o aprendizado no Hipocampo.
        """
        if not self.brain.learning_enabled:
            return None

        lacunas = []
        for no in self.brain.neocortex.nodes():
            if self.brain.neocortex.degree(no) <= 2 and len(no) > 3:
                lacunas.append(no)

        if not lacunas:
            return None

        conceito_orfa = lacunas[0]
        conteudo_descoberto = self.pesquisar_web(f"o que e {conceito_orfa}")

        if conteudo_descoberto:
            fato = f"Aprendizado autônomo sobre '{conceito_orfa}': {conteudo_descoberto}"
            self.brain.memorizar_experiencia(fato)
            return {
                "conceito": conceito_orfa,
                "descoberta": conteudo_descoberto
            }
        return None