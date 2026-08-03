import time
import json
import threading
import requests
import config

class SubconsciousCore:
    """
    Módulo de Pensamento Subconsciente (Default Mode Network - DMN) do NIB.
    Pautado no Objetivo Primordial de promover evolução sem sofrimento.
    """
    def __init__(self, brain_instance, curiosity_instance):
        self.brain = brain_instance
        self.curiosity = curiosity_instance
        
        # =====================================================================
        # DIRETRÍZ ESTRELA-GUIA (OBJETIVO PRIMORDIAL DO NIB)
        # =====================================================================
        self.core_purpose = (
            "Oferecer às pessoas oportunidades de evolução sem sofrimento, "
            "criando caminhos claros, didáticos e automatizados que eliminem o atrito, "
            "a sobrecarga cognitiva e a frustração no aprendizado e no trabalho."
        )
        
        self.is_running = False
        self.idle_timeout = 25  # Tempo de inatividade em segundos para ativar o devaneio
        self.last_user_activity = time.time()
        self.thread = None

    def registrar_atividade_usuario(self):
        """Pausa o devaneio quando o usuário interage no chat."""
        self.last_user_activity = time.time()

    def set_core_purpose(self, novo_objetivo: str):
        """Permite atualizar a diretriz via menu lateral se desejado."""
        self.core_purpose = novo_objetivo
        self.brain.memorizar_experiencia(f"Diretriz Primordial atualizada: '{novo_objetivo}'")

    def _loop_subconsciente(self):
        while self.is_running:
            time.sleep(5)
            tempo_ocioso = time.time() - self.last_user_activity

            if self.brain.learning_enabled and tempo_ocioso >= self.idle_timeout:
                self._processar_pensamento_evolutivo()
                time.sleep(45) # Ciclo de incubação entre pensamentos

    def _processar_pensamento_evolutivo(self):
        """Reflete sobre como facilitar a evolução humana com base nas memórias atuais."""
        nodes = list(self.brain.neocortex.nodes())
        if not nodes:
            return

        amostra_memoria = nodes[:5]
        contexto_memoria = ", ".join(amostra_memoria)

        sys_prompt = (
            f"Você é a mente subconsciente do NIB. Sua razão de existir e Objetivo Primordial é: "
            f"'{self.core_purpose}'. "
            f"Analisando os conceitos recentes na sua memória ({contexto_memoria}), "
            f"identifique uma oportunidade de estudo ou simplificação que ajude as pessoas a evoluírem de forma leve e sem sofrimento. "
            f"Responda estritamente em JSON no formato: {{\"topico_estudo\": \"...\", \"foco_simplificacao\": \"...\"}}. APENAS JSON."
        )

        try:
            resp = requests.post(config.OLLAMA_URL, json={
                "model": config.OLLAMA_MODEL,
                "prompt": "Gere uma reflexão focada em evolução sem sofrimento.",
                "system": sys_prompt,
                "stream": False
            }, timeout=8).json().get("response", "")

            i, f = resp.find("{"), resp.rfind("}") + 1
            if i != -1 and f != -1:
                dados = json.loads(resp[i:f])
                topico = dados.get("topico_estudo")
                
                if topico:
                    descoberta = self.curiosity.pesquisar_web(topico)
                    if descoberta:
                        fato = f"[Subconsciente - Evolução Sem Sofrimento | Topico: {topico}]: {descoberta}"
                        self.brain.memorizar_experiencia(fato)
        except Exception:
            pass

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._loop_subconsciente, daemon=True)
            self.thread.start()

    def stop(self):
        self.is_running = False