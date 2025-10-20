from src.database.helper.blizzard_parser import GlyphParser
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
        id: str = None,
        version: str = None,
        class_name: str = None,
        type: str = None,
        limit: int = 100,
    ) -> GlyphResponseModel | BaseResponseModel:
        if version:
            version = version.lower()
        self.logger.info(f"Received GET request on {self.name}")
        self.logger.debug(
            f"name: {name}, id: {id}, version: {version}, class_name: {class_name}, type: {type}, limit: {limit}"
        )

        result = []
        glyph_parser = GlyphParser(version, class_name)
        if id:
            result = [
                glyphs[glyph][version]
                for glyph in dict(
                    islice(glyphs.items(), len(glyphs.keys()) if limit == -1 else limit)
                )
                if id == glyphs[glyph].get(version, {}).get("id", -1)
                and (glyphs[glyph].get("type") == type if type else 1)
            ]
            if class_name and len(result) == 0:
                result = [glyph_parser.find_glyph(id)]
        elif name:
            result = [
                glyph
                for glyph in glyph_parser.fetch_search(name, search_type="glyph")
                if glyph.get("type") == type
            ]

        elif class_name:
            result = [
                glyphs[glyph][version]
                for glyph in dict(
                    islice(glyphs.items(), len(glyphs.keys()) if limit == -1 else limit)
                )
                if glyphs[glyph].get(version, {}).get("character_class") == class_name
                and (glyphs[glyph].get("type") == type if type else 1)
            ]
            if len(result) == 0:
                result = glyph_parser.find_class_glyphs(class_name)
        else:
            result = [
                glyphs[glyph][version]
                for glyph in dict(
                    islice(glyphs.items(), len(glyphs.keys()) if limit == -1 else limit)
                )
                if glyphs[glyph].get(version, {})
                and (glyphs[glyph].get("type") == type if type else 1)
            ]
        return self.return_result(result)
