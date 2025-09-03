from fastapi import Response
from models.recipe_model import RecipeModel
from routers.base_router import Router

class Recipe(Router):
    
    def __init__(self):
        super().__init__()
        self.router.add_api_route("/GetAll", self.get_all, methods=["GET"])
        self.router.add_api_route("/Find", self.find, methods=["GET"])
        self.router.add_api_route("/Add", self.add, methods=["POST"])

    def get_all(self):
        self.logger.info(f"Received GET request on {self.name} - get_all")
        return super().get()
    
    def find(self, name:str):
        self.logger.info(f"Received GET request on {self.name} - find")
        self.logger.info(f"Parameters: {name}")
        return super().get()
    
    async def add(self, recipe: RecipeModel):
        self.logger.info(f"Received POST request on {self.name} - add")
        self.logger.info(f"Parameters: {recipe}")
        return super().redirect_request(recipe)
