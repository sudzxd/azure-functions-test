"""HTTP request mock implementation.

This module provides a duck-typed mock for Azure HTTP trigger requests
with automatic body serialization, Pydantic validation, and full type safety.
"""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
# Standard Library
import json
from typing import Any
from urllib.parse import parse_qs

# Third-party
from pydantic import Field
from pydantic.dataclasses import dataclass

# Project/Local
from .._internal import get_logger, serialize_to_bytes
from ..protocols import HttpRequestProtocol

# =============================================================================
# LOGGER
# =============================================================================
logger = get_logger(__name__)


# =============================================================================
# CORE CLASSES
# =============================================================================
@dataclass
class HttpRequestMock:
    """Duck-typed mock for Azure HTTP trigger requests.

    This class implements the HttpRequestProtocol interface using Pydantic
    dataclass for validation and type safety. It provides automatic content-type
    inference, JSON parsing, and sensible defaults for testing.

    Attributes:
        method: HTTP method (GET, POST, PUT, DELETE, etc.). Defaults to "GET".
        url: Full request URL including query string. Defaults to "http://localhost".
        headers: HTTP headers as dictionary. Defaults to empty dict.
        params: Query parameters as dictionary. Defaults to empty dict.
        route_params: Route parameters as dictionary. Defaults to empty dict.
        body: Request body as bytes. Defaults to empty bytes.

    Examples:
        Create a GET request:

        >>> req = HttpRequestMock(method="GET", url="http://example.com/api/users")
        >>> req.method
        'GET'

        Create a POST request with JSON body:

        >>> req = HttpRequestMock(
        ...     method="POST",
        ...     body=b'{"name": "Alice"}',
        ...     headers={"Content-Type": "application/json"}
        ... )
        >>> req.get_json()
        {'name': 'Alice'}
    """

    method: str = Field(default="GET")
    url: str = Field(default="http://localhost")
    headers: dict[str, str] = Field(default_factory=dict)
    params: dict[str, str] = Field(default_factory=dict)
    route_params: dict[str, str] = Field(default_factory=dict)
    body: bytes = Field(default=b"")
    _form_cache: dict[str, str] | None = Field(default=None, init=False, repr=False)

    @property
    def form(self) -> dict[str, str]:
        """Parse and return form data from application/x-www-form-urlencoded body.

        Returns:
            Dictionary of form field names to values. For fields with multiple
            values, only the last value is returned.

        Examples:
            >>> req = HttpRequestMock(
            ...     body=b"name=Alice&age=30",
            ...     headers={"Content-Type": "application/x-www-form-urlencoded"}
            ... )
            >>> req.form["name"]
            'Alice'
            >>> req.form["age"]
            '30'
        """
        if self._form_cache is None:
            content_type = self.headers.get("Content-Type", "")
            if "application/x-www-form-urlencoded" in content_type:
                # Parse URL-encoded form data
                body_str = self.body.decode("utf-8")
                parsed = parse_qs(body_str, keep_blank_values=True)
                # parse_qs returns lists for each key; take the last value
                self._form_cache = {k: v[-1] for k, v in parsed.items()}
            else:
                self._form_cache = {}
        return self._form_cache

    def get_body(self) -> bytes:
        """Return request body as bytes.

        Returns:
            Request body as bytes.

        Examples:
            >>> req = HttpRequestMock(body=b"test")
            >>> req.get_body()
            b'test'
        """
        return self.body

    def get_json(self) -> Any:
        """Decode and return request body as a JSON object.

        Returns:
            Decoded JSON data.

        Raises:
            ValueError: When body does not contain valid JSON data.

        Examples:
            >>> req = HttpRequestMock(body=b'{"key": "value"}')
            >>> req.get_json()
            {'key': 'value'}
        """
        try:
            return json.loads(self.body.decode("utf-8"))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in HTTP request body: {e}") from e
        except UnicodeDecodeError as e:
            raise ValueError(f"Unable to decode HTTP request body as UTF-8: {e}") from e

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation showing method, URL, and memory address.

        Examples:
            >>> req = HttpRequestMock(method="POST", url="http://example.com")
            >>> repr(req)
            "<HttpRequestMock method='POST' url='http://example.com' at 0x...>"
        """
        return (
            f"<HttpRequestMock method={self.method!r} url={self.url!r} "
            f"at {hex(id(self))}>"
        )


# =============================================================================
# PUBLIC API
# =============================================================================
def mock_http_request(
    body: dict[Any, Any] | str | bytes | None = None,
    *,
    method: str = "GET",
    url: str = "http://localhost",
    headers: dict[str, str] | None = None,
    params: dict[str, str] | None = None,
    route_params: dict[str, str] | None = None,
) -> HttpRequestProtocol:
    """Create a mock HttpRequest for testing.

    Provides a test double for Azure HTTP trigger inputs with automatic
    body serialization and sensible defaults. Returns an object that
    implements HttpRequestProtocol.

    Args:
        body: Request body. Dicts are JSON-serialized automatically.
            Strings are UTF-8 encoded. Bytes are used as-is.
        method: HTTP method. Defaults to "GET".
        url: Full request URL. Defaults to "http://localhost".
        headers: HTTP headers dictionary. Defaults to empty dict.
        params: Query parameters dictionary. Defaults to empty dict.
        route_params: Route parameters dictionary. Defaults to empty dict.

    Returns:
        An HttpRequestMock instance implementing HttpRequestProtocol.

    Examples:
        Create a simple GET request:

        >>> req = mock_http_request(method="GET", url="http://example.com/api/users")
        >>> req.method
        'GET'

        Create a POST request with JSON body:

        >>> req = mock_http_request(
        ...     {"name": "Alice", "email": "alice@example.com"},
        ...     method="POST",
        ...     headers={"Content-Type": "application/json"}
        ... )
        >>> req.get_json()
        {'name': 'Alice', 'email': 'alice@example.com'}

        Create a request with query parameters:

        >>> req = mock_http_request(
        ...     method="GET",
        ...     url="http://example.com/api/users?page=1&limit=10",
        ...     params={"page": "1", "limit": "10"}
        ... )
        >>> req.params["page"]
        '1'

        Create a request with route parameters:

        >>> req = mock_http_request(
        ...     method="GET",
        ...     route_params={"user_id": "123"}
        ... )
        >>> req.route_params["user_id"]
        '123'
    """
    logger.debug(
        "Creating HttpRequestMock with method=%s, url=%s",
        method,
        url,
    )

    # Serialize body if provided
    serialized_body = serialize_to_bytes(body, allow_list=False)

    # Auto-set Content-Type header if not provided
    final_headers = dict(headers) if headers else {}
    if body and isinstance(body, dict) and "Content-Type" not in final_headers:
        final_headers["Content-Type"] = "application/json"

    return HttpRequestMock(
        method=method,
        url=url,
        headers=final_headers,
        params=params or {},
        route_params=route_params or {},
        body=serialized_body,
    )
