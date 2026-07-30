import os
import json
import threading
import requests
import logger_nib as logger

WEBHOOK_CONFIG_FILE = os.path.join("nib_storage", "webhook_config.json")

class WebhookManager:
    """
    Gerenciador de Webhooks e Notificações Ativas do NIB.
    Permite disparar notificações HTTP POST em background para Discord, Slack ou servidores customizados.
    """
    _webhook_url = None

    @classmethod
    def load_config(cls) -> str:
        if cls._webhook_url:
            return cls._webhook_url
        if os.path.exists(WEBHOOK_CONFIG_FILE):
            try:
                with open(WEBHOOK_CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    cls._webhook_url = data.get("url")
                    return cls._webhook_url
            except Exception:
                pass
        return None

    @classmethod
    def set_url(cls, url: str) -> bool:
        cls._webhook_url = url.strip() if url else None
        os.makedirs("nib_storage", exist_ok=True)
        try:
            with open(WEBHOOK_CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump({"url": cls._webhook_url}, f, ensure_ascii=False, indent=2)
            logger.log_nib("WEBHOOK", f"URL de Webhook atualizada: '{cls._webhook_url}'", logger.Colors.BRIGHT_GREEN)
            return True
        except Exception as e:
            logger.log_nib("WEBHOOK ERRO", f"Erro ao salvar Webhook: {e}", logger.Colors.BRIGHT_RED)
            return False

    @classmethod
    def notify(cls, event_type: str, title: str, details: str, payload_extra: dict = None):
        """Envia notificação via HTTP POST em uma thread separada (não-bloqueante)."""
        url = cls.load_config()
        if not url:
            return

        def send_async():
            try:
                body = {
                    "event": event_type,
                    "title": title,
                    "details": details,
                    "extra": payload_extra or {},
                    "source": "NIB Cognitive Assistant"
                }
                # Formato amigável para Discord
                if "discord.com" in url:
                    body = {
                        "embeds": [{
                            "title": f"🧠 NIB — {title}",
                            "description": details,
                            "color": 38007,
                            "fields": [
                                {"name": "Evento", "value": event_type, "inline": True}
                            ]
                        }]
                    }
                requests.post(url, json=body, timeout=5)
                logger.log_nib("WEBHOOK SUCESSO", f"Notificação disparada: [{event_type}] '{title}'", logger.Colors.BRIGHT_GREEN)
            except Exception as e:
                logger.log_nib("WEBHOOK AVISO", f"Falha ao enviar webhook: {e}", logger.Colors.YELLOW)

        thread = threading.Thread(target=send_async, daemon=True)
        thread.start()
