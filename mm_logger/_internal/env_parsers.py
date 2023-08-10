def default(value: str) -> list[list[str]]:
    return [[value]]


def comma_colon(value: str) -> list[list[str]]:
    return [e.split(":") for e in value.split(",")]


def comma(value: str) -> list[list[str]]:
    return [[e] for e in value.split(",")]
