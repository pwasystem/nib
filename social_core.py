import json
import time
import requests
import config

class SocialCore:
    """
    Módulo de Gestão de Relacionamentos Sociais do NIB.
    Mapeia conexões humanas, preferências e histórico afetivo no Neocórtex/Hipocampo.
    """
    def __init__(self, brain_instance):
        self.brain = brain_instance

    def registrar_ou_atualizar_pessoa(self, nome: str, relacao: str, detalhes: str):
        """
        Cadastra uma pessoa importante no círculo social do usuário/NIB.
        """
        ts = int(time.time())
        nome_clean = nome.strip().lower()
        relacao_clean = relacao.strip().lower()

        # 1. Registra o vínculo estrutural no Neocórtex (GraphRAG)
        self.brain.consolidar_sinapse("usuario", f"tem_{relacao_clean}", nome_clean, ts)
        
        # 2. Grava o contexto detalhado na memória episódica do Hipocampo
        fato_social = f"[Rede Social/Relação]: {nome.title()} ({relacao}). Detalhes e Preferências: {detalhes}"
        self.brain.memorizar_experiencia(fato_social)

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