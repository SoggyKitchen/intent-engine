import logging
import os
from rich.logging import RichHandler

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)],
)
log = logging.getLogger("intent")
