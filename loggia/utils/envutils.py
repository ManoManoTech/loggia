import os


def with_env(variable_name: str, variable_value: str) -> None:
    """'helper' to discourage people from procedurally editing the environment when reading our usage documentation."""
    os.environ[variable_name] = variable_value
