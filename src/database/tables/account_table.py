import base64
from datetime import datetime, timezone
from src.database.helper.hash import verify_hash
from src.database.tables.table import Table

DEFAULT_TIMEOUT = 3600


class AccountTable(Table):
    columns = {
        "id": {"value": "BIGSERIAL UNIQUE", "default": ""},
        "username": {"value": "varchar(32) UNIQUE NOT NULL", "default": ""},
        "hash": {"value": "TEXT NOT NULL", "default": ""},
        "level": {"value": "SMALLINT NOT NULL", "default": 0},
        "guild": {"value": "INTEGER REFERENCES guild(id)", "default": None},
        "creation_time": {"value": "BIGINT NOT NULL", "default": 0},
        "PRIMARY KEY": {"value": "(id)", "default": ""},
    }

    def get(self, request: str | dict):
        found_item = self.select("ALL", [("username", "=", request["username"])])

        if not found_item:
            raise Exception(f"No user found for name '{request['username']}'")
        results = self.format_result(found_item)[0]
        results.pop("hash")
        return results

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

    def add_or_update(self, request):
        query = f"select username from account where username = '{request['username']}'"
        found_item = self.select_query(query)

        if request["guild"] == -1:
            request["guild"] = None

        if found_item and request["hash"]:
            raise Exception(
                f"Account with username '{request['username']}' already exists"
            )

        if found_item:
            self.update(
                request,
                [("username", "=", request["username"])],
                "account",
            )
            return "Success"
        request["creation_time"] = datetime.now(timezone.utc).timestamp()
        self.insert(request, "account")
        return f"{request['username']}"

    def login(self, request):
        query = f"select hash from account where username = '{request['username']}'"
        found_item = self.select_query(query)

        if not found_item:
            raise Exception("Account or password is incorrect")

        correct_login = verify_hash(request["hash"], found_item[0][0])
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

    def update_functions(self):
        self.logger.debug(f"Updating function calls for {self.name}")
        self.set_function("Get", self.get)
        self.set_function("GetSession", self.get_session)
        self.set_function("PostRegister", self.add_or_update)
        self.set_function("PostLogin", self.login)
        self.set_function("Delete", self.delete_entry)
