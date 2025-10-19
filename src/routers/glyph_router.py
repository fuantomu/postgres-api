from src.database.helper.blizzard_parser import find_glyph
from src.models.response_model import BaseResponseModel, GlyphResponseModel
from src.routers.base_router import Router
from src.helper.glyphs import glyphs
from itertools import islice


class Glyph(Router):

    def __init__(self):
        super().__init__()

    def get(
        self,
        name: str = None,
        version: str = None,
        class_name: str = None,
        limit: int = 100,
    ) -> GlyphResponseModel | BaseResponseModel:
        if version:
            version = version.lower()

        result = []
        if name:
            result = [
                glyphs[glyph][version]
                for glyph in dict(
                    islice(glyphs.items(), len(glyphs.keys()) if limit == -1 else limit)
                )
                if name.lower()
                in glyphs[glyph].get(version, {}).get("name", "").lower()
            ]
            if class_name and len(result) == 0:
                glyph = find_glyph({"name": name}, version, class_name)
                result = [glyph] if glyph else []

        elif class_name:
            result = [
                glyphs[glyph][version]
                for glyph in dict(
                    islice(glyphs.items(), len(glyphs.keys()) if limit == -1 else limit)
                )
                if glyphs[glyph].get(version, {}).get("character_class") == class_name
            ]
        else:
            result = [
                glyphs[glyph][version]
                for glyph in dict(
                    islice(glyphs.items(), len(glyphs.keys()) if limit == -1 else limit)
                )
                if glyphs[glyph].get(version, {})
            ]
        unique_set = {tuple(sorted(d.items())) for d in result}
        return self.return_result([dict(t) for t in unique_set])
