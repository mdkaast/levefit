from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.deps import current_user
from app.models import Character, User
from app.schemas import (
    AuthRequest,
    CharacterCreate,
    CharacterOut,
    MeOut,
    TokenResponse,
    UserOut,
)
from app.security import InvalidInitData, InvalidToken, create_access_token, validate_init_data

router = APIRouter()


@router.post("/auth/telegram", response_model=TokenResponse)
def auth_telegram(body: AuthRequest, db: Session = Depends(get_db)) -> TokenResponse:
    try:
        tg_user = validate_init_data(
            body.init_data, settings.bot_token, settings.init_data_max_age_s
        )
    except InvalidInitData:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid init data") from None

    telegram_id = int(tg_user["id"])
    user = db.scalar(select(User).where(User.telegram_id == telegram_id))
    if user is None:
        user = User(telegram_id=telegram_id)
        db.add(user)
    user.username = tg_user.get("username")
    user.locale = tg_user.get("language_code")
    db.commit()

    try:
        token = create_access_token(user.id, settings.app_secret, settings.access_token_ttl_s)
    except InvalidToken:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "server misconfigured") from None
    return TokenResponse(access_token=token, expires_in=settings.access_token_ttl_s)


@router.get("/me", response_model=MeOut)
def me(user: User = Depends(current_user)) -> MeOut:
    return MeOut(
        user=UserOut.model_validate(user),
        character=CharacterOut.model_validate(user.character) if user.character else None,
    )


@router.post("/characters", response_model=CharacterOut, status_code=status.HTTP_201_CREATED)
def create_character(
    body: CharacterCreate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> Character:
    if user.character is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "character already exists")
    character = Character(user_id=user.id, **body.model_dump())
    db.add(character)
    db.commit()
    return character
