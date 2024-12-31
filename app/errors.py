from typing import Any, Callable
from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse

class LegalPadiException(Exception):
    """This is the base class for all bookly errors."""
    pass

class InvalidToken(LegalPadiException):
    """User has provided an invalid or expired token"""
    pass

class InvalidCredentials(LegalPadiException):
    """User has provided Invalid Email or Password"""
    pass

class RevokedToken(LegalPadiException):
    """User Token has been revoked, login for access"""
    pass

class AccessTokenRequired(LegalPadiException):
    """User has provided a Refresh Token where Access Token is required"""
    pass

class RefreshTokenRequired(LegalPadiException):
    """User has provided a Access Token where Refresh Token is required"""
    pass

class AccessDenied(LegalPadiException):
    """User does not have the necessary permissions to perform operation"""
    pass

class UserAlreadyExists(LegalPadiException):
    """User has provided an email for a user who already exists during signup"""
    pass

class AdminAlreadyExists(LegalPadiException):
    """Admin already exists"""
    pass

class EditorAlreadyExists(LegalPadiException):
    """Editor already exists"""
    pass

class CourseAlreadyExists(LegalPadiException):
    """Course already exists"""
    pass

class TagAlreadyExists(LegalPadiException):
    """Tag already exists"""
    pass

class TagNotFound(LegalPadiException):
    """Tag Not Found"""
    pass

class UserNotFound(LegalPadiException):
    """User Not Found"""
    pass

class CourseNotFound(LegalPadiException):
    """Course Not Found"""
    pass

class EditorNotFound(LegalPadiException):
    """Editor Not Found"""
    pass

class AdminNotFound(LegalPadiException):
    """Admin Not Found"""
    pass


def create_exception_handler(status_code:int, initial_detail: Any) -> Callable[[Request, Exception], JSONResponse]:
    async def exception_handler(request: Request, exc: LegalPadiException):
        return JSONResponse(
            content=initial_detail,
            status_code=status_code
        )
    
    return exception_handler 

def register_all_errors (app: FastAPI):
    app.add_exception_handler(
        AdminNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Admin is not found",
                "error": "Not Found"
            }
        )
    )
    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "User is not found",
                "error": "Not Found"
            }
        )
    )
    app.add_exception_handler(
        EditorNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Editor is not found",
                "error": "Not Found"
            }
        )
    )
    app.add_exception_handler(
        CourseNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Course is not found",
                "error": "Not Found"
            }
        )
    )
    app.add_exception_handler(
        AdminAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Admin already exists",
                "error": "Duplicate"
            }
        )
    )
    app.add_exception_handler(
        EditorAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Editor already exists",
                "error": "Duplicate"
            }
        )
    )
    app.add_exception_handler(
        CourseAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Course already exists",
                "error": "Duplicate"
            }
        )
    )
    app.add_exception_handler(
        UserAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "User with email already exists",
                "error": "Email cannot be duplicate"
            }
        )
    )
    app.add_exception_handler(
        TagAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "User with email already exists",
                "error": "Email cannot be duplicate"
            }
        )
    )
    app.add_exception_handler(
        AccessDenied,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "You do not have the permissions to perform this action",
                "error": "Access Denied"
            }
        )
    )
    app.add_exception_handler(
        AccessTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Provide a Valid Access Token",
                "error": "Access Token Required"
            }
        )
    )
    app.add_exception_handler(
        RefreshTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Provide a Valid Refresh Token",
                "error": "Refresh Token Required"
            }
        )
    )
    app.add_exception_handler(
        TagNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Tag is not found",
                "error": "Not Found"
            }
        )
    )
    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Credentials Invalid or Incorrect",
                "error": "Request Error"
            }
        )
    )
    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Token is Invalid",
                "error": "Token Error"
            }
        )
    )
    app.add_exception_handler(
        RevokedToken,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Token has been revoked, please Login in",
                "error": "Token Error"
            }
        )
    )
