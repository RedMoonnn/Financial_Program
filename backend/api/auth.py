from fastapi import APIRouter, HTTPException, Body, Depends
from services.services import UserService, EmailService
from pydantic import BaseModel, EmailStr
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
import os
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/auth", tags=["auth"])

SECRET_KEY = os.getenv('JWT_SECRET', 'secret')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="/api/auth/login"))):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="无效token")
        user = UserService.get_user(email)
        if not user:
            raise HTTPException(status_code=401, detail="用户不存在")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="token无效或过期")

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

@router.post("/register")
def register(data: RegisterModel):
    if not EmailService.verify_code(data.email, data.code):
        raise HTTPException(status_code=400, detail="验证码错误或已过期")
    try:
        UserService.register(data.email, data.password)
        return {"msg": "注册成功"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/send_code")
def send_code(data: ForgotModel):
    code = EmailService.gen_and_store_code(data.email)
    try:
        EmailService.send_code(data.email, code)
        return {"msg": "验证码已发送"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset")
def reset(data: ResetModel):
    if not EmailService.verify_code(data.email, data.code):
        raise HTTPException(status_code=400, detail="验证码错误或已过期")
    try:
        UserService.set_password(data.email, data.new_password)
        return {"msg": "密码重置成功"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 