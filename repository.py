from sqlalchemy.ext.asyncio import AsyncSession

from models import User


async def get_user(session: AsyncSession, telegram_id: int) -> User | None:
    return await session.get(User, telegram_id)


async def save_user(session: AsyncSession, telegram_id: int, login: str, token: str) -> None:
    user = await session.get(User, telegram_id)
    if user is None:
        session.add(User(telegram_id=telegram_id, tw_login=login, tw_token=token))
    else:
        user.tw_login = login
        user.tw_token = token
    await session.commit()
