from personalities.base import BasePersonalityTemplate
from personalities.custom_slider import CustomSliderPersonalityTemplate

class PersonalityFactory:
    """
    Gerenciador Central (Factory) de Templates de Personalidade do NIB.
    """
    @staticmethod
    def create_personality(template_type: str, **kwargs) -> BasePersonalityTemplate:
        template_type = template_type.lower()

        if template_type == "custom_slider":
            return CustomSliderPersonalityTemplate(
                name=kwargs.get("name", "Custom"),
                o_pct=float(kwargs.get("o_pct", 80)),
                c_pct=float(kwargs.get("c_pct", 90)),
                e_pct=float(kwargs.get("e_pct", 40)),
                a_pct=float(kwargs.get("a_pct", 70)),
                n_pct=float(kwargs.get("n_pct", 20))
            )

        # Fallback padrão equilibrado/analítico
        return CustomSliderPersonalityTemplate("Default", 80, 90, 40, 70, 20)