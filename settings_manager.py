import os
import json
import config
import logger_nib as logger

SETTINGS_FILE = os.path.join(config.STORAGE_DIR, "system_settings.json")

DEFAULT_SETTINGS = {
    "ollama_model": "qwen2.5-coder:latest",
    "memory_mode": "human",
    "learning_enabled": False,
    "personality_enabled": True,
    "active_personality_id": "custom_slider",
    "personality_sliders": {
        "o_pct": 80,
        "c_pct": 90,
        "e_pct": 40,
        "a_pct": 70,
        "n_pct": 20
    },
    "emotion_enabled": True,
    "auto_emotion": False,
    "subconscious_enabled": False
}

def load_settings() -> dict:
    """Carrega as configurações salvas em disco ou retorna os valores padrão."""
    settings = dict(DEFAULT_SETTINGS)
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    settings.update(data)
        except Exception as e:
            logger.log_warning(f"Erro ao carregar system_settings.json: {e}")
    return settings

def save_settings(settings_data: dict):
    """Salva a estrutura completa de configurações em disco."""
    try:
        current = load_settings()
        current.update(settings_data)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(current, f, ensure_ascii=False, indent=2)
        logger.log_nib("CONFIGURAÇÃO PERSISTENTE", "Configurações do NIB gravadas em disco com sucesso.", logger.Colors.BRIGHT_GREEN)
    except Exception as e:
        logger.log_warning(f"Erro ao salvar system_settings.json: {e}")

def update_setting(key: str, value):
    """Atualiza uma chave específica nas configurações salvas."""
    current = load_settings()
    current[key] = value
    save_settings(current)
