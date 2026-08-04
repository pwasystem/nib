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

    def test_analisar_e_formular_busca_archive_org(self):
        servico, query_opt = self.brain.analisar_e_formular_busca("Busque no archive.org a versão antiga da Geocities")
        self.assertEqual(servico, "archive_org")
        self.assertIn("Geocities", query_opt)

    def test_analisar_e_formular_busca_academico(self):
        servico, query_opt = self.brain.analisar_e_formular_busca("Pesquise o artigo de física quântica sobre superposição")
        self.assertEqual(servico, "academico")
        self.assertIn("física quântica", query_opt)

    def test_analisar_e_formular_busca_wikipedia(self):
        servico, query_opt = self.brain.analisar_e_formular_busca("O que é a banda Black Sabbath")
        self.assertEqual(servico, "wikipedia")
        self.assertIn("Black Sabbath", query_opt)

    @patch("requests.get")
    def test_buscar_archive_org(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "response": {
                "docs": [
                    {
                        "title": "Geocities Archive 1999",
                        "description": "Coleção de sites da Geocities",
                        "identifier": "geocities_1999"
                    }
                ]
            }
        }
        mock_get.return_value = mock_resp
        res = self.brain.buscar_archive_org("geocities")
        self.assertTrue(len(res) > 0)
        self.assertIn("Archive.org", res[0])
        self.assertIn("Geocities Archive 1999", res[0])

    @patch.object(NeuroInformatikBrain, "memorizar_experiencia")
    @patch.object(NeuroInformatikBrain, "buscar_archive_org")
    def test_roteamento_direto_archive_org(self, mock_archive, mock_mem):
        mock_archive.return_value = ["[Archive.org] Título: Geocities Web Archive"]
        res = self.brain.pesquisar_conhecimento_externo("Pesquise no wayback a página antiga do Google")
        self.assertIn("Archive.org", res)
        mock_archive.assert_called_once()
        mock_mem.assert_called_once()

    @patch.object(NeuroInformatikBrain, "memorizar_experiencia")
    @patch.object(NeuroInformatikBrain, "buscar_archive_org")
    @patch.object(NeuroInformatikBrain, "buscar_tendencias_e_web")
    @patch.object(NeuroInformatikBrain, "buscar_noticias")
    @patch.object(NeuroInformatikBrain, "buscar_diretorio_academico")
    @patch.object(NeuroInformatikBrain, "buscar_wikipedia")
    def test_fallback_completo_para_web(self, mock_wiki, mock_acad, mock_noticias, mock_web, mock_archive, mock_mem):
        mock_wiki.return_value = []
        mock_archive.return_value = []
        mock_acad.return_value = []
        mock_noticias.return_value = []
        mock_web.return_value = ["[Tendências/Web]: Conteudo geral da web"]
        
        res = self.brain.pesquisar_conhecimento_externo("termo desconhecido")
        
        self.assertIn("Tendências/Web", res)
        mock_wiki.assert_called_once()
        mock_archive.assert_called_once()
        mock_acad.assert_called_once()
        mock_noticias.assert_called_once()
        mock_web.assert_called_once()
        mock_mem.assert_called_once()

if __name__ == "__main__":
    unittest.main()
