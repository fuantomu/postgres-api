def generate_statement(columns) -> str:
    return ",\n".join(
        (
            f"{key} {val['value']} DEFAULT {val['default']}"
            if val.get("default")
            else f"{key} {val['value']}"
        )
        for key, val in columns.items()
    )
