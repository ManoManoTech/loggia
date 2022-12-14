from typing import Tuple
from urllib.parse import urlsplit, urlunsplit


def get_repository_information(source_url: str) -> Tuple[str, str]:
    """
    Retrieve name of the repository and url from any commit or file url from Gitlab.

    Args:
        source_url: a file or commit url from gitlab

    Returns:
        a Tuple with (name of the repository, url of the repository)

    Raises:
        ValueError: raised when the source_url is not valid
    """
    url_split = urlsplit(source_url)
    trimmed_path = url_split.path.split("/-/")[0].strip("/")
    url = urlunsplit((url_split.scheme, url_split.netloc, trimmed_path, None, None))
    return trimmed_path, url
