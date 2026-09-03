from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from datetime import datetime


class EmailAlreadyRegisteredException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail="Email đã được đăng ký")


class InvalidCredentialsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email hoặc mật khẩu không chính xác", headers={"WWW-Authenticate": "Bearer"})


class AccountLockedException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="Tài khoản đã bị khóa")


class InvalidTokenException(HTTPException):
    def __init__(self, detail: str = "Thông tin xác thực không hợp lệ"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, headers={"WWW-Authenticate": "Bearer"})


class InvalidRefreshTokenException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token không hợp lệ hoặc đã hết hạn", headers={"WWW-Authenticate": "Bearer"})


class AdminRequiredException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn cần có quyền quản trị viên để thực hiện thao tác này")


class TooManyLoginAttemptsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Bạn đã đăng nhập quá nhiều lần. Vui lòng thử lại sau")


class UserNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy người dùng")


class ClubNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy câu lạc bộ")


class ClubOwnerRequiredException(HTTPException):
    def __init__(self, action: str = "thực hiện thao tác này"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=f"Chỉ chủ câu lạc bộ mới được phép {action}")


class ClubMemberRequiredException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn phải là thành viên của câu lạc bộ để thực hiện thao tác này")


class ActivityPermissionException(HTTPException):
    def __init__(self, action: str = "thực hiện thao tác này"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=f"Bạn không có quyền {action} activity này")


class ActivityAssigneeNotMemberException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="User này không thuộc chiến dịch")


class ActivityNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy activity")


class UserAlreadyMemberException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="Người dùng đã là thành viên của câu lạc bộ")


async def http_exception_handler(request: Request, exc: HTTPException):
    content = {
        "success": False,
        "status_code": exc.status_code,
        "error": "Lỗi yêu cầu",
        "message": exc.detail,
        "method": request.method,
        "path": request.url.path,
    }
    if exc.status_code == status.HTTP_404_NOT_FOUND:
        content["timestamp"] = datetime.now().isoformat()
    return JSONResponse(status_code=exc.status_code, content=content)