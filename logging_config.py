import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    # Create custom log format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Setup handlers
    stream_handler = logging.StreamHandler()
    file_handler = RotatingFileHandler("betting_api.log", maxBytes=5 * 1024 * 1024, backupCount=5)  # Rotating logs when file reaches 5 MB

    # Set logging levels
    stream_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)

    # Setup log formatting
    formatter = logging.Formatter(log_format)
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Configure the root logger
    logging.basicConfig(
        level=logging.INFO,
        handlers=[stream_handler, file_handler]
    )

# Logger instance
logger = logging.getLogger(__name__)
