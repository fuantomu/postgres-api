from src.database.tables.table import Table

class IngredientTable(Table):
    columns = {
        "id": {
            "value": "UUID NOT NULL",
            "default": "uuid_generate_v1()"
        },
        "name": {
            "value": "varchar(80) UNIQUE NOT NULL",
            "default": ""
        },
        "description": {
            "value": "TEXT",
            "default": ""
        },
        "alias": {
            "value": "TEXT[]",
            "default": ""
        },
        "PRIMARY KEY": {
            "value": "(id)",
            "default": ""
        }
    }

    def update_alias(self, request: dict):
        ingredient = self.format_result(self.select("ALL", [("id","=",request['id'])], "ingredient"))[0]
        alias_list = [alias for alias in request['alias']]

        for alias in alias_list:
            if alias == ingredient["name"]:
                alias_list.remove(alias)
                self.logger.warning(f"'{alias}' is the same name as the Ingredient. Removing from request")

        if ingredient.get("alias"):
            alias_list.extend(ingredient['alias'])
            alias_list = list(set(alias_list))

        return alias_list
    
    def get(self, request : str|dict):
        if not request["value"]:
            return Table.get(self, request)
        if not request["search_alias"]:
            return self.format_result(self.select("ALL", [(request["key"],"=",request["value"])]))
        
        results = []
        selection = [(request["key"],"=",request["value"])]
        if request['key'] == 'name':
            selection.extend([('alias',"@>",[request['value']])])
        else:
            ingredient_name = self.select("name", [('id','=',request['value'])])
            if len(ingredient_name) > 0:
                selection.extend([('alias',"@>",[ingredient_name[0]])])
        selection.extend(["OR"])
        results = self.format_result(self.select("ALL", selection))
        
        return results
    
    def insert(self, request: dict) -> str:
        request.pop("overwrite_alias", None)
        if request.get("alias"):
            for alias in request.get('alias',[]):
                if alias == request["name"]:
                    request["alias"].remove(alias)
                    self.logger.warning(f"'{alias}' is the same name as the Ingredient. Removing from request")
                
        return super().insert(request)
    
    def update(self, request: dict, where = None, table_name = None, return_key = "id"):
        if not request["overwrite_alias"]:
            request['alias'] = self.update_alias(request)
        request.pop("overwrite_alias")
        return super().update(request, where, "ingredient")

    def update_functions(self):
        self.logger.debug(f"Updating function calls for {self.name}")
        self.set_function("Get", self.get)
        self.set_function("Post", self.add_or_update)

    