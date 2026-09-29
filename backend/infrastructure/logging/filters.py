import logging


class RequestIDFilter(logging.Filter):
    """Attach request metadata without recording headers, cookies, or bodies."""

    def filter(self, record):
        request = getattr(record, "request", None)
        if request is not None:
            record.request_id = getattr(request, "request_id", None)
            record.method = request.method
            record.path = request.path
        return True
