# ...existing code...
import logging
from typing import Optional, Dict, Any
from utils import mongo

logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logging.basicConfig(format="%(asctime)s %(levelname)s [%(name)s]: %(message)s", level=logging.DEBUG)

def log_event(username: str, event_type: str, details: Optional[Dict[str, Any]] = None) -> None:
    try:
        logger.debug("log_event username=%s event=%s details=%s", username, event_type, details)
        mongo.add_event(username, event_type, details=details or {})
    except Exception:
        logger.exception("log_event failed; falling back to stdout")
        logger.info("EVENT %s %s %s", username, event_type, details)
# ...existing code...