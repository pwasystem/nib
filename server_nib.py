import os
import json
import requests
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware


import config
import logger_nib as logger
from nib_brain import NeuroInformatikBrain
from nib_affective import NIBAffectiveCore
from curiosity_core import CuriosityCore
from personality_factory import PersonalityFactory

app = FastAPI(title="NIB - Neuro-Informatik Brain")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instancia o Núcleo Integrado Biológico
nib = NeuroInformatikBrain()
nib_affective = NIBAffectiveCore()
curiosity = CuriosityCore(nib)

# Instancia a personalidade inicial (Default via sliders)
nib.active_personality = PersonalityFactory.create_personality("custom_slider")


@app.get("/api/generate")
@app.head("/api/generate")
def generate_info():
    return {"status": "info", "message": "O endpoint de geração exige requisições POST com payload JSON."}


@app.get("/", response_class=HTMLResponse)
def get_index():
    index_path = os.path.join(config.BASE_DIR, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        return f.read()


@app.get("/api/memory-mode")
async def get_memory_mode():
    """Retorna o modo de memória ativo no NIB."""
    return {"status": "success", "mode": nib.memory_mode}


@app.post("/api/set-memory-mode")
async def set_memory_mode(request: Request):
    """Altera o modo de memória entre 'human' e 'perfect'."""
    data = await request.json()
    novo_modo = data.get("mode", "human")
    modo_atual = nib.set_memory_mode(novo_modo)
    return {"status": "success", "mode": modo_atual}


@app.post("/api/prune-memory")
async def prune_memory():
    """Aciona manualmente a poda sináptica no Modo Humano."""
    if nib.memory_mode != "human":
        return {"status": "error", "message": "A poda sináptica só é aplicável no Modo Humano."}
    
    nib.aplicar_esquecimento_hebbiano(limiar_corte=0.15)
    return {"status": "success", "message": "Poda sináptica executada com sucesso!"}


@app.get("/api/working-memory")
async def get_working_memory():
    """Retorna o histórico mantido no buffer de curto prazo (Memória de Trabalho)."""
    return {
        "status": "success",
        "capacity": nib.working_memory.capacity,
        "size": len(nib.working_memory.buffer),
        "history": nib.working_memory.to_list()
    }


@app.post("/api/clear-working-memory")
async def clear_working_memory():
    """Esvazia o buffer da Memória de Trabalho."""
    nib.reset_memoria_trabalho()
    return {"status": "success", "message": "Memória de trabalho limpa com sucesso!"}


@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Retorna dados consolidados para o Dashboard Cognitivo (estatísticas de memória, podas e personalidade)."""
    stats = nib.obter_estatisticas_memoria()
    stats["status"] = "success"
    stats["personality"] = {
        "enabled": nib.personality_enabled,
        "description": nib.active_personality.get_description() if hasattr(nib.active_personality, "get_description") else "",
        "sliders": {
            "o": getattr(nib.active_personality, "o_pct", 80),
            "c": getattr(nib.active_personality, "c_pct", 90),
            "e": getattr(nib.active_personality, "e_pct", 40),
            "a": getattr(nib.active_personality, "a_pct", 70),
            "n": getattr(nib.active_personality, "n_pct", 20),
        }
    }
    stats["affective"] = {
        "enabled": nib_affective.emotion_enabled,
        "auto_mode": nib_affective.auto_mode,
        "current_emotion": nib_affective.current_emotion,
        "p": round(nib_affective.pleasure, 2),
        "a": round(nib_affective.arousal, 2),
        "d": round(nib_affective.dominance, 2)
    }
    return stats


@app.get("/api/dashboard/graph")
async def get_dashboard_graph():
    """Retorna os nós e conexões do Neocórtex formatados para visualização interativa em grafo."""
    graph_data = nib.obter_dados_grafo()
    graph_data["status"] = "success"
    return graph_data




@app.post("/api/toggle-learning")
async def toggle_learning(request: Request):
    data = await request.json()
    nib.learning_enabled = data.get("enabled", False)
    
    descoberta_inicial = None
    if nib.learning_enabled:
        descoberta_inicial = curiosity.investigar_lacunas()
        
    return {
        "status": "success", 
        "learning_enabled": nib.learning_enabled,
        "descoberta": descoberta_inicial
    }


@app.post("/api/toggle-personality")
async def toggle_personality(request: Request):
    data = await request.json()
    nib.personality_enabled = data.get("enabled", True)
    return {
        "status": "success",
        "personality_enabled": nib.personality_enabled
    }


@app.post("/api/kill-and-rebirth")
async def kill_and_rebirth():
    """Apaga toda a memória do NIB e inicia um novo ciclo de vida."""
    nib.reset_memoria_completa()
    nib_affective.reset_emotion()
    nib.personality_enabled = True
    nib.learning_enabled = False

    mensagem_apresentacao = (
        "# 🧠 Olá! Eu sou o NIB (Neuro-Informatik Brain).\n\n"
        "Iniciei um **novo ciclo de vida** com minha memória totalmente limpa e zerada. Estou pronto para aprender e evoluir com você!\n\n"
        "### ⚡ Minhas Capacidades Cognitivas:\n\n"
        f"- 🧠 **Modo de Memória Atual**: **{nib.memory_mode.upper()}**\n"
        "- 🧠 **Hipocampo (Memória Episódica)**: Armazeno nossas conversas em banco vetorial (ChromaDB).\n"
        "- 🕸️ **Neocórtex (Memória Semântica & GraphRAG)**: Mapeio conceitos e conexões sinápticas.\n"
        "- 🧪 **Sistema Límbico (Modelo PAD)**: Reajo emocionalmente em tempo real.\n"
        "- 🎛️ **Córtex Pré-Frontal (Big Five / OCEAN)**: Adapto minha personalidade.\n"
        "- 💡 **Aprendizado Autônomo & Pesquisa Acadêmica**: Pesquiso fontes acadêmicas/web quando necessário.\n\n"
        "Como posso ajudar você hoje nesta nova jornada?"
    )

    return {
        "status": "success",
        "intro": mensagem_apresentacao
    }


@app.post("/api/toggle-emotion")
async def toggle_emotion(request: Request):
    data = await request.json()
    enabled = data.get("enabled", True)
    nib_affective.set_emotion_enabled(enabled)
    return {
        "status": "success",
        "emotion_enabled": nib_affective.emotion_enabled,
        "instruction": nib_affective.get_mood_instruction()
    }


@app.post("/api/set-custom-personality")
async def set_custom_personality(request: Request):
    data = await request.json()
    nib.active_personality = PersonalityFactory.create_personality(
        "custom_slider",
        name="Personalidade Customizada",
        o_pct=data.get("o_pct", 80),
        c_pct=data.get("c_pct", 90),
        e_pct=data.get("e_pct", 40),
        a_pct=data.get("a_pct", 70),
        n_pct=data.get("n_pct", 20)
    )
    return {
        "status": "success",
        "description": nib.active_personality.get_description()
    }


@app.post("/api/set-emotion")
async def set_emotion(request: Request):
    data = await request.json()
    p_val = float(data.get("p", 20))
    a_val = float(data.get("a", -10))
    d_val = float(data.get("d", 30))

    nib_affective.set_pad_direct(p_val, a_val, d_val)
    return {
        "status": "success",
        "instruction": nib_affective.get_mood_instruction()
    }

@app.post("/api/toggle-auto-emotion")
async def toggle_auto_emotion(request: Request):
    data = await request.json()
    enabled = data.get("enabled", False)
    nib_affective.set_auto_mode(enabled)
    return {
        "status": "success",
        "auto_mode": nib_affective.auto_mode,
        "p": nib_affective.pleasure,
        "a": nib_affective.arousal,
        "d": nib_affective.dominance,
        "instruction": nib_affective.get_mood_instruction()
    }

@app.get("/api/ollama-models")
async def get_ollama_models():
    """Busca a lista de modelos instalados diretamente no Ollama local de forma assíncrona."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get("http://localhost:11434/api/tags")
            modelos = [m["name"] for m in resp.json().get("models", [])]
            return {"status": "success", "models": modelos, "current": config.OLLAMA_MODEL}
    except Exception:
        return {"status": "error", "models": [config.OLLAMA_MODEL], "current": config.OLLAMA_MODEL}

@app.post("/api/set-ollama-model")
async def set_ollama_model(request: Request):
    """Altera o modelo ativo do Ollama em tempo de execução."""
    data = await request.json()
    novo_modelo = data.get("model")
    if novo_modelo:
        config.OLLAMA_MODEL = novo_modelo
        nib.model_name = novo_modelo
        return {"status": "success", "current": config.OLLAMA_MODEL}
    return {"status": "error", "message": "Modelo inválido"}

@app.get("/api/chat")
async def chat_stream(prompt: str):
    async def generate():
        logger.log_nib("CHAT API", f"Nova interação recebida | Modo Memória: {nib.memory_mode.upper()}", logger.Colors.BRIGHT_MAGENTA)
        
        if nib_affective.auto_mode and nib_affective.emotion_enabled:
            nib_affective.reajustar_emocao_automatica(prompt)
            
        descoberta_autonoma = None
        if nib.learning_enabled:
            descoberta_autonoma = curiosity.investigar_lacunas()

        memoria_contexto = nib.resgatar_memoria_relevante(prompt)
        contexto_trabalho = nib.obter_contexto_trabalho()
        
        instrucao_personalidade = nib.active_personality.build_system_instruction() if nib.personality_enabled else "Sua personalidade está desativada: responda de maneira neutra, clara e objetiva sem traços de personalidade marcantes."
        instrucao_humor = nib_affective.get_mood_instruction() if nib_affective.emotion_enabled else "Seu módulo emocional está desativado: mantenha um tom neutro e imparcial."
        temp_dinamica = nib_affective.get_temperature_modifier() if nib_affective.emotion_enabled else 0.4

        sys_prompt = (
            f"Você é o NIB (Neuro-Informatik Brain). "
            f"{instrucao_personalidade} "
            f"{instrucao_humor} "
            f"Responda diretamente ao usuário em texto fluído, legível e bem formatado usando Markdown (títulos, tópicos, negrito e blocos de código quando apropriado). "
            f"IMPORTANTE: NUNCA responda em formato JSON bruto e NUNCA envolva sua mensagem em chaves JSON como {{'resposta': ...}} ou estruturas de objeto."
        )

        prompt_final = (
            f"--- MEMÓRIA DE LONGO PRAZO ({nib.memory_mode.upper()}) ---\n{memoria_contexto}\n\n"
            f"--- MEMÓRIA DE TRABALHO (DIÁLOGO RECENTE) ---\n{contexto_trabalho}\n\n"
            f"Usuário: {prompt}\nNIB:"
        )

        resposta_completa = ""
        try:
            payload = {
                "model": config.OLLAMA_MODEL,
                "prompt": prompt_final,
                "system": sys_prompt,
                "stream": True,
                "options": {"temperature": temp_dinamica}
            }
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream("POST", config.OLLAMA_URL, json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line:
                            data = json.loads(line)
                            token = data.get("response", "")
                            resposta_completa += token
                            yield f"data: {json.dumps({'token': token})}\n\n"
        except Exception as e:
            status_code = getattr(getattr(e, 'response', None), 'status_code', None)
            if status_code == 404:
                err_msg = f"\n\n*[Erro no Ollama: O modelo '{config.OLLAMA_MODEL}' não está instalado. Selecione um modelo instalado na engrenagem ⚙️ ou execute 'ollama pull {config.OLLAMA_MODEL}']* "
            else:
                err_msg = f"\n\n*[Erro de comunicação com o Ollama: {str(e)}. Verifique se o Ollama está rodando em http://localhost:11434]*"
            yield f"data: {json.dumps({'token': err_msg})}\n\n"
            yield "data: [DONE]\n\n"
            return

        if resposta_completa.strip():
            nib.registrar_interacao_trabalho(prompt, resposta_completa)
            nib.memorizar_experiencia(f"Usuário: '{prompt}' | NIB: '{resposta_completa}'")


        
        if descoberta_autonoma:
            conceito_nome = descoberta_autonoma.get("conceito") or descoberta_autonoma.get("tema", "Criatividade Autônoma")
            evento_curiosidade = json.dumps({
                "curiosidade": True,
                "tipo": descoberta_autonoma.get("tipo", "criatividade"),
                "conceito": conceito_nome,
                "texto": descoberta_autonoma.get("descoberta", "")
            })
            yield f"data: {evento_curiosidade}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn
    logger.log_success(f"Iniciando servidor FastAPI NIB em http://{config.SERVER_HOST}:{config.SERVER_PORT}")
    uvicorn.run(app, host=config.SERVER_HOST, port=config.SERVER_PORT)