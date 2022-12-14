import logging
from os.path import exists
from pathlib import Path

logger = logging.getLogger(__name__)
try:
    import pygit2
except ImportError:
    logger.warning("pygit2 not installed, gitutils will not work.")


def clone(local_path: str, user: str, password: str, host: str, path: str) -> None:
    """
    Clones a repository into a local folder.
    Scheme is assumed to be `https://`

    Args:
        local_path (str): Local path to clone into. If the directory already exists, do nothing.
        user (str): Username for the remote repository.
        password (str): Password for the remote repository.
        host (str): Hostname for the remote repository.
        path (str): Path to the remote repository.
    """
    ### Support more options from pygit2.clone_repository
    url = f"https://{user}:{password}@{host}/{path}"
    if exists(local_path):
        logger.warning(f"Directory found at #{local_path}, skipping clone.")
    else:
        pygit2.clone_repository(url, local_path)
        logger.info(f"Clone completed: {path}")


def remove_then_add_everything(local_path: str) -> None:
    """Add/Remove all files in `local_path` repository."""
    repo = pygit2.Repository(local_path)
    index = repo.index
    index.remove_all(["*"])
    for file in Path(local_path).glob("**/*"):
        relpath = file.relative_to(local_path)
        if not file.is_dir() and not str(relpath).startswith(".git/"):
            index.add(relpath)
    index.write()


def commit(
    local_path: str,
    author_name: str,
    author_email: str,
    message: str,
    committer_name: str | None = None,
    committer_email: str | None = None,
    ref: str = "refs/head/master",
) -> None:
    """Commit staged changes in `local_path` repository"""
    committer_name = committer_name or author_name
    committer_email = committer_email or author_email
    author = pygit2.Signature(author_name, author_email)  # type: ignore # pylint:disable=no-member
    committer = pygit2.Signature(committer_name, committer_email)  # type: ignore #pylint:disable=no-member
    repo = pygit2.Repository(local_path)
    tree_id = repo.index.write_tree()
    oid = repo.create_commit(ref, author, committer, message, tree_id, [repo.head.target])
    repo.head.set_target(oid)
    logger.info(f"Commit {oid} added to {local_path}")


def push(local_path: str, remote_name: str = "origin", ref: str = "refs/heads/master:refs/heads/master") -> None:
    repo = pygit2.Repository(local_path)
    for remote in repo.remotes:
        if remote.name == remote_name:
            remote.push(ref.split(":"))
    logger.info(f"Pushed {local_path} to remote {remote_name} ref {ref}")
