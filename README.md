# Requirements
* python 3.13.x
* pip install -r requirements.txt
* docker / postgres database (included in docker-compose)


## How to run
* create a .env.local file with your specific parameters
* python -m src.server
Default api frontend address is http://localhost:1440

## Endpoints:
### /api/Recipe/
* POST
* GET
* DELETE
### /api/Recipe/Ingredient
* DELETE
### /api/Recipe/ByIngredient
* GET
### /api/Ingredient/
* POST
* GET
* DELETE

## Tests
* python -m tests.api.api_tests
