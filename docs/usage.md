# Usage

## Simplest usage

```python
# Setup
from mm_logs import configure_logging # TODO Change import
configure_logging()

# Usage
import logging
logger = logging.getLogger(__name__)
logger.info("Hello world!")
```

With this setup, you get a default logger, with a default configuration.
It supports JSON structured logging, and it is configured to work with DataDog.
You can configure it using environment variables. XXX LINK TO CONFIGURATION

## Custom Python logging configuration

```python
# Setup
from mm_utils import configure_logging # TODO Change import
configuration = ...
configuratio. # Customize the configuration as you wish
configure_logging(configuration)
```


## Configure loguru as well

```python
...
configure_logging()
configure_loguru()
```

## Configure Hypercorn or Gunicorn xSGI servers

