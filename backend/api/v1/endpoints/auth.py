import re
from datetime import datetime, timedelta
from typing import List

from core.config import JWT_CONFIG
from core.database import get_db_session_dependency
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from models.models import User
from pydantic import BaseModel, EmailStr
from services.auth.email_service import EmailService
from services.auth.user_service import UserService
from sqlalchemy.orm import Session

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
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="/api/auth/login")),
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


def get_admin_user(current_user: User = Depends(get_current_user)):
    """
    管理员权限验证函数
    只有管理员才能访问的接口使用此依赖
    """
    # 直接检查 is_admin 是否等于 1，避免访问已分离对象的属性
    if current_user.is_admin != 1:
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
        return {"msg": "注册成功"}
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
        return {"msg": "验证码已发送"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/email-preview-template")
def get_email_preview_template():
    """获取邮件预览模板（仅供前端预览使用）"""
    # 生成一个示例验证码用于展示
    sample_code = "123456"
    return {"html": EmailService.get_email_template(sample_code)}


@router.post("/login")
def login(data: LoginModel):
    if not UserService.verify_password(data.email, data.password):
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    access_token = create_access_token({"sub": data.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/forgot")
def forgot(data: ForgotModel):
    code = EmailService.gen_and_store_code(data.email)
    try:
        EmailService.send_code(data.email, code)
        return {"msg": "验证码已发送"}
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
        return {"msg": "密码重置成功"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/me")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    获取当前登录用户信息
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "is_admin": bool(current_user.is_admin == 1),
        "is_active": bool(current_user.is_active == 1),
        "created_at": str(current_user.created_at) if current_user.created_at else None,
    }


@router.get("/users", response_model=List[UserOut])
def get_users(skip: int = 0, limit: int = 100, current_user: User = Depends(get_admin_user)):
    """
    获取所有用户列表（仅管理员）
    """
    users = UserService.get_all_users()
    # 简单的转换，实际项目中可以使用 AutoMapper 或 Pydantic 的 from_orm
    result = []
    for u in users:
        result.append(
            {
                "id": u.id,
                "email": u.email,
                "username": u.username,
                "is_admin": u.is_admin == 1,
                "is_active": u.is_active == 1,
                "created_at": u.created_at,
            }
        )
    return result


@router.delete("/users/{user_id}")
def delete_user(user_id: int, current_user: User = Depends(get_admin_user)):
    """
    删除用户（仅管理员）
    """
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除自己")

    try:
        UserService.delete_user(user_id)
        return {"msg": "用户已删除"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
