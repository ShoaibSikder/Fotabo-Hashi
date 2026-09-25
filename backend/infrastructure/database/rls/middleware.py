from .context import clear_rls_context


class ClearRLSContextMiddleware:
    """Ensure a pooled connection never carries identity into another request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        finally:
            if getattr(request, "_rls_context_active", False):
                clear_rls_context()
