import unittest
from unittest.mock import MagicMock, patch

from nib_brain import NeuroInformatikBrain

class TestTieredSearch(unittest.TestCase):
    @patch("chromadb.PersistentClient")
    def setUp(self, mock_chroma):
        self.mock_chroma_client = MagicMock()
        mock_chroma.return_value = self.mock_chroma_client
        self.brain = NeuroInformatikBrain()

    def test_extrair_termo_busca(self):
        query = "Não é essa NIB, busque native in black"
        termo = self.brain.extrair_termo_busca(query)
        self.assertIn("native in black", termo)

    def test_eh_termo_cientifico(self):
        self.assertTrue(self.brain.eh_termo_cientifico("física quântica"))
        self.assertTrue(self.brain.eh_termo_cientifico("algoritmos e estrutura de dados"))
        self.assertFalse(self.brain.eh_termo_cientifico("NIB Black Sabbath"))

    @patch.object(NeuroInformatikBrain, "memorizar_experiencia")
    @patch.object(NeuroInformatikBrain, "buscar_wikipedia")
    @patch.object(NeuroInformatikBrain, "buscar_diretorio_academico")
    def test_tier_1_wikipedia_sucesso_termo_geral(self, mock_acad, mock_wiki, mock_mem):
        mock_wiki.return_value = ["[Wikipedia PT] Título: N.I.B. | Resumo: Musica do Black Sabbath"]
        
        res = self.brain.pesquisar_conhecimento_externo("NIB Black Sabbath")
        
        self.assertIn("Wikipedia", res)
        mock_wiki.assert_called_once()
        mock_acad.assert_not_called()
        mock_mem.assert_called_once()

    @patch.object(NeuroInformatikBrain, "memorizar_experiencia")
    @patch.object(NeuroInformatikBrain, "buscar_wikipedia")
    @patch.object(NeuroInformatikBrain, "buscar_diretorio_academico")
    def test_termo_cientifico_inicia_busca_academica(self, mock_acad, mock_wiki, mock_mem):
        mock_acad.return_value = ["[Artigo arXiv] Título: Física Quântica Avançada"]
        
        res = self.brain.pesquisar_conhecimento_externo("física quântica")
        
        self.assertIn("arXiv", res)
        mock_acad.assert_called_once()
        mock_wiki.assert_not_called()
        mock_mem.assert_called_once()

    @patch.object(NeuroInformatikBrain, "memorizar_experiencia")
    @patch.object(NeuroInformatikBrain, "buscar_tendencias_e_web")
    @patch.object(NeuroInformatikBrain, "buscar_noticias")
    @patch.object(NeuroInformatikBrain, "buscar_diretorio_academico")
    @patch.object(NeuroInformatikBrain, "buscar_wikipedia")
    def test_fallback_completo_para_web(self, mock_wiki, mock_acad, mock_noticias, mock_web, mock_mem):
        mock_wiki.return_value = []
        mock_acad.return_value = []
        mock_noticias.return_value = []
        mock_web.return_value = ["[Tendências/Web]: Conteudo geral da web"]
        
        res = self.brain.pesquisar_conhecimento_externo("termo totalmente desconhecido")
        
        self.assertIn("Tendências/Web", res)
        mock_wiki.assert_called_once()
        mock_acad.assert_called_once()
        mock_noticias.assert_called_once()
        mock_web.assert_called_once()
        mock_mem.assert_called_once()

if __name__ == "__main__":
    unittest.main()
