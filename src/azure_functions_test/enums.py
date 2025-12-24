"""Enumerations for azure-functions-test.

This module provides enumeration types for commonly used constants
to improve type safety and code maintainability across the test framework.
"""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
from enum import StrEnum

# =============================================================================
# HTTP ENUMS
# =============================================================================


class HttpMethod(StrEnum):
    """HTTP request methods.

    String-based enum for HTTP methods supported by Azure Functions HTTP triggers.
    """

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class ContentType(StrEnum):
    """Common HTTP content types.

    Standard MIME types used in HTTP request/response headers.
    """

    JSON = "application/json"
    FORM_URLENCODED = "application/x-www-form-urlencoded"
    MULTIPART_FORM_DATA = "multipart/form-data"
    OCTET_STREAM = "application/octet-stream"
    TEXT_PLAIN = "text/plain"
    TEXT_HTML = "text/html"


# =============================================================================
# AZURE RESOURCE ENUMS
# =============================================================================


class AzureProvider(StrEnum):
    """Azure resource provider names.

    Microsoft Azure resource providers used in resource IDs and event sources.
    """

    STORAGE = "Microsoft.Storage"
    EVENT_GRID = "Microsoft.EventGrid"
    SERVICE_BUS = "Microsoft.ServiceBus"
    WEB = "Microsoft.Web"
    TEST = "Microsoft.Test"


# =============================================================================
# EVENT GRID ENUMS
# =============================================================================


class EventGridEventType(StrEnum):
    """Azure Event Grid system and custom event types.

    Standard event types published by Azure services via Event Grid.
    """

    # Storage events
    BLOB_CREATED = "Microsoft.Storage.BlobCreated"
    BLOB_DELETED = "Microsoft.Storage.BlobDeleted"
    BLOB_RENAMED = "Microsoft.Storage.BlobRenamed"
    DIRECTORY_CREATED = "Microsoft.Storage.DirectoryCreated"
    DIRECTORY_DELETED = "Microsoft.Storage.DirectoryDeleted"

    # Custom/test events
    TEST_EVENT = "Test.Event"
    CUSTOM_EVENT = "Custom.Application.Event"


# =============================================================================
# BLOB STORAGE ENUMS
# =============================================================================


class BlobOperation(StrEnum):
    """Azure Blob Storage API operations.

    Operations that can be performed on blobs, used in Event Grid event data.
    """

    PUT_BLOB = "PutBlob"
    DELETE_BLOB = "DeleteBlob"
    COPY_BLOB = "CopyBlob"
    SNAPSHOT_BLOB = "SnapshotBlob"


class BlobType(StrEnum):
    """Azure Blob Storage blob types.

    The three types of blobs supported by Azure Blob Storage.
    """

    BLOCK_BLOB = "BlockBlob"
    PAGE_BLOB = "PageBlob"
    APPEND_BLOB = "AppendBlob"


# =============================================================================
# TIMER TRIGGER ENUMS
# =============================================================================


class ScheduleStatusKey(StrEnum):
    """Timer trigger schedule status dictionary keys.

    Keys used in the schedule_status dictionary for timer triggers.
    """

    LAST = "Last"
    NEXT = "Next"
    LAST_UPDATED = "LastUpdated"
