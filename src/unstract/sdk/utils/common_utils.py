import logging
import uuid

from unstract.sdk.constants import LogLevel

logger = logging.getLogger(__name__)


class CommonUtils:
    @staticmethod
    def generate_uuid() -> str:
        """Class method to get uuid."""
        return str(uuid.uuid4())


# Mapping from python log level to Unstract counterpart
PY_TO_UNSTRACT_LOG_LEVEL = {
    logging.DEBUG: LogLevel.DEBUG,
    logging.INFO: LogLevel.INFO,
    logging.WARNING: LogLevel.WARN,
    logging.ERROR: LogLevel.ERROR,
}
