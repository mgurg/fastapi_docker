import uuid


def to_snake_case(value: str):
    return "_".join(value.lower().split())


def is_valid_uuid(value: str):
    try:
        return uuid.UUID(str(value))
    except ValueError:
        return None
