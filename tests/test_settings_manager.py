import unittest
import tempfile
import os
from unittest.mock import patch
import settings_manager

class TestSettingsManager(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w", encoding="utf-8")
        self.temp_file.write("{}")
        self.temp_file.close()

    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            try:
                os.remove(self.temp_file.name)
            except Exception:
                pass

    def test_save_and_load_settings(self):
        with patch.object(settings_manager, "SETTINGS_FILE", self.temp_file.name):
            settings_manager.update_setting("ollama_model", "test_model:latest")
            settings_manager.update_setting("memory_mode", "perfect")
            settings_manager.update_setting("learning_enabled", True)
            
            st = settings_manager.load_settings()
            self.assertEqual(st.get("ollama_model"), "test_model:latest")
            self.assertEqual(st.get("memory_mode"), "perfect")
            self.assertTrue(st.get("learning_enabled"))

if __name__ == "__main__":
    unittest.main()
