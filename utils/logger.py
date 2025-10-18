import logging
import os

def setup_logger():
    """Configures and returns a logger instance."""
    logger = logging.getLogger("AI-Sahayak")
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(log_level)

    # Create console handler
    ch = logging.StreamHandler()
    ch.setLevel(log_level)

    # Create formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    # Add the handler to the logger, ensuring no duplicates
    if not logger.handlers:
        logger.addHandler(ch)
    
    return logger

# Initialize logger
logger = setup_logger()