"""Example: Testing HTTP triggered Azure Functions."""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
# Standard Library
import json

# Third-party
from azure.functions import HttpResponse

# Project/Local
from azure_functions_test import mock_http_request
from azure_functions_test.protocols import HttpRequestProtocol


# =============================================================================
# EXAMPLE: Simple HTTP GET Request
# =============================================================================
def get_user(req: HttpRequestProtocol) -> HttpResponse:
    """Handle GET request to retrieve user by ID.

    Args:
        req: HTTP request with user_id parameter.

    Returns:
        HTTP response with user data or error.
    """
    user_id = req.params.get("user_id")

    if not user_id:
        return HttpResponse(
            json.dumps({"error": "user_id parameter is required"}),
            status_code=400,
            mimetype="application/json",
        )

    # Simulate user retrieval
    user = {"user_id": user_id, "name": "John Doe", "email": "john@example.com"}

    return HttpResponse(
        json.dumps(user),
        status_code=200,
        mimetype="application/json",
    )


def test_get_user_success() -> None:
    """Test successful user retrieval."""
    # Arrange
    req = mock_http_request(params={"user_id": "123"})

    # Act
    response = get_user(req)

    # Assert
    assert response.status_code == 200
    data = json.loads(response.get_body())
    assert data["user_id"] == "123"
    assert data["name"] == "John Doe"


def test_get_user_missing_parameter() -> None:
    """Test user retrieval with missing user_id parameter."""
    # Arrange
    req = mock_http_request(params={})

    # Act
    response = get_user(req)

    # Assert
    assert response.status_code == 400
    data = json.loads(response.get_body())
    assert "error" in data


# =============================================================================
# EXAMPLE: HTTP POST with JSON Body
# =============================================================================
def create_order(req: HttpRequestProtocol) -> HttpResponse:
    """Handle POST request to create a new order.

    Args:
        req: HTTP request with order data in body.

    Returns:
        HTTP response with created order or error.
    """
    try:
        order_data = req.get_json()
    except ValueError:
        return HttpResponse(
            json.dumps({"error": "Invalid JSON in request body"}),
            status_code=400,
            mimetype="application/json",
        )

    # Validate required fields
    if "items" not in order_data or not order_data["items"]:
        return HttpResponse(
            json.dumps({"error": "items field is required"}),
            status_code=400,
            mimetype="application/json",
        )

    # Create order
    order = {
        "order_id": "ORD-12345",
        "items": order_data["items"],
        "total": sum(item.get("price", 0) for item in order_data["items"]),
        "status": "created",
    }

    return HttpResponse(
        json.dumps(order),
        status_code=201,
        mimetype="application/json",
    )


def test_create_order_success() -> None:
    """Test successful order creation."""
    # Arrange
    order_data = {
        "items": [
            {"id": 1, "name": "Item 1", "price": 10.00},
            {"id": 2, "name": "Item 2", "price": 20.00},
        ]
    }
    req = mock_http_request(order_data, method="POST")

    # Act
    response = create_order(req)

    # Assert
    assert response.status_code == 201
    data = json.loads(response.get_body())
    assert data["order_id"] == "ORD-12345"
    assert data["total"] == 30.00


def test_create_order_missing_items() -> None:
    """Test order creation with missing items."""
    # Arrange
    req = mock_http_request({}, method="POST")

    # Act
    response = create_order(req)

    # Assert
    assert response.status_code == 400


# =============================================================================
# EXAMPLE: HTTP Headers and Authentication
# =============================================================================
def protected_endpoint(req: HttpRequestProtocol) -> HttpResponse:
    """Handle request with authentication.

    Args:
        req: HTTP request with Authorization header.

    Returns:
        HTTP response based on authentication status.
    """
    auth_header: str | None = req.headers.get("Authorization", None)

    if not auth_header or not auth_header.startswith("Bearer "):
        return HttpResponse(
            json.dumps({"error": "Unauthorized"}),
            status_code=401,
            mimetype="application/json",
        )

    token: str = auth_header.replace("Bearer ", "")

    # Simulate token validation
    if token != "valid-token-123":
        return HttpResponse(
            json.dumps({"error": "Invalid token"}),
            status_code=403,
            mimetype="application/json",
        )

    return HttpResponse(
        json.dumps({"message": "Access granted"}),
        status_code=200,
        mimetype="application/json",
    )


def test_protected_endpoint_with_valid_token() -> None:
    """Test protected endpoint with valid authentication."""
    # Arrange
    req = mock_http_request(headers={"Authorization": "Bearer valid-token-123"})

    # Act
    response = protected_endpoint(req)

    # Assert
    assert response.status_code == 200
    data = json.loads(response.get_body())
    assert data["message"] == "Access granted"


def test_protected_endpoint_without_token() -> None:
    """Test protected endpoint without authentication."""
    # Arrange
    req = mock_http_request(headers={})

    # Act
    response = protected_endpoint(req)

    # Assert
    assert response.status_code == 401


# =============================================================================
# EXAMPLE: Route Parameters
# =============================================================================
def test_http_request_with_route_params() -> None:
    """Test HTTP request with route parameters."""
    # Arrange
    req = mock_http_request(route_params={"id": "123", "category": "electronics"})

    # Assert
    assert req.route_params["id"] == "123"
    assert req.route_params["category"] == "electronics"


# =============================================================================
# EXAMPLE: Content Type Detection
# =============================================================================
def test_http_request_json_auto_sets_content_type() -> None:
    """Test that JSON body automatically sets Content-Type header."""
    # Arrange
    req = mock_http_request({"data": "test"}, method="POST")

    # Assert
    assert req.headers["Content-Type"] == "application/json"


if __name__ == "__main__":
    # Run all test examples
    test_get_user_success()
    test_get_user_missing_parameter()
    test_create_order_success()
    test_create_order_missing_items()
    test_protected_endpoint_with_valid_token()
    test_protected_endpoint_without_token()
    test_http_request_with_route_params()
    test_http_request_json_auto_sets_content_type()
    print("✓ All HTTP request examples passed!")
