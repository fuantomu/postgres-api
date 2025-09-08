from database.tables.table import Table

class IngredientTable(Table):
    columns = {
        "id": {
            "value": "UUID NOT NULL PRIMARY KEY",
            "default": "uuid_generate_v1()"
        },
        "name": {
            "value": "TEXT UNIQUE NOT NULL",
            "default": ""
        },
        "description": {
            "value": "TEXT",
            "default": ""
        },
        "alias": {
            "value": "TEXT",
            "default": ""
        }
    }

    