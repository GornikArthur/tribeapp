from models import async_session, User, Interest, UserLike, Location
from models import LocationModel, InterestModel, FullInterestModel, UserModel, UserUpdateModel
from sqlalchemy import select, update, delete
from fastapi import HTTPException

def generate_myuser_data(user, location=None, interests=None):
    try:
        return {
            "User_id": user.User_id,
            "Name": user.Name,
            "Age": user.Age,
            "TelegramLink": user.TelegramLink,
            "Location": {
                "Country": location.Country if location else "Unknown",
                "City": location.City if location else "Unknown"
            },
            "Interests": [
                {"Interest_id": i.Interest_id, "Title": i.Title, "Description": i.Description}
                for i in (interests or [])
            ]
        }
    except Exception as e:
        print("Ошибка при сборке данных пользователя:", e)
        raise

async def get_my_user(telegram_link: str):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.TelegramLink == telegram_link))

        if not user:
            user = User(
                TelegramLink=telegram_link,
                Name="New User",
                Age=0,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)

        interests = (await session.scalars(select(Interest).where(Interest.User_id == user.User_id))).all()
        if user.Location_id is not None:
            location = await session.scalar(select(Location).where(Location.Location_id == user.Location_id))
        else: 
            location = None
        return generate_myuser_data(
            user=user,
            location=location,
            interests=interests,
        )

async def change_user_info(user: UserUpdateModel):
    async with async_session() as session:
        try:
            user_db = await session.scalar(select(User).where(User.User_id == user.User_id))
            if not user_db:
                raise HTTPException(status_code=404, detail="User not found")

            user_data = user.dict(exclude_unset=True)

            for key, val in user_data.items():
                if key != "Location":
                    setattr(user_db, key, val)

            if user.Location:
                location = await session.scalar(
                    select(Location).where(
                            Location.Country == user.Location.Country,
                            Location.City == user.Location.City
                        )
                )
                if not location:
                    location = Location(
                        Country=user.Location.Country,
                        City=user.Location.City
                    )
                    session.add(location)
                    await session.flush()

                user_db.Location_id = location.Location_id

            await session.commit()
            await session.refresh(user_db)

            return user_db

        except Exception as e:
            print("Ошибка при обновлении пользователя:", e)
            await session.rollback()
            raise HTTPException(status_code=500, detail="Internal Server Error")
        
async def add_interest(interest: InterestModel, my_user):
    async with async_session() as session:
        add_interest = await session.scalar(select(Interest).where(Interest.User_id == my_user["User_id"], Interest.Title == interest.Title))
        if not add_interest:
            add_interest = Interest(
                User_id=my_user["User_id"],
                Title=interest.Title,
                Description=interest.Description
            )    
            session.add(add_interest)
            await session.flush()
            await session.commit()
        else:
            add_interest.Description = interest.Description
            await session.commit()
            await session.refresh(add_interest)
        return interest
    
async def remove_interest(interest_id: int):
    async with async_session() as session:
        interest_to_delete = await session.scalar(select(Interest).where(Interest.Interest_id == interest_id))
        if interest_to_delete: 
            await session.delete(interest_to_delete)
            print("interest_to_delete:", interest_id)
            await session.flush()
            await session.commit()
        return interest_to_delete
    
async def get_user_by_id(current_id: int):
    async with async_session() as session:
        stmt = select(User).where(User.User_id > current_id).order_by(User.User_id.asc()).limit(1)
        result = await session.execute(stmt)
        user = result.scalars().first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        interests = (await session.scalars(select(Interest).where(Interest.User_id == user.User_id))).all()
        location = await session.scalar(select(Location).where(Location.Location_id == user.Location_id))
        return generate_myuser_data(
            user=user,
            location=location,
            interests=interests,
        )

async def get_my_likes(my_user):
    async with async_session() as session:
        user_likes = (await session.scalars(
            select(UserLike).where(UserLike.Liked_id == my_user["User_id"])
        )).all()

        users = []
        for like in user_likes:
            c_user = await session.scalar(select(User).where(User.User_id == like.Liker_id))
            if not c_user:
                continue
            interests = (await session.scalars(select(Interest).where(Interest.User_id == c_user.User_id))).all()
            location = await session.scalar(select(Location).where(Location.Location_id == c_user.Location_id))
            users.append(generate_myuser_data(
                user=c_user,
                location=location,
                interests=interests,
            ))

        return users

async def add_like(user: UserUpdateModel, my_user):
    async with async_session() as session:
        like = await session.scalar(select(UserLike).where(UserLike.Liker_id == my_user["User_id"], UserLike.Liked_id == user.User_id))
        if not like:
            like = UserLike(
                Liker_id = my_user["User_id"],
                Liked_id = user.User_id
            )    
            session.add(like)
            await session.flush()
            await session.commit()
        return like
