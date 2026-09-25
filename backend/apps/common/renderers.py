from rest_framework.renderers import JSONRenderer


class StandardJSONRenderer(JSONRenderer):
    """Apply the API success envelope to every JSON success response once."""

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = (renderer_context or {}).get("response")
        if (
            response is not None
            and 200 <= response.status_code < 300
            and response.status_code != 204
            and not (isinstance(data, dict) and "success" in data)
        ):
            data = {"success": True, "data": data}
        return super().render(data, accepted_media_type, renderer_context)
