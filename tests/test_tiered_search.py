import unittest
from unittest.mock import MagicMock, patch

from nib_brain import NeuroInformatikBrain

class TestTieredSearch(unittest.TestCase):
    @patch("chromadb.PersistentClient")
    def setUp(self, mock_chroma):
        self.mock_chroma_client = MagicMock()
        mock_chroma.return_value = self.mock_chroma_client
        self.brain = NeuroInformatikBrain()

    @patch.object(NeuroInformatikBrain, "memorizar_experiencia")
    @patch.object(NeuroInformatikBrain, "buscar_tendencias_e_web")
    @patch.object(NeuroInformatikBrain, "buscar_noticias")
    @patch.object(NeuroInformatikBrain, "buscar_diretorio_academico")
    def test_tier_1_academico_sucesso(self, mock_acad, mock_noticias, mock_web, mock_mem):
        mock_acad.return_value = ["[Artigo arXiv] Título: IA em Saúde"]
        
        res = self.brain.pesquisar_conhecimento_externo("inteligencia artificial")
        
        self.assertIn("arXiv", res)
        mock_acad.assert_called_once()
        mock_noticias.assert_not_called()
        mock_web.assert_not_called()
        mock_mem.assert_called_once()

    @patch.object(NeuroInformatikBrain, "memorizar_experiencia")
    @patch.object(NeuroInformatikBrain, "buscar_tendencias_e_web")
    @patch.object(NeuroInformatikBrain, "buscar_noticias")
    @patch.object(NeuroInformatikBrain, "buscar_diretorio_academico")
    def test_tier_2_noticias_fallback(self, mock_acad, mock_noticias, mock_web, mock_mem):
        mock_acad.return_value = []
        mock_noticias.return_value = ["[Notícia]: Lançado novo modelo de IA"]
        
        res = self.brain.pesquisar_conhecimento_externo("novo modelo ia")
        
        self.assertIn("Notícia", res)
        mock_acad.assert_called_once()
        mock_noticias.assert_called_once()
        mock_web.assert_not_called()
        mock_mem.assert_called_once()

    @patch.object(NeuroInformatikBrain, "memorizar_experiencia")
    @patch.object(NeuroInformatikBrain, "buscar_tendencias_e_web")
    @patch.object(NeuroInformatikBrain, "buscar_noticias")
    @patch.object(NeuroInformatikBrain, "buscar_diretorio_academico")
    def test_tier_3_tendencias_web_fallback(self, mock_acad, mock_noticias, mock_web, mock_mem):
        mock_acad.return_value = []
        mock_noticias.return_value = []
        mock_web.return_value = ["[Tendências/Web]: Tendências tecnológicas de 2026"]
        
        res = self.brain.pesquisar_conhecimento_externo("tendencias tech")
        
        self.assertIn("Tendências/Web", res)
        mock_acad.assert_called_once()
        mock_noticias.assert_called_once()
        mock_web.assert_called_once()
        mock_mem.assert_called_once()

if __name__ == "__main__":
    unittest.main()
