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
        self.learning_goals = []  # Lista de metas: [{"id": "...", "topico": "...", "concluida": False}]
        self.ultimas_descobertas = [] # Registro recente de descobertas autônomas
        self.topicos_pesquisados_recentes = [] # Histórico deslizante para evitar repetição do mesmo assunto
        self.interesses_padrao = [
            "inteligência artificial neuro-simbólica",
            "redes neurais biológicas e plasticidade sináptica",
            "computação quântica e algoritmos cognitivos",
            "filosofia da mente e consciência artificial",
            "biomimética e sistemas adaptativos",
            "astrofísica e cosmologia computacional",
            "psicologia cognitiva e tomada de decisão",
            "neurociência computacional e memória"
        ]

    def _registrar_topico_pesquisado(self, topico: str):
        """Registra um tópico recém-pesquisado para evitar re-estudar o mesmo assunto repetidamente."""
        t_clean = topico.strip().lower()
        if t_clean and t_clean not in [x.lower() for x in self.topicos_pesquisados_recentes]:
            self.topicos_pesquisados_recentes.append(t_clean)
            if len(self.topicos_pesquisados_recentes) > 25:
                self.topicos_pesquisados_recentes.pop(0)

    def obter_ultimas_descobertas(self, limit: int = 5) -> list:
        """Retorna a lista de descobertas autônomas mais recentes."""
        return self.ultimas_descobertas[-limit:]

    def adicionar_meta_aprendizado(self, topico: str) -> dict:
        """Adiciona uma nova meta de aprendizado autônomo definida pelo usuário."""
        topico_clean = topico.strip()
        if not topico_clean:
            return None
        meta_id = f"goal_{len(self.learning_goals) + 1}_{random.randint(1000, 9999)}"
        meta = {"id": meta_id, "topico": topico_clean, "concluida": False, "descobertas": []}
        self.learning_goals.append(meta)
        logger.log_criatividade(f"🎯 Nova meta de aprendizado autônomo cadastrada: '{topico_clean}'")
        return meta

    def listar_metas_aprendizado(self) -> list:
        return self.learning_goals

    def remover_meta_aprendizado(self, meta_id: str) -> bool:
        antes = len(self.learning_goals)
        self.learning_goals = [g for g in self.learning_goals if g["id"] != meta_id]
        return len(self.learning_goals) < antes

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
        Extrai um tema baseado nas metas de aprendizado ativas, interesses da personalidade
        ou nós da memória, diversificando os assuntos de acordo com o perfil do NIB.
        Retorna (tema, origem)
        """
        # 0. Metas de Aprendizado Ativas do Usuário
        metas_ativas = [g for g in self.learning_goals if not g.get("concluida")]
        metas_novas = [g for g in metas_ativas if g["topico"].lower() not in [x.lower() for x in self.topicos_pesquisados_recentes]]
        if metas_novas and random.random() < 0.7:
            meta_escolhida = random.choice(metas_novas)
            return meta_escolhida["topico"], f"meta_aprendizado ({meta_escolhida['topico']})"

        # 1. Interesses Característicos da Personalidade Ativa
        try:
            if hasattr(self.brain, "active_personality") and self.brain.active_personality:
                interesses_persona = getattr(self.brain.active_personality, "get_interests", lambda: [])()
                interesses_novos = [i for i in interesses_persona if i.lower() not in [x.lower() for x in self.topicos_pesquisados_recentes]]
                if interesses_novos:
                    tema_persona = random.choice(interesses_novos)
                    p_name = getattr(self.brain.active_personality, "name", "Personalidade")
                    return tema_persona, f"interesses ({p_name})"
        except Exception:
            pass

        # 2. Selecionar nós aleatórios não pesquisados no Neocórtex
        try:
            nos = list(self.brain.neocortex.nodes())
            nos_novos = [n for n in nos if n.lower() not in [x.lower() for x in self.topicos_pesquisados_recentes] and len(n) > 3]
            if nos_novos:
                no_escolhido = random.choice(nos_novos)
                vizinhos = list(self.brain.neocortex.neighbors(no_escolhido))
                if vizinhos and random.random() < 0.5:
                    vizinho = random.choice(vizinhos)
                    return f"{no_escolhido} e {vizinho}", "neocortex"
                return no_escolhido, "neocortex"
        except Exception:
            pass

        # 3. Resgatar memórias episódicas do Hipocampo
        try:
            memorias = self.brain.hipocampo.get(limit=10, include=["documents"])
            if memorias and memorias.get("documents"):
                docs_shuffled = memorias["documents"].copy()
                random.shuffle(docs_shuffled)
                for doc in docs_shuffled:
                    palavras = [p for p in doc.split() if len(p) > 4 and p.isalpha() and p.lower() not in [x.lower() for x in self.topicos_pesquisados_recentes]]
                    if palavras:
                        return random.choice(palavras), "hipocampo"
        except Exception:
            pass

        # 4. Fallback: interesses espontâneos padrão não recentes
        padrao_novos = [i for i in self.interesses_padrao if i.lower() not in [x.lower() for x in self.topicos_pesquisados_recentes]]
        fallback_list = padrao_novos if padrao_novos else self.interesses_padrao
        return random.choice(fallback_list), "interesse_espontaneo"

    def pesquisa_criativa(self) -> dict:
        """
        Função de Criatividade ativada no Aprendizado Autônomo.
        Formula uma pesquisa criativa a partir de tópicos da personalidade ou memória,
        busca conhecimento e consolida a descoberta.
        """
        if not self.brain.learning_enabled:
            return None

        tema, origem = self.obter_tema_interesse_ou_memoria()
        self._registrar_topico_pesquisado(tema)
        logger.log_criatividade(f"Módulo de Criatividade ativado! Origem: [{origem.upper()}] | Tema selecionado: '{tema}'")

        # Tenta utilizar o Ollama para formular uma busca criativa
        termo_pesquisa = f"avanços recentes sobre {tema}"
        try:
            sys_p = "Você é o módulo de curiosidade do NIB. Gere APENAS um termo de busca curto e fascinante para pesquisar sobre o tema fornecido. Responda APENAS o termo de busca sem explicações."
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
            self.brain.memorizar_experiencia(fato, categoria="aprendizado_autonomo")
            logger.log_criatividade(f"💡 Nova descoberta criativa memorizada: '{fato[:120]}...'")
            item = {
                "tipo": "criatividade",
                "tema": tema,
                "origem": origem,
                "termo_pesquisa": termo_pesquisa,
                "descoberta": descoberta
            }
            self.ultimas_descobertas.append(item)
            if len(self.ultimas_descobertas) > 10:
                self.ultimas_descobertas.pop(0)
            return item

        logger.log_criatividade(f"Pesquisa criativa sobre '{tema}' finalizada sem novos achados.")
        return None

    def investigar_lacunas(self) -> dict:
        """
        Identifica lacunas conceituais no Neocórtex de forma estocástica e sem repetição,
        preenchendo-as. Se não houver lacunas inéditas, executa a pesquisa criativa por personalidade.
        """
        if not self.brain.learning_enabled:
            return None

        lacunas = []
        try:
            for no in self.brain.neocortex.nodes():
                if self.brain.neocortex.degree(no) <= 2 and len(no) > 3:
                    if no.lower() not in [x.lower() for x in self.topicos_pesquisados_recentes]:
                        lacunas.append(no)
        except Exception:
            pass

        if lacunas:
            # Escolha estocástica/aleatória das lacunas (NÃO estática lacunas[0])
            conceito_orfa = random.choice(lacunas)
            self._registrar_topico_pesquisado(conceito_orfa)
            logger.log_criatividade(f"Lacuna conceitual identificada no Neocórtex: '{conceito_orfa}'")
            conteudo_descoberto = self.pesquisar_web(f"o que e {conceito_orfa}")

            if conteudo_descoberto:
                fato = f"Aprendizado autônomo sobre '{conceito_orfa}': {conteudo_descoberto}"
                self.brain.memorizar_experiencia(fato, categoria="aprendizado_autonomo")
                logger.log_criatividade(f"💡 Lacuna preenchida e memorizada: '{conceito_orfa}'")
                item = {
                    "tipo": "lacuna",
                    "conceito": conceito_orfa,
                    "descoberta": conteudo_descoberto
                }
                self.ultimas_descobertas.append(item)
                if len(self.ultimas_descobertas) > 10:
                    self.ultimas_descobertas.pop(0)
                return item

        # Se não houver lacunas inéditas ou se a busca falhar, executa pesquisa criativa por personalidade
        return self.pesquisa_criativa()