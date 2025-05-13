from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Annotated
from models import LocationModel, InterestModel, FullInterestModel, UserModel, UserUpdateModel
from models import async_session, User
import requests as rq

app = FastAPI()

origins = [
    "http://localhost:5173",
    "https://tribeappf.netlify.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       
    allow_credentials=False,      
    allow_methods=["*"],
    allow_headers=["*"],
)


tg_link = "https://t.me/"

@app.get("/authentication/{username}", response_model=UserModel)
async def make_authentication(username: str):
    user = await get_my_user(username)  # Use actual async logic here
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/edit/{username}", response_model=UserModel)
async def get_my_user(username: str):
    my_user = await rq.get_my_user(tg_link+username)
    return my_user

@app.post("/edit_user", response_model=UserUpdateModel)
async def change_user_info(user: UserUpdateModel):
    await rq.change_user_info(user)
    return user

@app.post("/edit_interest/{username}", response_model=InterestModel)
async def add_interest(interest: InterestModel, username: str):
    my_user = await rq.get_my_user(tg_link+username)
    await rq.add_interest(interest, my_user)
    return interest

@app.post("/remove_interest/{interest_id}")
async def remove_interest(interest_id: int):
    interest = await rq.remove_interest(interest_id)
    if not interest:
        raise HTTPException(status_code=404, detail="Interest not found")
    return {"message": "Interest successfully removed", "interest_id": interest_id}

@app.get("/search/{user_id}/{username}", response_model=UserModel)
async def get_user_by_id(user_id: int, username: str):
    return await rq.get_user_by_id(user_id, username)

@app.get("/likes/{username}", response_model=List[UserUpdateModel])
async def get_likes(username: str):
    my_user = await rq.get_my_user(tg_link+username)
    return await rq.get_my_likes(my_user)

@app.post("/like_user/{username}", response_model=UserUpdateModel)
async def add_like(user: UserUpdateModel, username: str):
    my_user = await rq.get_my_user(tg_link+username)
    await rq.add_like(user, my_user)
    return user

@app.get("/likes-by-id/{user_id}", response_model=UserModel)
async def get_likes_user_by_id(user_id: int):
    print("user_id: ", user_id)
    return await rq.get_user_by_id(user_id-1)