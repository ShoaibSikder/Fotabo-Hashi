from typing import Any

from rest_framework.response import Response


def success_response(
    *,
    data: Any = None,
    status_code: int = 200,
) -> Response:
    return Response(
        {
            "success": True,
            "data": data,
        },
        status=status_code,
    )