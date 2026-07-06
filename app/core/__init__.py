from .config import settings
from .logger import get_logger

# whatever we pull inside __all__ becomes part of this package public API
# so it can be imported from this package
logger = get_logger()

__all__ = ["settings"]
