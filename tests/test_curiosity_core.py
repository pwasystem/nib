import unittest
from unittest.mock import MagicMock, patch
import networkx as nx
from curiosity_core import CuriosityCore

class TestCuriosityCoreOriginal(unittest.TestCase):
    def setUp(self):
        self.mock_brain = MagicMock()
        self.mock_brain.learning_enabled = True
        self.mock_brain.neocortex = nx.DiGraph()
        self.curiosity = CuriosityCore(self.mock_brain)

    def test_learning_disabled(self):
        self.mock_brain.learning_enabled = False
        self.assertIsNone(self.curiosity.investigar_lacunas())

    @patch("curiosity_core.CuriosityCore.pesquisa_criativa")
    def test_no_lacunas_triggers_criatividade(self, mock_criatividade):
        mock_criatividade.return_value = {"tipo": "criatividade", "tema": "IA"}
        res = self.curiosity.investigar_lacunas()
        self.assertEqual(res["tipo"], "criatividade")
        mock_criatividade.assert_called_once()

    @patch("curiosity_core.CuriosityCore.pesquisar_web")
    def test_lacuna_found_and_learned(self, mock_pesquisa):
        mock_pesquisa.return_value = "Python e uma linguagem de programação."
        self.mock_brain.neocortex.add_node("python")

        res = self.curiosity.investigar_lacunas()
        self.assertIsNotNone(res)
        self.assertEqual(res["conceito"], "python")
        self.assertEqual(res["descoberta"], "Python e uma linguagem de programação.")
        self.mock_brain.memorizar_experiencia.assert_called_once()

if __name__ == "__main__":
    unittest.main()
