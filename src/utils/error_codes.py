"""
Unified Error Codes and Response Format.
Provides standardized error handling across ECOMATS tools.
"""

from enum import Enum
from typing import Any, Dict, Optional
import json


class ErrorCode(Enum):
    """Standard error codes for ECOMATS tools."""
    SUCCESS = "S000"
    
    # Parameter errors (E1xx)
    MISSING_PARAM = "E101"
    INVALID_PARAM = "E102"
    
    # Feature errors (E2xx)
    NOT_IMPLEMENTED = "E201"
    NOT_SUPPORTED = "E202"
    
    # API errors (E3xx)
    API_ERROR = "E301"
    API_TIMEOUT = "E302"
    API_RATE_LIMIT = "E303"
    
    # Validation errors (E4xx)
    VALIDATION_ERROR = "E401"
    DATA_NOT_FOUND = "E402"


def success_response(data: Any, meta: Optional[Dict] = None) -> Dict:
    """
    Create a standardized success response.
    
    Args:
        data: Response data
        meta: Optional metadata
    
    Returns:
        Standardized success response dict
    """
    response = {
        "success": True,
        "data": data
    }
    if meta:
        response["meta"] = meta
    return response


def error_response(
    code: ErrorCode, 
    message: str, 
    details: Optional[Dict] = None
) -> Dict:
    """
    Create a standardized error response.
    
    Args:
        code: ErrorCode enum value
        message: Human-readable error message
        details: Optional additional error details
    
    Returns:
        Standardized error response dict
    """
    response = {
        "success": False,
        "error_code": code.value,
        "error_message": message
    }
    if details:
        response["details"] = details
    return response


def error_json(
    code: ErrorCode, 
    message: str, 
    details: Optional[Dict] = None
) -> str:
    """
    Create a JSON string error response (for tool returns).
    
    Args:
        code: ErrorCode enum value
        message: Human-readable error message
        details: Optional additional error details
    
    Returns:
        JSON string of error response
    """
    return json.dumps(
        error_response(code, message, details), 
        ensure_ascii=False
    )
