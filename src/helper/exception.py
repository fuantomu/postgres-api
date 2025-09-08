from psycopg import errors
import re

def handle_exception(exception : Exception):
    match(exception.__class__):
        case errors.UniqueViolation:
            group = re.search(r"Key \((\w+)\)=\(([^)]+)\)", str(exception))
            return f"An item with the {group.group(1)} '{group.group(2)}' already exists"
        case errors.ConnectionTimeout:
            return f"Connection to the database timed out. Is the host/post correct?"
        case _:
            return str(exception)