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
    SFTP_AUTH = 50


def handle_error(e, error_code):
    logger.error(f"In {error_code}: {e}")
    print(json.dumps({"error": {"code": error_code, "message": e}}), flush=True)
    raise


class Progress:
    byte_so_far = 0
    oid = None
    i = 0.0

    def __init__(self, oid):
        logger.info("Progress is initialized")
        self.oid = oid

    def progress_callback(self, byte_so_far, size):
        if byte_so_far / size < self.i:
            return
        self.i += 0.1
        bytes_since_last = byte_so_far - self.byte_so_far
        self.byte_so_far = byte_so_far
        res = json.dumps({
            "event": "progress",
            "oid": self.oid,
            "byteSoFar": byte_so_far,
            "bytesSinceLast": bytes_since_last,
        })
        logger.debug(res)
        print(res, flush=True)  # Tried, but couldn't return by yield in a callback.


def stage_logger(phase):
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.info(f"Enter {phase}.")
            yield from func(*args, **kwargs)
            logger.info(f"Exit {phase}.")
        return wrapper
    return decorator


def include(k):
    def option(v):
        return [k, str(v)] if v else []
    return option


def include_pyelfs_wrapped(k):
    def option(v):
        return [k, f"pyelfs://{str(v)}"] if v else []
    return option


def exclude():
    def option(v):
        return []
    return option
