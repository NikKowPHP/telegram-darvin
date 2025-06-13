import logging
import sys
from app.core.config import settings


def setup_logging():
    logging.basicConfig(
        level=settings.LOG_LEVEL.upper(),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
            # Add FileHandler if needed later
        ],
    )
    # You can set specific log levels for libraries here if needed
    # logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
