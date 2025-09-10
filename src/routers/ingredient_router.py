from models.ingredient_model import IngredientAliasModel, IngredientModel
from routers.base_router import Router

class Ingredient(Router):
    
    def __init__(self):
        super().__init__()
        self.router.add_api_route("/", self.add, methods=["POST"], status_code=201)
        self.router.add_api_route("/Alias", self.add_alias, methods=["POST"], status_code=201)
        
    async def add(self, ingredient: IngredientModel)-> str:
        self.logger.info(f"Received POST request on {self.name} - add")
        self.logger.debug(f"Parameters: {ingredient}")
        ingredient.__delattr__("id")
        return super().redirect_request('Add', ingredient.model_dump())
    
    async def add_alias(self, alias: list[IngredientAliasModel], id: str|None = None, name: str|None = None)-> str:
        self.logger.info(f"Received POST request on {self.name} - add_alias")
        self.logger.debug(f"Parameters: {id or name} - {alias}")
        if not id and not name:
            return super().missing_parameters(["id","name"])
        return super().redirect_request('Alias', {"key": "id" if id else "name", "value": id or name, "alias": [_alias.model_dump() for _alias in alias]})
    
    def get(self, id: str = None, name: str = None) -> list[IngredientModel]:
        return super().get(id=id, name= name)
