import urllib.parse
import random
import requests
from bs4 import BeautifulSoup
import logger_nib as logger

class CuriosityCore:
    """
    Módulo de Curiosidade e Criatividade para Aprendizado Autônomo do NIB.
    Varre o Neocórtex e o Hipocampo para identificar conceitos de interesse
    e memórias passadas, formulando hipóteses e pesquisas criativas autônomas.
    """
    def __init__(self, brain_instance):
        self.brain = brain_instance
        self.interesses_padrao = [
            "inteligência artificial neuro-simbólica",
            "redes neurais biológicas e plasticidade sináptica",
            "computação quântica e algoritmos cognitivos",
            "filosofia da mente e consciência artificial",
            "biomimética e sistemas adaptativos"
        ]

    def pesquisar_web(self, termo: str) -> str:
        """Executa busca HTML leve para preencher a lacuna encontrada."""
        logger.log_pesquisa_web(f"Pesquisando na web por: '{termo}'...")
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

    def obter_tema_interesse_ou_memoria(self) -> tuple[str, str]:
        """
        Extrai um tema baseado na memória existente (Neocórtex / Hipocampo)
        ou seleciona um assunto de interesse espontâneo.
        Retorna (tema, origem)
        """
        # 1. Tentar utilizar os interesses característicos da personalidade ativa
        try:
            if hasattr(self.brain, "active_personality") and self.brain.active_personality:
                if hasattr(self.brain.active_personality, "get_interests"):
                    interesses_persona = self.brain.active_personality.get_interests()
                    if interesses_persona and random.random() < 0.6:
                        tema_persona = random.choice(interesses_persona)
                        return tema_persona, f"interesses ({self.brain.active_personality.name})"
        except Exception:
            pass

        # 2. Tentar selecionar nós no Neocórtex
        try:
            nos = list(self.brain.neocortex.nodes())
            if nos:
                no_escolhido = random.choice(nos)
                vizinhos = list(self.brain.neocortex.neighbors(no_escolhido))
                if vizinhos:
                    vizinho = random.choice(vizinhos)
                    return f"{no_escolhido} e {vizinho}", "neocortex"
                return no_escolhido, "neocortex"
        except Exception:
            pass

        # 3. Tentar resgatar memórias episódicas do Hipocampo
        try:
            memorias = self.brain.hipocampo.get(limit=5, include=["documents"])
            if memorias and memorias.get("documents"):
                doc = random.choice(memorias["documents"])
                palavras = [p for p in doc.split() if len(p) > 4 and p.isalpha()]
                if palavras:
                    return random.choice(palavras), "hipocampo"
        except Exception:
            pass

        # 4. Fallback: interesses espontâneos padrão
        return random.choice(self.interesses_padrao), "interesse_espontaneo"

    def pesquisa_criativa(self) -> dict:
        """
        Função de Criatividade ativada no Aprendizado Autônomo.
        Formula uma pesquisa criativa a partir de tópicos na memória
        ou interesses espontâneos, busca conhecimento e consolida a descoberta.
        """
        if not self.brain.learning_enabled:
            return None

        tema, origem = self.obter_tema_interesse_ou_memoria()
        logger.log_criatividade(f"Módulo de Criatividade ativado! Origem: [{origem.upper()}] | Tema selecionado: '{tema}'")

        # Tenta utilizar o Ollama para formular uma busca criativa
        termo_pesquisa = f"avanços recentes sobre {tema}"
        try:
            sys_p = "Você é o módulo de criatividade do NIB. Gere APENAS um termo de busca curto e fascinante para pesquisar sobre o tema fornecido. Responda APENAS o termo de busca sem explicações."
            resp = requests.post(self.brain.ollama_url, json={
                "model": self.brain.model_name,
                "prompt": f"Tema de interesse: {tema}",
                "system": sys_p,
                "stream": False
            }, timeout=4).json().get("response", "").strip()

            if resp and len(resp) < 100:
                termo_pesquisa = resp.replace('"', '').replace("'", "")
        except Exception:
            pass

        logger.log_criatividade(f"Pesquisa autônoma criativa em andamento para o termo: '{termo_pesquisa}'...")
        descoberta = self.brain.pesquisar_conhecimento_externo(termo_pesquisa)

        if descoberta and "Nenhuma informação" not in descoberta:
            fato = f"Aprendizado criativo autônomo sobre '{tema}' ({origem}): {descoberta}"
            self.brain.memorizar_experiencia(fato)
            logger.log_criatividade(f"💡 Nova descoberta criativa memorizada: '{fato[:120]}...'")
            return {
                "tipo": "criatividade",
                "tema": tema,
                "origem": origem,
                "termo_pesquisa": termo_pesquisa,
                "descoberta": descoberta
            }

        logger.log_criatividade(f"Pesquisa criativa sobre '{tema}' finalizada sem novos achados.")
        return None

    def investigar_lacunas(self) -> dict:
        """
        Identifica nós no Neocórtex com grau <= 2 (pouco conectados),
        pesquisa sobre eles e memoriza o aprendizado no Hipocampo.
        Se não houver lacunas simples, executa a pesquisa de criatividade.
        """
        if not self.brain.learning_enabled:
            return None

        lacunas = []
        try:
            for no in self.brain.neocortex.nodes():
                if self.brain.neocortex.degree(no) <= 2 and len(no) > 3:
                    lacunas.append(no)
        except Exception:
            pass

        if lacunas:
            conceito_orfa = lacunas[0]
            logger.log_criatividade(f"Lacuna conceitual identificada no Neocórtex: '{conceito_orfa}'")
            conteudo_descoberto = self.pesquisar_web(f"o que e {conceito_orfa}")

            if conteudo_descoberto:
                fato = f"Aprendizado autônomo sobre '{conceito_orfa}': {conteudo_descoberto}"
                self.brain.memorizar_experiencia(fato)
                logger.log_criatividade(f"💡 Lacuna preenchida e memorizada: '{conceito_orfa}'")
                return {
                    "tipo": "lacuna",
                    "conceito": conceito_orfa,
                    "descoberta": conteudo_descoberto
                }

        # Se não houver lacunas diretas, executa pesquisa criativa baseada em interesses/memória
        return self.pesquisa_criativa()