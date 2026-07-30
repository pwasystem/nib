from personalities.base import BasePersonalityTemplate
from personalities.custom_slider import CustomSliderPersonalityTemplate
from personalities.templates.zodiac_template import ZodiacTemplate
from personalities.templates.chinese_template import ChineseMatrixTemplate
from personalities.templates.preset_templates import PresetArchetypeTemplate
from personalities.templates.custom_manager import CustomPersonalityTemplate, CustomPersonalityStore
from personalities.chinese_matrix import ChineseMatrix60

class PersonalityFactory:
    """
    Gerenciador Central (Factory) de Templates de Personalidade e Modos Emocionais do NIB.
    """
    @staticmethod
    def create_personality(template_type: str, **kwargs) -> BasePersonalityTemplate:
        t_type = (template_type or "").lower().strip()

        if t_type == "custom_slider":
            return CustomSliderPersonalityTemplate(
                name=kwargs.get("name", "Custom"),
                o_pct=float(kwargs.get("o_pct", 80)),
                c_pct=float(kwargs.get("c_pct", 90)),
                e_pct=float(kwargs.get("e_pct", 40)),
                a_pct=float(kwargs.get("a_pct", 70)),
                n_pct=float(kwargs.get("n_pct", 20))
            )

        if t_type == "custom":
            t_id = kwargs.get("preset_key") or kwargs.get("id") or kwargs.get("template_id")
            store = CustomPersonalityStore.load_all()
            if t_id and t_id in store:
                data = store[t_id]
                return CustomPersonalityTemplate(
                    template_id=t_id,
                    name=data.get("name", "Custom"),
                    description=data.get("description", ""),
                    ocean=data.get("ocean", {}),
                    pad=data.get("pad", {}),
                    interests=data.get("interests", [])
                )

        if t_type == "zodiac":
            signo = kwargs.get("signo") or kwargs.get("name") or "Virgem"
            return ZodiacTemplate(signo=signo)

        if t_type == "chinese_matrix" or t_type == "chinese":
            animal = kwargs.get("animal") or "dragao"
            elemento = kwargs.get("elemento") or "madeira"
            return ChineseMatrixTemplate(animal=animal, elemento=elemento)

        if t_type == "preset":
            preset_key = kwargs.get("preset_key") or kwargs.get("name") or "stoic_mentor"
            return PresetArchetypeTemplate(preset_key=preset_key)

        # Fallback padrão equilibrado/analítico
        return CustomSliderPersonalityTemplate("Default", 80, 90, 40, 70, 20)

    @staticmethod
    def list_available_templates() -> dict:
        """Retorna todos os templates e presets disponíveis organizados por categoria."""
        zodiac_signos = [
            "Aries", "Touro", "Gemeos", "Cancer", 
            "Leao", "Virgem", "Libra", "Escorpiao", 
            "Sagitario", "Capricornio", "Aquario", "Peixes"
        ]
        
        presets = []
        for key, pinfo in PresetArchetypeTemplate.PRESETS.items():
            presets.append({
                "id": key,
                "type": "preset",
                "name": pinfo["name"],
                "description": pinfo["desc"],
                "interests": pinfo.get("interests", [])
            })

        custom_store = CustomPersonalityStore.load_all()
        custom_list = []
        for cid, cinfo in custom_store.items():
            custom_list.append({
                "id": cid,
                "type": "custom",
                "name": cinfo["name"],
                "description": cinfo.get("description", ""),
                "ocean": cinfo.get("ocean", {}),
                "pad": cinfo.get("pad", {}),
                "interests": cinfo.get("interests", [])
            })

        zodiac_list = []
        for signo in zodiac_signos:
            zt = ZodiacTemplate(signo)
            zodiac_list.append({
                "id": f"zodiac_{signo.lower()}",
                "type": "zodiac",
                "signo": signo,
                "name": f"Zodíaco - {signo}",
                "description": zt.get_description(),
                "interests": zt.get_interests()
            })

        chinese_list = []
        for anim, elem in ChineseMatrix60.listar_todas_60_personalidades():
            ct = ChineseMatrixTemplate(anim, elem)
            chinese_list.append({
                "id": f"chinese_{anim}_{elem}",
                "type": "chinese_matrix",
                "animal": anim,
                "elemento": elem,
                "name": f"Chinês - {anim.capitalize()} de {elem.capitalize()}",
                "description": ct.get_description(),
                "interests": ct.get_interests()
            })

        return {
            "custom": custom_list,
            "presets": presets,
            "zodiac": zodiac_list,
            "chinese_matrix": chinese_list
        }