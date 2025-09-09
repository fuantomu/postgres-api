from models.recipe_ingredients_model import RecipeIngredientModel
from models.recipe_model import RecipeModel
from routers.base_router import Router

class Recipe(Router):
    
    def __init__(self):
        super().__init__()
        self.router.add_api_route("/", self.add, methods=["POST"], status_code=201)
        self.router.add_api_route("/GetRecipesByIngredient", self.get_recipes_by_ingredient, methods=["GET"], status_code=202)
        self.router.add_api_route("/AddIngredients", self.add_ingredient, methods=["POST"], status_code=201)
        
    def get_recipes_by_ingredient(self, id: str = None, ingredient: str = None):
        self.logger.info(f"Received GET request on {self.name} - get_recipes_by_ingredient")
        self.logger.debug(f"Parameters: {ingredient or id}")
        if not id and not ingredient:
            return super().missing_parameters(["id","ingredient"])
        return super().redirect_request('GetRecipesByIngredient', {"key": "id" if id else "name", "value": id or ingredient})

    async def add(self, recipe: RecipeModel) -> str:
        self.logger.info(f"Received POST request on {self.name} - add")
        self.logger.debug(f"Parameters: {recipe}")
        recipe.__delattr__("id")
        return super().redirect_request('Add', recipe.model_dump())
    
    async def add_ingredient(self, ingredients: list[RecipeIngredientModel], id: str = None, recipe: str = None):
        self.logger.info(f"Received POST request on {self.name} - add_ingredient")
        self.logger.debug(f"Parameters: {recipe or id} - {ingredients}")
        if not id and not recipe:
            return super().missing_parameters(["id","recipe"])
        return super().redirect_request('AddIngredient', {"key": "id" if id else "name", "value": id or recipe, "ingredients": [ingredient.dict() for ingredient in ingredients]})
    
    def get(self, id: str = None, name: str = None) -> list[RecipeModel]:
        return super().get(id=id, name= name)
