import json
from enum import Enum
from logging import getLogger
logger = getLogger(__name__)

class ERROR_CODE(Enum):
    INIT = 10
    UPLOAD = 30
    DOWNLOAD = 20
    PROGRESS = 30
    TERMINATE = 40


def handle_error(e, error_code):
    logger.error(f"In {error_code}: {e}")
    print(json.dumps({"error": {"code": error_code, "message": e}}), flush=True)
    raise
