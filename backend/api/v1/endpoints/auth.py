import re
from datetime import datetime, timedelta

from core.config import JWT_CONFIG
from core.database import get_db_session_dependency
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from models.models import User
from pydantic import BaseModel, EmailStr
from services.auth.email_service import EmailService
from services.auth.user_service import UserService
from services.exceptions import UserServiceException
from sqlalchemy.orm import Session

from api.middleware import APIResponse

router = APIRouter(prefix="/auth", tags=["auth"])


# 从配置获取JWT设置
SECRET_KEY = JWT_CONFIG["secret_key"]
ALGORITHM = JWT_CONFIG["algorithm"]
ACCESS_TOKEN_EXPIRE_MINUTES = JWT_CONFIG["access_token_expire_minutes"]


def create_access_token(data: dict, expires_delta: timedelta = None):
    """创建JWT访问令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")),
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="无效token")
        user = UserService.get_user(email)
        if not user:
            raise HTTPException(status_code=401, detail="用户不存在")
        return user
    except JWTError as e:
        raise HTTPException(status_code=401, detail="token无效或过期") from e


def is_admin_user(user: User) -> bool:
    """
    检查用户是否为管理员（辅助函数）

    Args:
        user: 用户对象

    Returns:
        True if admin, False otherwise
    """
    return user.is_admin == 1


def get_admin_user(current_user: User = Depends(get_current_user)):
    """
    管理员权限验证函数（统一权限检查）
    只有管理员才能访问的接口使用此依赖
    """
    if not is_admin_user(current_user):
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user


class RegisterModel(BaseModel):
    email: EmailStr
    password: str
    code: str


class LoginModel(BaseModel):
    email: EmailStr
    password: str


class ForgotModel(BaseModel):
    email: EmailStr


class ResetModel(BaseModel):
    email: EmailStr
    code: str
    new_password: str


class UpdateUsernameModel(BaseModel):
    username: str | None = None


class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str | None = None
    is_admin: bool
    is_active: bool
    created_at: datetime | None = None

    class Config:
        orm_mode = True


@router.post("/register")
def register(data: RegisterModel):
    if not EmailService.verify_code(data.email, data.code):
        raise HTTPException(status_code=400, detail="验证码错误或已过期")
    try:
        UserService.register(data.email, data.password)
        return APIResponse.success(message="注册成功")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/send_code")
def send_code(data: ForgotModel, session: Session = Depends(get_db_session_dependency)):
    """发送验证码（注册时使用）"""
    # 注册时如邮箱已注册则直接返回错误
    user = session.query(User).filter_by(email=data.email).first()
    if user:
        raise HTTPException(status_code=400, detail="该邮箱已注册，请直接登录或找回密码")
    code = EmailService.gen_and_store_code(data.email)
    try:
        EmailService.send_code(data.email, code)
        return APIResponse.success(message="验证码已发送")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/login")
def login(data: LoginModel):
    if not UserService.verify_password(data.email, data.password):
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    access_token = create_access_token({"sub": data.email})
    return APIResponse.success(data={"access_token": access_token, "token_type": "bearer"})


@router.post("/forgot")
def forgot(data: ForgotModel):
    code = EmailService.gen_and_store_code(data.email)
    try:
        EmailService.send_code(data.email, code)
        return APIResponse.success(message="验证码已发送")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/reset")
def reset(data: ResetModel):
    # 新密码复杂度校验
    if not re.match(r"^(?=.*[a-z])(?=.*[A-Z]).{6,20}$", data.new_password):
        raise HTTPException(status_code=400, detail="新密码需包含大小写字母，长度6-20位")
    if not EmailService.verify_code(data.email, data.code):
        raise HTTPException(status_code=400, detail="验证码错误或已过期")
    try:
        UserService.set_password(data.email, data.new_password)
        return APIResponse.success(message="密码重置成功")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/me")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    获取当前登录用户信息
    """
    user_data = UserService.user_to_dict(current_user)
    return APIResponse.success(data=user_data, message="获取用户信息成功")


@router.get("/users")
def get_users(current_user: User = Depends(get_admin_user)):
    """
    获取所有用户列表（仅管理员）
    """
    users = UserService.get_all_users()
    result = [UserService.user_to_dict(u) for u in users]
    # 统一使用 APIResponse 格式
    return APIResponse.success(data=result, message="获取用户列表成功")


@router.delete("/users/{user_id}")
def delete_user(user_id: int, current_user: User = Depends(get_admin_user)):
    """
    删除用户（仅管理员）
    """
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除自己")

    try:
        UserService.delete_user(user_id)
        return APIResponse.success(message="用户已删除")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.put("/me/username")
def update_username(data: UpdateUsernameModel, current_user: User = Depends(get_current_user)):
    """
    更新当前用户的用户名
    """
    try:
        # 处理空字符串：将空字符串转换为 None
        username = data.username
        if username is not None:
            username = username.strip()
            if username == "":
                username = None

        # 验证用户名长度（如果提供）
        if username is not None and len(username) > 64:
            raise HTTPException(status_code=400, detail="用户名长度不能超过64个字符")

        UserService.update_username(current_user.id, username)
        # 重新获取用户信息
        updated_user = UserService.get_user(current_user.email)
        user_data = UserService.user_to_dict(updated_user)
        return APIResponse.success(data=user_data, message="用户名更新成功")
    except UserServiceException as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新用户名失败: {str(e)}") from e
