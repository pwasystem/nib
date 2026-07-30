import unittest
from unittest.mock import MagicMock, patch
import networkx as nx

from curiosity_core import CuriosityCore

class TestCuriosityCore(unittest.TestCase):
    def setUp(self):
        self.mock_brain = MagicMock()
        self.mock_brain.learning_enabled = True
        self.mock_brain.neocortex = nx.DiGraph()
        self.mock_brain.ollama_url = "http://localhost:11434/api/generate"
        self.mock_brain.model_name = "qwen2.5:3b"
        self.curiosity = CuriosityCore(self.mock_brain)

    def test_disabled_learning(self):
        self.mock_brain.learning_enabled = False
        self.assertIsNone(self.curiosity.pesquisa_criativa())
        self.assertIsNone(self.curiosity.investigar_lacunas())

    def test_obter_tema_interesse_ou_memoria_fallback(self):
        tema, origem = self.curiosity.obter_tema_interesse_ou_memoria()
        self.assertIn(tema, self.curiosity.interesses_padrao)
        self.assertEqual(origem, "interesse_espontaneo")

    def test_obter_tema_neocortex(self):
        self.mock_brain.neocortex.add_node("fisica")
        self.mock_brain.neocortex.add_node("quantica")
        self.mock_brain.neocortex.add_edge("fisica", "quantica")

        tema, origem = self.curiosity.obter_tema_interesse_ou_memoria()
        self.assertEqual(origem, "neocortex")
        self.assertTrue("fisica" in tema or "quantica" in tema)

    @patch("requests.post")
    def test_pesquisa_criativa_sucesso(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"response": "Avanços em inteligência artificial"}
        mock_post.return_value = mock_resp

        self.mock_brain.pesquisar_conhecimento_externo.return_value = "[Artigo] Novas descobertas sobre IA"
        
        resultado = self.curiosity.pesquisa_criativa()
        
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado["tipo"], "criatividade")
        self.assertIn("descoberta", resultado)
        self.mock_brain.memorizar_experiencia.assert_called_once()

if __name__ == "__main__":
    unittest.main()
