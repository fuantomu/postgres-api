import base64
from datetime import datetime, timezone
from src.database.helper.hash import verify_hash
from src.database.tables.account_character_table import AccountCharacterTable
from src.database.tables.table import Table

DEFAULT_TIMEOUT = 3600


class AccountTable(Table):
    columns = {
        "id": {"value": "BIGSERIAL UNIQUE", "default": ""},
        "username": {
            "value": "CITEXT UNIQUE NOT NULL",
            "default": "",
        },
        "hash": {"value": "TEXT NOT NULL", "default": ""},
        "level": {"value": "SMALLINT NOT NULL", "default": 0},
        "guild": {"value": "INTEGER REFERENCES guild(id)", "default": None},
        "creation_time": {"value": "BIGINT NOT NULL", "default": 0},
        "PRIMARY KEY": {"value": "(id)", "default": ""},
    }

    def get(self, request: str | dict):
        if not request["username"]:
            found_items = self.format_result(self.select("ALL"))
            for item in found_items:
                found_characters = self.select(
                    "character_id",
                    [("account_id", "=", item["id"])],
                    "accountcharacter",
                )
                item["characters"] = [char[0] for char in found_characters]
                item.pop("hash", None)
                if not item.get("guild"):
                    item["guild"] = -1
            return found_items
        else:
            found_item = self.select("ALL", [("username", "=", request["username"])])

        if not found_item:
            raise Exception(f"No user found for name '{request['username']}'")
        result = self.format_result(found_item)[0]

        found_characters = self.select(
            "character_id", [("account_id", "=", found_item[0][0])], "accountcharacter"
        )
        result["characters"] = [char[0] for char in found_characters]

        result.pop("hash", None)
        if not result.get("guild"):
            result["guild"] = -1
        return result

    def delete_entry(self, request):
        found_user = self.select(
            "username",
            [
                ("username", "=", request["username"]),
            ],
        )
        if len(found_user) == 0:
            raise Exception(f"No user found for name '{request['name']}'")

        return super().delete_entry(request)

    def register(self, request):
        found_user = self.select(
            "id",
            [
                ("username", "=", request["username"]),
            ],
        )
        if found_user:
            raise Exception(
                f"Account with username '{request['username']}' already exists"
            )

        if request["guild"] == -1:
            request["guild"] = None

        characters: list[int] = request.pop("characters", [])

        request["creation_time"] = datetime.now(timezone.utc).timestamp()
        id = self.insert(
            request,
            "account",
        )

        for character in characters:
            AccountCharacterTable.insert(
                self,
                {"account_id": id, "character_id": character},
                "accountcharacter",
                "account_id",
            )
        return f"{request['username']}"

    def update_account(self, request):
        found_user = self.select(
            "id",
            [
                ("username", "=", request["username"]),
            ],
        )

        if len(found_user) == 0:
            raise Exception(f"No user found for name '{request['name']}'")

        if request["guild"] == -1:
            request["guild"] = None

        characters: list[int] = request.pop("characters", [])

        self.update(request, [("id", "=", found_user[0][0])], "account")
        existing_characters = AccountCharacterTable.select(
            self,
            "character_id",
            [("account_id", "=", found_user[0][0])],
            "accountcharacter",
        )
        for _character in existing_characters:
            if _character[0] not in characters:
                AccountCharacterTable.delete_entry(
                    self,
                    {"account_id": found_user[0][0], "character_id": _character[0]},
                )
            elif _character[0] in characters:
                characters.remove(_character[0])
        for character in characters:
            AccountCharacterTable.insert(
                self,
                {"account_id": found_user[0][0], "character_id": character},
                "accountcharacter",
                "account_id",
            )
        return "Success"

    def login(self, request):
        found_user = self.select(
            "hash",
            [
                ("username", "=", request["username"]),
            ],
        )

        if not found_user:
            raise Exception("Account or password is incorrect")

        correct_login = verify_hash(request["hash"], found_user[0][0])
        if not correct_login:
            raise Exception("Account or password is incorrect")
        session = base64.b64encode(
            f"{request['username']}{datetime.now(timezone.utc).timestamp()}".encode(
                "utf-8"
            )
        ).decode("utf-8")
        self.sessions[session] = (
            datetime.now(timezone.utc).timestamp() + DEFAULT_TIMEOUT,
            request["username"],
        )
        return {"session": session, "timeout": DEFAULT_TIMEOUT}

    def get_session(self, request: str | dict):
        found_session = self.sessions.get(request["session"])

        if not found_session:
            raise Exception("No session found")

        if datetime.now(timezone.utc).timestamp() > found_session[0]:
            self.sessions.pop(request["session"])
            raise Exception("Session no longer valid")

        return {
            "timeout": int(found_session[0] - datetime.now(timezone.utc).timestamp()),
            "username": found_session[1],
        }

    def get_characters(self, request: str | dict):
        found_user = self.select(
            "id",
            [
                ("username", "=", request["username"]),
            ],
        )
        if len(found_user) == 0:
            raise Exception(f"No user found for name '{request['name']}'")

        found_characters = self.select(
            "character_id",
            [("account_id", "=", found_user[0][0])],
            "accountcharacter",
        )

        return [char[0] for char in found_characters]

    def update_functions(self):
        self.logger.debug(f"Updating function calls for {self.name}")
        self.set_function("Post", self.update_account)
        self.set_function("Get", self.get)
        self.set_function("GetSession", self.get_session)
        self.set_function("GetCharacters", self.get_characters)
        self.set_function("PostRegister", self.register)
        self.set_function("PostLogin", self.login)
        self.set_function("Delete", self.delete_entry)
