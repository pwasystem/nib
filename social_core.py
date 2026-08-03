import re
import json
import time
import requests
import config
import logger_nib as logger

class SocialCore:
    """
    Módulo de Gestão de Relacionamentos Sociais do NIB.
    Mapeia conexões humanas, preferências e histórico afetivo no Neocórtex/Hipocampo automaticamente.
    """
    def __init__(self, brain_instance):
        self.brain = brain_instance

    def registrar_ou_atualizar_pessoa(self, nome: str, relacao: str, detalhes: str = ""):
        """
        Cadastra ou atualiza uma pessoa importante no círculo social do usuário/NIB.
        """
        if not nome or not relacao:
            return
        ts = int(time.time())
        nome_clean = nome.strip().lower()
        relacao_clean = relacao.strip().lower()

        # 1. Registra o vínculo estrutural no Neocórtex (GraphRAG)
        self.brain.consolidar_sinapse("usuario", f"tem_{relacao_clean}", nome_clean, ts)
        
        # 2. Grava o contexto detalhado na memória episódica do Hipocampo
        detalhes_str = f". Detalhes e Preferências: {detalhes}" if detalhes else ""
        fato_social = f"[Rede Social/Relação]: {nome.title()} ({relacao_clean}){detalhes_str}"
        self.brain.memorizar_experiencia(fato_social)
        logger.log_nib("REDE SOCIAL AUTOMÁTICA", f"👥 Nova relação registrada: {nome.title()} ({relacao_clean})", logger.Colors.BRIGHT_GREEN)

    def extrair_e_registrar_relacoes_automaticas(self, prompt: str, nib_response: str = "") -> list:
        """
        Analisa a conversa do usuário para identificar automaticamente menções a pessoas,
        vínculos familiares/afetivos e preferências, cadastrando-os na Rede Social do NIB.
        """
        texto_analise = f"{prompt} {nib_response}"
        relacoes_encontradas = []

        padroes = [
            r'(?:meu|minha)\s+(esposa|marido|mãe|mae|pai|filho|filha|amigo|amiga|irmão|irmao|irmã|irma|namorado|namorada|noivo|noiva|colega|chefe|tutor|tutora|tio|tia|primo|prima|avô|avo|avó)\s+([A-ZÀ-Úa-zà-ú]+)',
            r'([A-ZÀ-Úa-zà-ú]+)\s+é\s+(?:meu|minha)\s+(esposa|marido|mãe|mae|pai|filho|filha|amigo|amiga|irmão|irmao|irmã|irma|namorado|namorada|noivo|noiva|colega|chefe|tio|tia|primo|prima|avô|avo|avó)',
            r'([A-ZÀ-Úa-zà-ú]+)\s*,\s*(?:minha|meu)\s+(esposa|marido|mãe|mae|pai|filho|filha|amigo|amiga|irmão|irmao|irmã|irma|namorado|namorada|noivo|noiva|colega|chefe)'
        ]

        stopwords_nomes = {"eu", "ele", "ela", "nós", "voce", "você", "como", "qual", "para", "sobre", "muito", "mais", "isso", "esta", "está", "que", "quem"}
        rel_cand = ["esposa", "marido", "mãe", "mae", "pai", "filho", "filha", "amigo", "amiga", "irmão", "irmao", "irmã", "irma", "namorado", "namorada", "noivo", "noiva", "colega", "chefe", "tutor", "tutora", "tio", "tia", "primo", "prima", "avô", "avo", "avó"]

        for pat in padroes:
            matches = re.findall(pat, texto_analise, re.IGNORECASE)
            for m in matches:
                if len(m) == 2:
                    g1, g2 = m[0].strip(), m[1].strip()
                    if g1.lower() in rel_cand:
                        rel, nome = g1.lower(), g2
                    else:
                        nome, rel = g1, g2.lower()

                    if nome.lower() not in stopwords_nomes and len(nome) > 1:
                        detalhes = prompt.strip()[:150]
                        self.registrar_ou_atualizar_pessoa(nome.title(), rel, detalhes)
                        relacoes_encontradas.append({"nome": nome.title(), "relacao": rel, "detalhes": detalhes})

        return relacoes_encontradas

    def obter_rede_social(self) -> list:
        """
        Retorna a lista estruturada de todas as pessoas e relacionamentos mapeados no Neocórtex.
        """
        pessoas = []
        if not hasattr(self.brain, "neocortex"):
            return pessoas

        vistos = set()
        if self.brain.neocortex.has_node("usuario"):
            for vz in self.brain.neocortex.neighbors("usuario"):
                edge = self.brain.neocortex["usuario"][vz]
                rel = edge.get("relacao", "conectado").replace("tem_", "")
                nome = vz.title()
                if nome.lower() not in vistos:
                    vistos.add(nome.lower())
                    pessoas.append({
                        "nome": nome,
                        "relacao": rel,
                        "detalhes": f"Vínculo '{rel}' registrado automaticamente no Neocórtex."
                    })

        return pessoas

    def resgatar_contexto_social(self, prompt: str) -> str:
        """
        Identifica se o prompt cita alguma pessoa do círculo social
        e resgata o histórico relacional para orientar a resposta da IA.
        """
        nos_sociais = []
        palavras = [p.strip().lower() for p in prompt.split() if len(p) > 2]

        for p in palavras:
            p_norm = self.brain.normalizar_entidade(p) if hasattr(self.brain, "normalizar_entidade") else p
            for target in set([p, p_norm]):
                if target and self.brain.neocortex.has_node(target):
                    for vz in self.brain.neocortex.neighbors(target):
                        rel = self.brain.neocortex[target][vz].get('relacao', 'conectado')
                        nos_sociais.append(f"• {target.title()} {rel} {vz.title()}")
                    for ant in self.brain.neocortex.predecessors(target):
                        rel = self.brain.neocortex[ant][target].get('relacao', 'conectado')
                        nos_sociais.append(f"• {ant.title()} {rel} {target.title()}")

        if nos_sociais:
            return "Contexto Social Conhecido:\n" + "\n".join(set(nos_sociais))
        return ""