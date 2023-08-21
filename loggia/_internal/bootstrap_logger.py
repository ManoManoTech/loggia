class BootstrapLogger:
    """BootstrapLogger for use before standard logging is setup.

    It basically captures all log calls properly - logs are properly written
    after logging is setup. (vaporware, presently clobbering stdout like a maniac)
    """

    @classmethod
    def warn(cls, msg: str, exc=None) -> None:
        cls.log("warn", msg, exc)

    @classmethod
    def error(cls, msg: str, exc=None) -> None:
        cls.log("error", msg, exc)

    @classmethod
    def log(cls, level: str, msg: str, exc=None) -> None:
        # XXX implement a proper prelogger
        print(f"[{level.upper()}] {msg}")
        if exc:
            print(exc)
