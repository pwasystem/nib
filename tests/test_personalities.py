import unittest
from personalities.base import BasePersonalityTemplate
from personalities.custom_slider import CustomSliderPersonalityTemplate
from personality_factory import PersonalityFactory

class TestPersonalities(unittest.TestCase):
    def test_custom_slider_personality_clamping(self):
        p = CustomSliderPersonalityTemplate("Test", 150, -50, 40, 70, 20)
        traits = p.get_ocean_traits()
        self.assertEqual(traits["O"], 1.0)
        self.assertEqual(traits["C"], 0.0)
        self.assertEqual(traits["E"], 0.4)
        self.assertEqual(traits["A"], 0.7)
        self.assertEqual(traits["N"], 0.2)

    def test_system_instruction_generation(self):
        p = CustomSliderPersonalityTemplate("Analytical", 90, 95, 20, 30, 10)
        instruction = p.build_system_instruction()
        self.assertIn("Analytical", instruction)
        self.assertIn("precisão técnica", instruction)
        self.assertIn("conciso", instruction)
        self.assertIn("cético", instruction)
        self.assertIn("analogias ricas", instruction)

    def test_personality_factory(self):
        p1 = PersonalityFactory.create_personality("custom_slider", name="Custom", o_pct=80, c_pct=90, e_pct=40, a_pct=70, n_pct=20)
        self.assertIsInstance(p1, CustomSliderPersonalityTemplate)
        self.assertEqual(p1.name, "Custom")

        p2 = PersonalityFactory.create_personality("unknown_type")
        self.assertIsInstance(p2, CustomSliderPersonalityTemplate)
        self.assertEqual(p2.name, "Default")

if __name__ == "__main__":
    unittest.main()
