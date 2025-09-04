# ...existing code...
import logging
from typing import Optional, Tuple
from utils.mongo import (
    create_user, get_user_by_email, verify_password,
    create_session, validate_session, delete_session, hash_password
)

logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logging.basicConfig(format="%(asctime)s %(levelname)s [%(name)s]: %(message)s", level=logging.DEBUG)

def register_user(email: str, name: str, password: str, is_admin: bool = False):
    logger.debug("register_user %s", email)
    return create_user(email, name, password, is_admin)

def login_user(email: str, password: str) -> Tuple[Optional[str], Optional[str]]:
    logger.debug("login_user %s", email)
    user = get_user_by_email(email)
    if not user:
        logger.warning("login_user: user not found %s", email)
        return None, "User not found"
    if not verify_password(password, user.get("password", "")):
        logger.warning("login_user: invalid password %s", email)
        return None, "Invalid password"
    token = create_session(email)
    logger.info("login_user success %s", email)
    return token, None

def logout_token(token: str):
    logger.debug("logout_token %s", token)
    delete_session(token)

def current_user_from_token(token: str) -> Optional[str]:
    return validate_session(token)
# ...existing code...