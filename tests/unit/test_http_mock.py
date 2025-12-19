"""Unit tests for HttpRequest mock."""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
# Project/Local
from azure_functions_test import mock_http_request


# =============================================================================
# TESTS: Initialization & Defaults
# =============================================================================
def test_mock_http_request_uses_defaults_when_no_args() -> None:
    """mock_http_request() should use default values when called with no args."""
    req = mock_http_request()

    assert req.method == "GET"
    assert req.url == "http://localhost"
    assert req.headers == {}
    assert req.params == {}
    assert req.route_params == {}
    assert req.get_body() == b""


def test_mock_http_request_uses_empty_body_by_default() -> None:
    """mock_http_request() should use empty bytes body by default."""
    req = mock_http_request()

    assert req.get_body() == b""


# =============================================================================
# TESTS: HTTP Methods
# =============================================================================
def test_mock_http_request_get_method() -> None:
    """GET method should be set correctly."""
    req = mock_http_request(method="GET")

    assert req.method == "GET"


def test_mock_http_request_post_method() -> None:
    """POST method should be set correctly."""
    req = mock_http_request(method="POST")

    assert req.method == "POST"


def test_mock_http_request_put_method() -> None:
    """PUT method should be set correctly."""
    req = mock_http_request(method="PUT")

    assert req.method == "PUT"


def test_mock_http_request_delete_method() -> None:
    """DELETE method should be set correctly."""
    req = mock_http_request(method="DELETE")

    assert req.method == "DELETE"


def test_mock_http_request_patch_method() -> None:
    """PATCH method should be set correctly."""
    req = mock_http_request(method="PATCH")

    assert req.method == "PATCH"


# =============================================================================
# TESTS: Body Serialization - Dict
# =============================================================================
def test_mock_http_request_dict_body_serialized_to_json() -> None:
    """Dict body should be JSON-serialized to bytes."""
    req = mock_http_request({"name": "Alice", "age": 30}, method="POST")

    body = req.get_body()
    assert isinstance(body, bytes)
    assert body == b'{"name": "Alice", "age": 30}'


def test_mock_http_request_dict_body_get_json_returns_dict() -> None:
    """get_json() should return the original dict."""
    req = mock_http_request({"name": "Alice", "age": 30}, method="POST")

    data = req.get_json()
    assert data == {"name": "Alice", "age": 30}


def test_mock_http_request_nested_dict_body() -> None:
    """Nested dict should be serialized correctly."""
    req = mock_http_request({"user": {"name": "Alice", "age": 30}}, method="POST")

    data = req.get_json()
    assert data == {"user": {"name": "Alice", "age": 30}}


def test_mock_http_request_dict_auto_sets_content_type() -> None:
    """Dict body should auto-set Content-Type to application/json."""
    req = mock_http_request({"data": "test"}, method="POST")

    assert req.headers["Content-Type"] == "application/json"


# =============================================================================
# TESTS: Body Serialization - String
# =============================================================================
def test_mock_http_request_string_body_encoded_to_utf8() -> None:
    """String body should be UTF-8 encoded to bytes."""
    req = mock_http_request("Hello, World!", method="POST")

    body = req.get_body()
    assert isinstance(body, bytes)
    assert body == b"Hello, World!"


def test_mock_http_request_string_body_with_unicode() -> None:
    """String with Unicode characters should be encoded correctly."""
    req = mock_http_request("Hello, 世界! 🌍", method="POST")

    body = req.get_body()
    assert body.decode("utf-8") == "Hello, 世界! 🌍"


# =============================================================================
# TESTS: Body Serialization - Bytes
# =============================================================================
def test_mock_http_request_bytes_body_used_as_is() -> None:
    """Bytes body should be used as-is without modification."""
    req = mock_http_request(b"\x00\x01\x02\x03", method="POST")

    body = req.get_body()
    assert body == b"\x00\x01\x02\x03"


# =============================================================================
# TESTS: URL & Headers
# =============================================================================
def test_mock_http_request_custom_url() -> None:
    """Custom URL should override the default."""
    req = mock_http_request(url="http://example.com/api/users")

    assert req.url == "http://example.com/api/users"


