from models.ingredient_model import IngredientModel
from routers.base_router import Router

class Ingredient(Router):
    
    def __init__(self):
        super().__init__()
        self.router.add_api_route("/", self.add, methods=["POST"], status_code=201)
        
    
    async def add(self, ingredient: IngredientModel):
        self.logger.info(f"Received POST request on {self.name} - add")
        self.logger.info(f"Parameters: {ingredient}")
        return super().redirect_request('Add', ingredient)
