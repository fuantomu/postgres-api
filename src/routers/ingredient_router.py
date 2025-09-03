from fastapi import Response
from models.ingredient_model import IngredientModel
from routers.base_router import Router

class Ingredient(Router):
    
    def __init__(self):
        super().__init__()
        self.router.add_api_route("/GetAll", self.get_all, methods=["GET"])
        self.router.add_api_route("/GetRecipesByIngredient", self.get_recipes_by_ingredient, methods=["GET"])
        self.router.add_api_route("/Find", self.find, methods=["GET"])
        self.router.add_api_route("/Add", self.add, methods=["Post"])

    def get_all(self):
        self.logger.info(f"Received GET request on {self.name} - get_all")
        return super().get()
    
    def get_recipes_by_ingredient(self, ingredient: str):
        self.logger.info(f"Received GET request on {self.name} - get_recipes_by_ingredient")
        self.logger.info(f"Parameters: {ingredient}")
        return super().get()
    
    def find(self, name:str):
        self.logger.info(f"Received GET request on {self.name} - find")
        self.logger.info(f"Parameters: {name}")
        return super().get()
    
    async def add(self, ingredient: IngredientModel):
        self.logger.info(f"Received POST request on {self.name} - add")
        self.logger.info(f"Parameters: {ingredient}")
        return super().redirect_request(ingredient)
