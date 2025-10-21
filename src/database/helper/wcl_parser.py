from dotenv import load_dotenv
import requests
from os import getenv


class WCLParser:
    def __init__(self, version):
        self.version = version
        self.token = self.get_wcl_oauth()
        self.endpoint = f"https://{version}.warcraftlogs.com/api/v2/client"

    def get_wcl_oauth(self):
        url = f"https://{self.version}.warcraftlogs.com/oauth/token"
        result = requests.post(
            url,
            data={"grant_type": "client_credentials"},
            auth=requests.auth.HTTPBasicAuth(
                getenv("WCL_CLIENT_ID"), getenv("WCL_CLIENT_SECRET")
            ),
        )
        if result.status_code != 200:
            raise Exception(result.text)
        else:
            return result.json().get("access_token")

    def get_schema(self, schema: str) -> str:
        try:
            with open(f"src/database/helper/schemas/{schema}.graphql", "r") as f:
                return f.read()
        except Exception as e:
            raise e

    def get_character(self, character: str, server: str, region: str):
        body = (
            self.get_schema("character")
            .replace("$NAME", character)
            .replace("$SERVER", server)
            .replace("$REGION", region)
        )
        result = requests.get(
            self.endpoint,
            json={"query": body},
            headers={"Authorization": f"Bearer {self.token}"},
        )
        if result.status_code != 200:
            raise Exception(result.text)
        else:
            return result.json()["data"]["characterData"]["character"]

    def get_zone(self, zone: int):
        body = self.get_schema("zone").replace("$ID", str(zone))
        result = requests.get(
            self.endpoint,
            json={"query": body},
            headers={"Authorization": f"Bearer {self.token}"},
        )
        if result.status_code != 200:
            raise Exception(result.text)
        else:
            return result.json()["data"]["worldData"]["zone"]


if __name__ == "__main__":
    load_dotenv(".env")
    load_dotenv(".env.local", override=True)
    test = WCLParser("classic")
    # out = test.get_character("heavenstamp", "everlook", "eu")
    out = test.get_zone(1040)
    print(out)
