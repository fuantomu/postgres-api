from src.models.ingredient_model import IngredientModel
from src.models.response_model import BaseResponseModel, IngredientResponseModel
from src.routers.base_router import Router


class Ingredient(Router):

    def __init__(self):
        super().__init__()
        self.router.add_api_route(
            "/",
            self.post,
            methods=["POST"],
            status_code=201,
            summary="Add a new or update an existing ingredient",
            response_model=BaseResponseModel,
            responses={400: {"model": BaseResponseModel}},
        )

    async def post(self, ingredient: IngredientModel, overwrite_alias: bool = False):
        self.logger.info(f"Received POST request on {self.name}")
        self.logger.debug(f"Parameters: {ingredient},{overwrite_alias}")
        request = ingredient.model_dump()
        request["overwrite_alias"] = overwrite_alias
        request.pop("id")
        for key in request.copy().keys():
            if request[key] is None:
                request.pop(key)
        return super().redirect_request("Post", request)

    def get(
        self, search_alias: bool = None, id: str = None, name: str = None
    ) -> IngredientResponseModel | BaseResponseModel:
        return super().redirect_request(
            "Get",
            {
                "key": "id" if id else "name",
                "value": id or name,
                "search_alias": search_alias or False,
            },
        )
