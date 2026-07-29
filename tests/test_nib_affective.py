import unittest
from unittest.mock import patch, MagicMock
from nib_affective import NIBAffectiveCore

class TestNIBAffectiveCore(unittest.TestCase):
    def setUp(self):
        self.affective = NIBAffectiveCore(pleasure=0.2, arousal=-0.1, dominance=0.3)

    def test_initial_state(self):
        self.assertEqual(self.affective.pleasure, 0.2)
        self.assertEqual(self.affective.arousal, -0.1)
        self.assertEqual(self.affective.dominance, 0.3)
        self.assertFalse(self.affective.auto_mode)

    def test_set_pad_direct(self):
        self.affective.set_pad_direct(80, -60, 40)
        self.assertEqual(self.affective.pleasure, 0.8)
        self.assertEqual(self.affective.arousal, -0.6)
        self.assertEqual(self.affective.dominance, 0.4)

    def test_set_pad_direct_clamping(self):
        self.affective.set_pad_direct(150, -200, 50)
        self.assertEqual(self.affective.pleasure, 1.0)
        self.assertEqual(self.affective.arousal, -1.0)
        self.assertEqual(self.affective.dominance, 0.5)

    def test_temperature_modifier(self):
        self.affective.arousal = 1.0
        self.assertEqual(self.affective.get_temperature_modifier(), 0.75)

        self.affective.arousal = -1.0
        self.assertEqual(self.affective.get_temperature_modifier(), 0.1)

    def test_mood_instruction(self):
        self.affective.set_pad_direct(80, 60, 70)
        instruction = self.affective.get_mood_instruction()
        self.assertIn("entusiasmado", instruction)

    @patch("requests.post")
    def test_auto_emotion_reaction(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"response": '{"p": 0.8, "a": 0.5, "d": 0.6}'}
        mock_post.return_value = mock_resp

        self.affective.set_auto_mode(True)
        self.affective.reajustar_emocao_automatica("Estou muito feliz hoje!")

        # 0.7 * 0.2 + 0.3 * 0.8 = 0.14 + 0.24 = 0.38
        self.assertEqual(self.affective.pleasure, 0.38)

    @patch("requests.post")
    def test_auto_emotion_invalid_json(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"response": "Sem JSON válido aqui!"}
        mock_post.return_value = mock_resp

        self.affective.set_auto_mode(True)
        orig_p = self.affective.pleasure
        self.affective.reajustar_emocao_automatica("Olá")
        self.assertEqual(self.affective.pleasure, orig_p)

if __name__ == "__main__":
    unittest.main()
