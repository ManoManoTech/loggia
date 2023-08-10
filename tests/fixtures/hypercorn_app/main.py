from hypercorn.asyncio import serve
from hypercorn.config import Config

from hypercorn_app.app import app
from loggia.logger import configure_logging
from loggia.structlog_utils.hypercorn_logger import HypercornLogger


async def main():
    # Configure the logger
    configure_logging()
    # Configure Hypercorn as you would normally
    config = Config()
    config.logger_class = HypercornLogger
    await serve(app, config)


if __name__ == "__main__":
    # Run asyncio event loop
    import asyncio

    asyncio.run(main())
