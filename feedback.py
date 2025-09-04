# ...existing code...
import logging
from typing import Any, Dict, Optional
from utils import mongo

logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logging.basicConfig(format="%(asctime)s %(levelname)s [%(name)s]: %(message)s", level=logging.DEBUG)

def collect_feedback(prompt: str, response: str, user_email: str, rating: Optional[int] = None, extra: Optional[Dict[str,Any]] = None) -> None:
    try:
        logger.debug("collect_feedback user=%s prompt_len=%d", user_email, len(prompt))
        metadata = extra or {}
        if rating is not None:
            metadata["rating"] = int(rating)
        mongo.add_feedback(user_email, prompt, response, metadata=metadata)
        logger.info("collect_feedback stored for %s", user_email)
    except TypeError:
        # fallback to older signature
        try:
            mongo.add_feedback(user_email, prompt, response)
            logger.info("collect_feedback stored (fallback) for %s", user_email)
        except Exception:
            logger.exception("collect_feedback fallback failed")
    except Exception:
        logger.exception("collect_feedback failed")
# ...existing code...