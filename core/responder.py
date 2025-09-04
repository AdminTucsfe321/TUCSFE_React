import yaml
import os
import logging

# Setup logger for this module
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logging.basicConfig(
        format="%(asctime)s %(levelname)s [%(name)s]: %(message)s",
        level=logging.INFO
    )

# Load the dummy content only once for efficiency
try:
    DUMMY_PATH = os.path.join(os.path.dirname(__file__), "..", "book_input_dummy.yaml")
    with open(DUMMY_PATH, "r") as f:
        BOOK = yaml.safe_load(f)
    logger.info(f"Loaded dummy book content from {DUMMY_PATH} successfully.")
except Exception as e:
    logger.error(f"Failed to load dummy book content from {DUMMY_PATH}: {e}", exc_info=True)
    BOOK = {"chapters": []}  # Fallback empty structure

def get_response(prompt, config=None):
    logger.info(f"get_response called with prompt: '{prompt}'")

    if not prompt.strip():
        logger.warning("Empty prompt received.")
        return "Please enter a question."

    prompt_l = prompt.lower()
    logger.debug(f"Lowercased prompt: '{prompt_l}'")

    # Check for keywords and match chapters
    if "inquiry" in prompt_l or "universal" in prompt_l:
        logger.info("Matched keyword related to 'inquiry' or 'universal'")
        for ch in BOOK.get("chapters", []):
            if "inquiry" in ch.get("title", "").lower():
                logger.info(f"Returning content for chapter: {ch.get('title')}")
                return ch.get("content", "")
    if "habit" in prompt_l:
        logger.info("Matched keyword related to 'habit'")
        for ch in BOOK.get("chapters", []):
            if "habit" in ch.get("title", "").lower():
                logger.info(f"Returning content for chapter: {ch.get('title')}")
                return ch.get("content", "")

    logger.info("No matching keywords found. Returning fallback message.")
    return "This is a Beta AI demo. Try: 'What is Universal Inquiry?' or 'How do habits form?'"
