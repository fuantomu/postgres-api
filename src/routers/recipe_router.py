from src.models.recipe_model import DeleteIngredientsModel, RecipeModel
from src.models.response_model import BaseResponseModel, RecipeResponseModel
from src.routers.base_router import Router

class Recipe(Router):
    
    def __init__(self):
        super().__init__()
        self.router.add_api_route("/", self.post, methods=["POST"], status_code=201, summary="Add a new or update an existing recipe", response_model=BaseResponseModel, responses={400: {"model": BaseResponseModel}})
        self.router.add_api_route("/RecipesByIngredient", self.get_recipes_by_ingredient, methods=["GET"], status_code=202, summary="Get recipes that include a given ingredient", responses={400: {"model": BaseResponseModel}})
        self.router.add_api_route("/RecipeIngredients", self.delete_recipe_ingredients, methods=["DELETE"], status_code=200,  summary="Delete one or more ingredient from a recipe", response_model=BaseResponseModel, responses={400: {"model": BaseResponseModel}})
        
    def get_recipes_by_ingredient(self, ingredient_id: str = None, ingredient: str = None, include_alias : bool = False) -> RecipeResponseModel | BaseResponseModel:
        self.logger.info(f"Received GET request on {self.name} - get_recipes_by_ingredient")
        self.logger.debug(f"Parameters: {ingredient or ingredient_id}")
        if not ingredient_id and not ingredient:
            return super().missing_parameters(["ingredient_id","ingredient"])
        return super().redirect_request('RecipesByIngredient', {"key": "id" if ingredient_id else "name", "value": ingredient_id or ingredient, "include_alias": include_alias})
    
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
    
    def delete_recipe_ingredients(self, ingredients: list[DeleteIngredientsModel], id: str = None, name: str = None):
        self.logger.info(f"Received DELETE request on {self.name} - delete_recipe_ingredients")
        self.logger.debug(f"Parameters: {name or id},{ingredients}")
        if not id and not name:
            return super().missing_parameters(["id","name"])
        ingredients = [ingredient.model_dump() for ingredient in ingredients]
        return super().redirect_request('DeleteIngredients', {"key": "id" if id else "name", "value": id or name, "ingredients": ingredients})

    def get(self, id: str = None, name: str = None) -> RecipeResponseModel:
        return super().redirect_request('Get', {"key": "id" if id else "name", "value": id or name})
