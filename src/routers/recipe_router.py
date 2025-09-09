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
        return super().redirect_request('GetRecipesByIngredient', {"key": "id" if id else "name", "value": id or ingredient})

    async def add(self, recipe: RecipeModel) -> str:
        self.logger.info(f"Received POST request on {self.name} - add")
        self.logger.debug(f"Parameters: {recipe}")
        return super().redirect_request('Add', recipe.model_dump())
    
    async def add_ingredient(self, ingredients: list[dict], id: str = None, recipe: str = None):
        self.logger.info(f"Received POST request on {self.name} - add_ingredient")
        self.logger.debug(f"Parameters: {recipe or id} - {ingredients}")
        return super().redirect_request('AddIngredient', {"key": "id" if id else "name", "value": id or recipe, "ingredients": ingredients})
    
    def get(self, id: str = None, name: str = None) -> list[RecipeModel]:
        return super().get(id=id, name= name)
