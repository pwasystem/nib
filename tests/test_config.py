import os
import unittest
import config

class TestConfig(unittest.TestCase):
    def test_config_paths(self):
        self.assertTrue(os.path.isabs(config.BASE_DIR))
        self.assertTrue(os.path.isabs(config.STORAGE_DIR))
        self.assertTrue(os.path.isabs(config.HIPPOCAMPUS_DIR))
        self.assertTrue(os.path.isabs(config.NEOCORTEX_FILE))
        self.assertTrue(os.path.isabs(config.SYNAPTIC_JOURNAL))
        
        self.assertTrue(os.path.exists(config.STORAGE_DIR))
        self.assertTrue(os.path.exists(config.HIPPOCAMPUS_DIR))

    def test_config_ollama_settings(self):
        self.assertIsInstance(config.OLLAMA_URL, str)
        self.assertIsInstance(config.OLLAMA_MODEL, str)

if __name__ == "__main__":
    unittest.main()
