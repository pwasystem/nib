import unittest
from unittest.mock import MagicMock, patch

from nib_brain import NeuroInformatikBrain

class TestSearchTriggers(unittest.TestCase):
    @patch("chromadb.PersistentClient")
    def setUp(self, mock_chroma):
        self.mock_chroma_client = MagicMock()
        mock_chroma.return_value = self.mock_chroma_client
        self.brain = NeuroInformatikBrain()

    def test_solicitou_pesquisa_ou_correcao_positivos(self):
        frases_positivas = [
            "Não é essa NIB, busque native in black",
            "Você está errado sobre a fórmula",
            "Pesquise sobre quantum computing",
            "Está incorreto, corrija isso",
            "Busque mais informações na internet"
        ]
        for f in frases_positivas:
            self.assertTrue(self.brain.solicitou_pesquisa_ou_correcao(f), f"Falhou para: {f}")

    def test_solicitou_pesquisa_ou_correcao_negativos(self):
        frases_negativas = [
            "Olá NIB, como você está?",
            "Qual é a capital da França?",
            "Explique o que é uma função em Python"
        ]
        for f in frases_negativas:
            self.assertFalse(self.brain.solicitou_pesquisa_ou_correcao(f), f"Falhou para: {f}")

    @patch.object(NeuroInformatikBrain, "pesquisar_conhecimento_externo")
    def test_resgatar_memoria_forca_pesquisa(self, mock_pesquisar):
        mock_pesquisar.return_value = "[Web Result]: Native in Black e uma musica do Black Sabbath."
        
        # Simula resposta mesmo com contexto presente
        res = self.brain.resgatar_memoria_relevante("Não é essa NIB, busque native in black")
        
        mock_pesquisar.assert_called_once_with("Não é essa NIB, busque native in black", apenas_academico=False)
        self.assertIn("Pesquisa Web", res)

    def test_solicitou_aprendizado_ou_memoria_conversas_passadas(self):
        frases_conversas = [
            "Olá, você tem a memória de alguma conversa passada?",
            "Você se lembra de mim?",
            "O que conversamos na sessão anterior?",
            "Já conversamos antes sobre esse assunto?",
            "Qual o histórico das nossas conversas passadas?"
        ]
        for f in frases_conversas:
            self.assertTrue(self.brain.solicitou_aprendizado_ou_memoria(f), f"Falhou para gatilho de conversa passada: {f}")

if __name__ == "__main__":
    unittest.main()
