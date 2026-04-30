from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.db.users import User
from backend.modules.auth import service
from backend.modules.auth.deps import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: str
    name: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    email: str
    name: str


class MeResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    existing = await service.get_user_by_email(db, payload.email)
    if existing:
        existing.password_hash = service.hash_password(payload.password)
        await db.commit()
        await db.refresh(existing)
        token = service.create_access_token(str(existing.id), existing.email)
        return TokenResponse(access_token=token, email=existing.email, name=existing.name)
    user = await service.register_user(db, payload.email, payload.name, payload.password)
    token = service.create_access_token(str(user.id), user.email)
    return TokenResponse(access_token=token, email=user.email, name=user.name)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    user = await service.authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверная почта или пароль")
    token = service.create_access_token(str(user.id), user.email)
    return TokenResponse(access_token=token, email=user.email, name=user.name)


@router.get("/me", response_model=MeResponse)
async def me(current_user: User = Depends(get_current_user)) -> MeResponse:
    return MeResponse(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        role=current_user.role.value,
    )
