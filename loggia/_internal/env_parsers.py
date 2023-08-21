FALSY_STRINGS={"N", "NO", "NEIN", "NON", "0", "FALSE", "DISABLED", "BY CHTULU, NO!"}
def _is_truthy_string(s: str) -> bool:
    if s and s.upper() not in FALSY_STRINGS:
        return True
    return False


def default(value: str) -> list[list[str]]:
    return [[value]]


def comma_colon(value: str) -> list[list[str]]:
    return [e.split(":") for e in value.split(",")]


def comma(value: str) -> list[list[str]]:
    return [[e] for e in value.split(",")]


def single_boolean_string(value: str) -> list[list[bool]]:
    return [[_is_truthy_string(value)]]