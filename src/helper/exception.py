from psycopg import errors
import re


def handle_exception(exception: Exception):
    match (exception.__class__):
        case errors.UniqueViolation:
            group = re.search(r"Key \(([^)]+)\)=\(([^)]+)\)", str(exception))
            return (
                f"An item with the {group.group(1)} '{group.group(2)}' already exists"
            )
        case errors.ConnectionTimeout:
            return "Connection to the database timed out. Is the host/post correct?"
        case errors.InvalidTextRepresentation:
            group = re.search(r"type (\w+): \"(.+)\"", str(exception))
            return f"Value '{group.group(2)}' does not match type of '{group.group(1)}'"
        case _:
            return str(exception)
