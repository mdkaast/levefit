"""Источник продуктов за единым интерфейсом (F1).

Выбор внешней базы ещё не сделан. Сейчас работает только локальная таблица `foods`. Open Food Facts
(лицензия ODbL с обязательным открытием производных баз) и USDA FoodData Central (CC0, без
российских
брендов) можно подключить, реализовав `FoodSource`; штрихкод (F8) потребует `by_barcode`.
"""

from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Food


class FoodSource(Protocol):
    def search(self, query: str, limit: int = 30, group: str | None = None) -> list[Food]: ...

    def get(self, food_id: int) -> Food | None: ...


class LocalFoodSource:
    """Продукты из БД: общий каталог и личные продукты пользователя."""

    def __init__(self, db: Session, user_id: int) -> None:
        self.db = db
        self.user_id = user_id

    def _visible(self) -> list[Food]:
        rows = self.db.scalars(select(Food).where(Food.is_active.is_(True)).order_by(Food.name))
        return [f for f in rows if f.owner_id is None or f.owner_id == self.user_id]

    def search(self, query: str, limit: int = 30, group: str | None = None) -> list[Food]:
        # casefold в Python: lower() в SQLite не понимает кириллицу
        needle = query.strip().casefold()
        found = [
            f
            for f in self._visible()
            if (not group or f.group == group) and (not needle or needle in f.name.casefold())
        ]
        found.sort(key=lambda f: (not f.name.casefold().startswith(needle), f.name.casefold()))
        return found[:limit]

    def get(self, food_id: int) -> Food | None:
        food = self.db.get(Food, food_id)
        if food is None or not food.is_active:
            return None
        return food if food.owner_id in (None, self.user_id) else None
