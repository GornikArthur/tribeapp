from sqlalchemy import String, Integer, BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from typing import Optional
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Annotated

URL_DATABASE = 'postgresql+asyncpg://postgres:KORNPwGdODRBHtwoOJPSVpIKMwsaTuSc@hopper.proxy.rlwy.net:33401/railway'

engine = create_async_engine(url=URL_DATABASE, echo=True)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)

class LocationModel(BaseModel):
    Country: str
    City: str

class InterestModel(BaseModel):
    Title: str
    Description: str

class FullInterestModel(InterestModel):
    Interest_id: int

class UserModel(BaseModel):
    User_id: int
    Name: str
    Age: int
    Location: LocationModel
    TelegramLink: str
    Interests: List[FullInterestModel]
    #LikedBy: List[User]

class UserUpdateModel(BaseModel):
    User_id: int
    Name: str
    Age: int
    TelegramLink: str
    Location: LocationModel

class Base(AsyncAttrs, DeclarativeBase):
    pass

class Location(Base):
    __tablename__ = 'Locations'

    Location_id: Mapped[int] = mapped_column(primary_key=True)
    Country: Mapped[str] = mapped_column(String(128))
    City: Mapped[str] = mapped_column(String(128))

class User(Base):
    __tablename__ = 'Users'

    User_id: Mapped[int] = mapped_column(primary_key=True)
    TelegramLink: Mapped[str] = mapped_column(String(128))
    Name: Mapped[str] = mapped_column(String(128))
    Age: Mapped[int] = mapped_column(Integer)
    Location_id: Mapped[Optional[int]] = mapped_column(ForeignKey('Locations.Location_id'), nullable=True)

class Interest(Base):
    __tablename__ = 'Interests'

    Interest_id: Mapped[int] = mapped_column(primary_key=True)
    User_id: Mapped[int] = mapped_column(ForeignKey('Users.User_id'))
    Title: Mapped[str] = mapped_column(String(128))
    Description: Mapped[str] = mapped_column(String(512))

class UserLike(Base):
    __tablename__ = 'User_likes'

    Liker_id: Mapped[int] = mapped_column(ForeignKey('Users.User_id'), primary_key=True)
    Liked_id: Mapped[int] = mapped_column(ForeignKey('Users.User_id'), primary_key=True)

async def init_db():
    async with engine.begin() as con:
        await con.run_sync(Base.metadata.create_all)
