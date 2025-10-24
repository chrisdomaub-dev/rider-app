from __future__ import annotations

from functools import lru_cache
from typing import Any, Optional, Union

from rest_framework import status
from rest_framework.response import Response


class RestViewMixin:
    """
    A reusable mixin for DRF providing:
      1. Action-based serializer identification.
      2. Unified JSON response with consistent schema.

    Response schema:
    {
        "message": str,
        "errors": list[str],
        "data": any,
        "status": int
    }
    """

    def get_serializer_class(self):
        """Identify which serializer to use based on the action name."""

        if hasattr(self, "action_serializers"):
            serializer = getattr(self, "action_serializers", {}).get(self.action)
            if serializer:
                return serializer
        return super().get_serializer_class()

    def RestResponse(
        self,
        data: Optional[Any] = None,
        message: Optional[str] = None,
        errors: Optional[Union[str, list[str]]] = None,
        status: int = 200,
        **kwargs: Any,
    ) -> Response:
        """
        Build and return a consistent JSON response.

        Accepts numeric status (e.g., 200) or DRF constants (e.g., status.HTTP_200_OK).
        Always returns numeric code in the JSON payload.
        """
        payload = {
            "message": self._build_message(message, status),
            "errors": self._build_errors(errors),
            "data": data,
            "status": status,
        }

        return Response(payload, status=self._map_status_constant(status), **kwargs)

    def _build_errors(self, errors: Optional[Union[str, list[str]]]) -> list[str]:
        """Normalize the error field into a list of strings."""
        if not errors:
            return []
        if isinstance(errors, str):
            return [errors.strip()] if errors.strip() else []
        if isinstance(errors, (list, tuple)):
            return [str(e) for e in errors if str(e).strip()]
        return [str(errors)]

    @lru_cache(maxsize=None)
    def _map_status_constant(self, status_code: int) -> int:
        """Map numeric code to DRF status constant if available, returns the numeric code otherwise."""
        for name, value in vars(status).items():
            if name.startswith("HTTP_") and value == status_code:
                return value
        return status_code

    def _build_message(self, message: Optional[str], code: int) -> str:
        """Provide a default message if none is given."""
        if message:
            return message
        if 200 <= code < 300:
            return "Success"
        elif 400 <= code < 500:
            return "A client error occurred."
        elif 500 <= code < 600:
            return "A server error occurred."
        return "Response"
