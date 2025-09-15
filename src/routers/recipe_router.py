from src.models.recipe_model import RecipeModel
from src.models.response_model import BaseResponseModel, RecipeResponseModel
from src.routers.base_router import Router

class Recipe(Router):
    
    def __init__(self):
        super().__init__()
        self.router.add_api_route("/", self.post, methods=["POST"], status_code=201, summary="Add a new or update an existing recipe", response_model=BaseResponseModel, responses={400: {"model": BaseResponseModel}})
        self.router.add_api_route("/GetRecipesByIngredient", self.get_recipes_by_ingredient, methods=["GET"], status_code=202, summary="Get recipes that include a given ingredient", responses={400: {"model": BaseResponseModel}})
        
    def get_recipes_by_ingredient(self, ingredient_id: str = None, ingredient: str = None, include_alias : bool = False):
        self.logger.info(f"Received GET request on {self.name} - get_recipes_by_ingredient")
        self.logger.debug(f"Parameters: {ingredient or ingredient_id}")
        if not ingredient_id and not ingredient:
            return super().missing_parameters(["ingredient_id","ingredient"])
        return super().redirect_request('GetRecipesByIngredient', {"key": "id" if ingredient_id else "name", "value": ingredient_id or ingredient, "include_alias": include_alias})
    
    async def post(self, recipe: RecipeModel, overwrite_ingredients: bool = False):
        self.logger.info(f"Received POST request on {self.name}")
        self.logger.debug(f"Parameters: {recipe},{overwrite_ingredients}")
        request = recipe.model_dump()
        request["overwrite_ingredients"] = overwrite_ingredients
        request.pop("id")
        for key in request.copy().keys():
            if request[key] is None:
                request.pop(key)
        return super().redirect_request('Post', request)

    def get(self, id: str = None, name: str = None) -> RecipeResponseModel:
        return super().redirect_request('Get', {"key": "id" if id else "name", "value": id or name})