def test_mock_http_request_custom_headers() -> None:
    """Custom headers should be set correctly."""
    headers = {"Authorization": "Bearer token123", "X-Custom": "value"}
    req = mock_http_request(headers=headers)

    assert req.headers["Authorization"] == "Bearer token123"
    assert req.headers["X-Custom"] == "value"


def test_mock_http_request_custom_content_type_header() -> None:
    """Custom Content-Type header should not be overridden."""
    headers = {"Content-Type": "text/plain"}
    req = mock_http_request({"data": "test"}, method="POST", headers=headers)

    assert req.headers["Content-Type"] == "text/plain"


# =============================================================================
# TESTS: Query Parameters
# =============================================================================
def test_mock_http_request_query_params() -> None:
    """Query parameters should be set correctly."""
    params = {"page": "1", "limit": "10", "filter": "active"}
    req = mock_http_request(params=params)

    assert req.params["page"] == "1"
    assert req.params["limit"] == "10"
    assert req.params["filter"] == "active"


def test_mock_http_request_empty_params() -> None:
    """Empty params should work correctly."""
    req = mock_http_request(params={})

    assert req.params == {}


# =============================================================================
# TESTS: Route Parameters
# =============================================================================
def test_mock_http_request_route_params() -> None:
    """Route parameters should be set correctly."""
    route_params = {"user_id": "123", "action": "edit"}
    req = mock_http_request(route_params=route_params)

    assert req.route_params["user_id"] == "123"
    assert req.route_params["action"] == "edit"


def test_mock_http_request_empty_route_params() -> None:
    """Empty route params should work correctly."""
    req = mock_http_request(route_params={})

    assert req.route_params == {}


# =============================================================================
# TESTS: Edge Cases
# =============================================================================
def test_mock_http_request_empty_dict_body() -> None:
    """Empty dict should serialize correctly."""
    req = mock_http_request({}, method="POST")

    assert req.get_json() == {}
    assert req.get_body() == b"{}"


def test_mock_http_request_empty_string_body() -> None:
    """Empty string should encode to empty bytes."""
    req = mock_http_request("", method="POST")

    assert req.get_body() == b""


def test_mock_http_request_none_body() -> None:
    """None body should result in empty bytes."""
    req = mock_http_request(None, method="POST")

    assert req.get_body() == b""


# =============================================================================
# TESTS: Multiple Instances
# =============================================================================
def test_mock_http_request_multiple_instances_independent() -> None:
    """Multiple request instances should be independent."""
    req1 = mock_http_request({"order": 1}, method="POST", url="http://example.com/1")
    req2 = mock_http_request({"order": 2}, method="GET", url="http://example.com/2")

    assert req1.get_json() == {"order": 1}
    assert req2.get_json() == {"order": 2}
    assert req1.method == "POST"
    assert req2.method == "GET"
    assert req1.url == "http://example.com/1"
    assert req2.url == "http://example.com/2"


# =============================================================================
# TESTS: Integration with Real Use Cases
# =============================================================================
def test_mock_http_request_api_endpoint_simulation() -> None:
    """Should support testing typical API endpoint scenarios."""
    req = mock_http_request(
        {"name": "Alice", "email": "alice@example.com"},
        method="POST",
        url="http://example.com/api/users",
        headers={"Authorization": "Bearer token123"},
        params={"validate": "true"},
    )

    assert req.method == "POST"
    assert req.get_json()["name"] == "Alice"
    assert req.headers["Authorization"] == "Bearer token123"
    assert req.params["validate"] == "true"


def test_mock_http_request_with_all_parameters() -> None:
    """All parameters should work together."""
    req = mock_http_request(
        {"data": "test"},
        method="PUT",
        url="http://example.com/api/resource/123",
        headers={"Content-Type": "application/json", "X-API-Key": "key123"},
        params={"version": "2"},
        route_params={"id": "123"},
    )

    assert req.get_json() == {"data": "test"}
    assert req.method == "PUT"
    assert req.url == "http://example.com/api/resource/123"
    assert req.headers["Content-Type"] == "application/json"
    assert req.headers["X-API-Key"] == "key123"
    assert req.params["version"] == "2"
    assert req.route_params["id"] == "123"
