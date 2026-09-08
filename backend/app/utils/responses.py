"""
Helpers to build the consistent {success, message, data} / {success, message, error}
response envelope used across every AgroEye endpoint.
"""
from fastapi.responses import JSONResponse
from fastapi import status


def success_response(message: str, data=None, status_code: int = status.HTTP_200_OK):
    return JSONResponse(status_code=status_code, content={"success": True, "message": message, "data": data})


def error_response(message: str, error: str, status_code: int = status.HTTP_400_BAD_REQUEST):
    return JSONResponse(status_code=status_code, content={"success": False, "message": message, "error": error})
