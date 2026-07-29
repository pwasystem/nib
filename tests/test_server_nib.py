import json
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from server_nib import app

class TestServerNIB(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_get_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("NIB - Neuro-Informatik Brain", response.text)

    def test_toggle_learning(self):
        response = self.client.post("/api/toggle-learning", json={"enabled": True})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertTrue(data["learning_enabled"])

        response_off = self.client.post("/api/toggle-learning", json={"enabled": False})
        self.assertFalse(response_off.json()["learning_enabled"])

    def test_set_custom_personality(self):
        response = self.client.post("/api/set-custom-personality", json={
            "o_pct": 85, "c_pct": 95, "e_pct": 50, "a_pct": 60, "n_pct": 10
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")

    def test_set_emotion(self):
        response = self.client.post("/api/set-emotion", json={"p": 50, "a": -20, "d": 40})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")

    def test_toggle_auto_emotion(self):
        response = self.client.post("/api/toggle-auto-emotion", json={"enabled": True})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["auto_mode"])

    def test_toggle_personality(self):
        response = self.client.post("/api/toggle-personality", json={"enabled": False})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["personality_enabled"])

    def test_toggle_emotion(self):
        response = self.client.post("/api/toggle-emotion", json={"enabled": False})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["emotion_enabled"])

    def test_kill_and_rebirth(self):
        response = self.client.post("/api/kill-and-rebirth")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("NIB (Neuro-Informatik Brain)", data["intro"])

    @patch("requests.get")
    def test_get_ollama_models(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"models": [{"name": "qwen2.5:3b"}, {"name": "llama3.1:8b"}]}
        mock_get.return_value = mock_resp

        response = self.client.get("/api/ollama-models")
        self.assertEqual(response.status_code, 200)
        self.assertIn("qwen2.5:3b", response.json()["models"])

    def test_set_ollama_model(self):
        response = self.client.post("/api/set-ollama-model", json={"model": "llama3.1:8b"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["current"], "llama3.1:8b")

    @patch("requests.post")
    def test_chat_stream_error(self, mock_post):
        mock_post.side_effect = Exception("Connection refused")
        response = self.client.get("/api/chat?prompt=ola")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Connection refused", response.text)

    @patch("requests.post")
    def test_chat_stream_success(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.iter_lines.return_value = [
            json.dumps({"response": "Ola! "}).encode("utf-8"),
            json.dumps({"response": "Como posso ajudar?"}).encode("utf-8")
        ]
        mock_post.return_value = mock_resp
        response = self.client.get("/api/chat?prompt=ola")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Ola! ", response.text)
        self.assertIn("[DONE]", response.text)

if __name__ == "__main__":
    unittest.main()
