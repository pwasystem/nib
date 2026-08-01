import unittest
import os
import settings_manager

class TestSettingsManager(unittest.TestCase):
    def test_save_and_load_settings(self):
        settings_manager.update_setting("ollama_model", "test_model:latest")
        settings_manager.update_setting("memory_mode", "perfect")
        settings_manager.update_setting("learning_enabled", True)
        
        st = settings_manager.load_settings()
        self.assertEqual(st.get("ollama_model"), "test_model:latest")
        self.assertEqual(st.get("memory_mode"), "perfect")
        self.assertTrue(st.get("learning_enabled"))

if __name__ == "__main__":
    unittest.main()
