import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import config

class TestNeuroInformatikBrain(unittest.TestCase):
    def setUp(self):
        try:
            self.test_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        except TypeError:
            self.test_dir = tempfile.TemporaryDirectory()
        self.orig_hippocampus = config.HIPPOCAMPUS_DIR
        self.orig_neocortex = config.NEOCORTEX_FILE
        self.orig_wal = config.SYNAPTIC_JOURNAL

        config.HIPPOCAMPUS_DIR = os.path.join(self.test_dir.name, "hippocampus")
        config.NEOCORTEX_FILE = os.path.join(self.test_dir.name, "neocortex_graph.json")
        config.SYNAPTIC_JOURNAL = os.path.join(self.test_dir.name, "synaptic_journal.jsonl")
        os.makedirs(config.HIPPOCAMPUS_DIR, exist_ok=True)

        from nib_brain import NeuroInformatikBrain
        self.brain = NeuroInformatikBrain()

    def tearDown(self):
        config.HIPPOCAMPUS_DIR = self.orig_hippocampus
        config.NEOCORTEX_FILE = self.orig_neocortex
        config.SYNAPTIC_JOURNAL = self.orig_wal
        try:
            self.test_dir.cleanup()
        except Exception:
            pass

    def test_consolidar_sinapse(self):
        self.brain.consolidar_sinapse("Python", "e_um", "Linguagem", 1000)
        self.assertTrue(self.brain.neocortex.has_node("python"))
        self.assertTrue(self.brain.neocortex.has_node("linguagem"))
        self.assertTrue(self.brain.neocortex.has_edge("python", "linguagem"))
        self.assertEqual(self.brain.neocortex["python"]["linguagem"]["relacao"], "e_um")

    def test_consolidar_sinapse_empty_input(self):
        self.brain.consolidar_sinapse("", "rel", "objeto", 1000)
        self.assertEqual(len(self.brain.neocortex.nodes()), 0)

    @patch("requests.post")
    def test_memorizar_experiencia(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "response": '{"triplas": [{"sujeito": "IA", "relacao": "processa", "objeto": "dados"}]}'
        }
        mock_post.return_value = mock_resp

        self.brain.memorizar_experiencia("IA processa dados")
        self.assertTrue(self.brain.neocortex.has_edge("ia", "dados"))

        # Verify WAL log file
        self.assertTrue(os.path.exists(config.SYNAPTIC_JOURNAL))
        with open(config.SYNAPTIC_JOURNAL, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("IA processa dados", content)

    def test_resgatar_memoria_relevante(self):
        self.brain.consolidar_sinapse("algoritmo", "gera", "codigo", 1000)
        res = self.brain.resgatar_memoria_relevante("algoritmo de teste")
        self.assertIn("algoritmo", res)
        self.assertIn("codigo", res)

    def test_eh_dialogo_informal(self):
        self.assertTrue(self.brain.eh_dialogo_informal("quer ser meu amigo?"))
        self.assertTrue(self.brain.eh_dialogo_informal("olá NIB tudo bem"))
        self.assertFalse(self.brain.eh_dialogo_informal("o que é a teoria da relatividade geral?"))

    def test_deduplicacao_memoria_trabalho(self):
        self.brain.registrar_interacao_trabalho("quer ser meu amigo", "Claro! Podemos ser amigos.")
        self.brain.hipocampo.add(documents=["Claro! Podemos ser amigos."], ids=["synapse_test_1"])
        res = self.brain.resgatar_memoria_relevante("quer ser meu amigo")
        # Deve omitir a memória episódica repetida que já está na memória de trabalho
        self.assertNotIn("[Memória Episódica]: Claro! Podemos ser amigos.", res)

if __name__ == "__main__":
    unittest.main()
