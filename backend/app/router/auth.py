from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.model.user import User
from app.schema.auth import UserSignup, UserLogin, Token
from app.service.auth_service import AuthService
from app.service.dependencies import get_database

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=Token, status_code=201)
def signup(payload: UserSignup, db: Session = Depends(get_database)) -> Token:
    auth_service = AuthService(db)
    existing_user = auth_service.get_user_by_email(payload.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        password_hash=auth_service.get_password_hash(payload.password),
        name=payload.name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = auth_service.create_access_token(data={"sub": str(user.id)})
    return Token(token=access_token, user_id=user.id)


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_database)) -> Token:
    auth_service = AuthService(db)
    user = auth_service.get_user_by_email(payload.email)
    if not user or not auth_service.verify_password(
        payload.password, user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth_service.create_access_token(data={"sub": str(user.id)})
    return Token(token=access_token, user_id=user.id)
