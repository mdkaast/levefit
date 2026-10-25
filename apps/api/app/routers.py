from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.deps import current_user
from app.game import ensure_user_quests, streak_view, utcnow
from app.models import Character, User
from app.schemas import (
    AuthRequest,
    CharacterCreate,
    CharacterOut,
    MeOut,
    QuestOut,
    StreakOut,
    TokenResponse,
    UserOut,
    UserPatch,
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
def me(user: User = Depends(current_user), db: Session = Depends(get_db)) -> MeOut:
    character = user.character
    return MeOut(
        user=UserOut.model_validate(user),
        character=CharacterOut.model_validate(character) if character else None,
        streak=StreakOut(**streak_view(db, user, utcnow().date())) if character else None,
    )


@router.patch("/me", response_model=UserOut)
def patch_me(
    body: UserPatch, user: User = Depends(current_user), db: Session = Depends(get_db)
) -> User:
    changes = {k: v for k, v in body.model_dump(exclude_unset=True).items() if v is not None}
    if changes.keys() & {"reminder_time", "timezone"}:
        user.last_reminder_date = None  # новое время может ещё наступить сегодня
    for field, value in changes.items():
        setattr(user, field, value)
    db.commit()
    return user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(user: User = Depends(current_user), db: Session = Depends(get_db)) -> None:
    """Полностью удаляет пользователя; связанные данные удаляются каскадом в БД."""
    db.delete(user)
    db.commit()


@router.get("/quests", response_model=list[QuestOut])
def quests(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[QuestOut]:
    items = ensure_user_quests(db, user.id, utcnow().date())
    db.commit()
    return [
        QuestOut(
            id=uq.id,
            code=uq.quest.code,
            kind=uq.quest.kind,
            progress=uq.progress,
            target=uq.quest.condition["target"],
            xp_reward=uq.quest.xp_reward,
            status=uq.status,
        )
        for uq in items
    ]


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
