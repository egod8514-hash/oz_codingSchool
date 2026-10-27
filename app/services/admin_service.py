from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import UserModel
from app.core.enum.enum_department import DepartmentEnum
from app.core.enum.enum_role import RoleEnum


async def get_users(
    db: AsyncSession,
    search: str | None = None,
    department: DepartmentEnum | None = None,
):
    query = select(UserModel).where(
        UserModel.is_deleted.is_(False)
    )

    if search:
        query = query.where(
            UserModel.email.contains(search)
            | UserModel.name.contains(search)
        )

    if department:
        query = query.where(
            UserModel.department == department
        )

    result = await db.execute(query)
    users = result.scalars().all()

    return users


async def update_user_role(
    db: AsyncSession,
    user_id: int,
    role: RoleEnum,
):
    query = select(UserModel).where(
        UserModel.id == user_id,
        UserModel.is_deleted.is_(False),
    )

    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        return None

    user.role = role

    await db.commit()
    await db.refresh(user)

    return user