from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.admin import is_admin
from app.config import settings
from app.db import get_db
from app.deps import current_user
from app.game import change_mode, streak_view, utcnow
from app.models import BodyMetric, Character, User
from app.schemas import (
    AuthRequest,
    CharacterCreate,
    CharacterOut,
    CharacterPatch,
    MeOut,
    StreakOut,
    TokenResponse,
    UserOut,
    UserPatch,
)
from app.security import InvalidInitData, InvalidToken, create_access_token, validate_init_data

router = APIRouter()


def _upsert_user(db: Session, telegram_id: int, tg_user: dict) -> User:
    """Находит или создаёт пользователя; два одновременных первых входа не должны падать."""
    for _ in range(2):
        user = db.scalar(select(User).where(User.telegram_id == telegram_id))
        if user is None:
            user = User(telegram_id=telegram_id)
            db.add(user)
        user.username = tg_user.get("username")
        user.locale = tg_user.get("language_code")
        try:
            db.commit()
            return user
        except IntegrityError:  # параллельный запрос успел создать пользователя
            db.rollback()
    raise HTTPException(status.HTTP_409_CONFLICT, "concurrent login, try again")


@router.post("/auth/telegram", response_model=TokenResponse)
def auth_telegram(body: AuthRequest, db: Session = Depends(get_db)) -> TokenResponse:
    try:
        tg_user = validate_init_data(
            body.init_data, settings.bot_token, settings.init_data_max_age_s
        )
    except InvalidInitData:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid init data") from None

    telegram_id = int(tg_user["id"])
    user = _upsert_user(db, telegram_id, tg_user)

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
        is_admin=is_admin(user),
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
        user.reminders_today = 0
    if "mode" in changes:
        change_mode(db, user, changes.pop("mode"), utcnow().date())
    for field, value in changes.items():
        setattr(user, field, value)
    db.commit()
    return user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(user: User = Depends(current_user), db: Session = Depends(get_db)) -> None:
    """Полностью удаляет пользователя; связанные данные удаляются каскадом в БД."""
    db.delete(user)
    db.commit()


@router.post("/characters", response_model=CharacterOut, status_code=status.HTTP_201_CREATED)
def create_character(
    body: CharacterCreate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> Character:
    if user.character is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "character already exists")
    data = body.model_dump(exclude={"age", "weight_kg"})
    now = utcnow()
    character = Character(
        user_id=user.id, birth_year=now.year - body.age if body.age else None, **data
    )
    db.add(character)
    if body.weight_kg is not None:  # стартовый вес — первая точка графика, без XP
        db.add(BodyMetric(user_id=user.id, date=now.date(), weight_kg=body.weight_kg))
    db.commit()
    return character


@router.patch("/me/character", response_model=CharacterOut)
def patch_character(
    body: CharacterPatch, user: User = Depends(current_user), db: Session = Depends(get_db)
) -> Character:
    """Акцент на мышцы меняется в профиле в любое время; план учтёт его со следующей недели."""
    if user.character is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "character not found")
    if body.target_muscles is not None:
        user.character.target_muscles = body.target_muscles
    if body.silhouette is not None:
        user.character.silhouette = body.silhouette
    db.commit()
    return user.character
