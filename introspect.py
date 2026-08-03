import os
import json
import config

class NIBIntrospector:
    """
    Módulo de Introspecção do NIB.
    Mapeia e persiste a autoconsciência da arquitetura de código e capacidades do sistema.
    """
    def __init__(self, base_dir: str = None, cache_path: str = None):
        self.base_dir = base_dir or getattr(config, "BASE_DIR", ".")
        self.cache_path = cache_path or getattr(config, "INTROSPECT_CACHE_FILE", os.path.join(self.base_dir, "nib_storage", "introspect_capacities.json"))

    def mapear_capacidades_sistema(self) -> str:
        """Lê a estrutura dos arquivos .py e resume classes, funções e rotas disponíveis."""
        ignorar = {".venv", "venv", "__pycache__", ".git", "build", "dist"}
        mapa = ["=== ARQUITETURA DE CÓDIGO E CAPACIDADES DO NIB ==="]
        
        for root, dirs, files in os.walk(self.base_dir):
            dirs[:] = [d for d in dirs if d not in ignorar]
            for arq in sorted(files):
                if arq.endswith(".py"):
                    caminho = os.path.join(root, arq)
                    rel_path = os.path.relpath(caminho, self.base_dir)
                    mapa.append(f"\n📄 [Arquivo: {rel_path}]")
                    
                    try:
                        with open(caminho, "r", encoding="utf-8") as f:
                            for linha in f:
                                l = linha.strip()
                                if l.startswith("class ") or l.startswith("def ") or l.startswith("@app."):
                                    mapa.append(f"  • {l}")
                    except Exception:
                        pass

        return "\n".join(mapa)

    def obter_ou_gerar_capacidades(self, force_refresh: bool = False) -> str:
        """
        Retorna o mapa de capacidades. Se já existir no cache em disco e force_refresh=False,
        carrega direto da memória persistida.
        """
        if not force_refresh and os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                    if isinstance(dados, dict) and "capacidades" in dados:
                        return dados["capacidades"]
            except Exception:
                pass

        conteudo = self.mapear_capacidades_sistema()
        self.salvar_memoria_introspectiva(conteudo)
        return conteudo

    def salvar_memoria_introspectiva(self, conteudo: str):
        """Grava o mapa de introspecção no arquivo JSON de cache."""
        try:
            os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
            payload = {
                "timestamp": os.path.getmtime(self.base_dir) if os.path.exists(self.base_dir) else 0,
                "capacidades": conteudo
            }
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[INTROSPECÇÃO] Erro ao gravar cache em disco: {e}")

    # Alias para compatibilidade
    Mapear_capacidades_sistema = mapear_capacidades_sistema