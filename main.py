from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Annotated
from models import LocationModel, InterestModel, FullInterestModel, UserModel, UserUpdateModel
from models import async_session, User
import requests as rq

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ethernet-down-baseball-carried.trycloudflare.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

tg_link = "https://t.me/arturgornik"

@app.get("/authentication", response_model=UserModel)
async def make_authentication():
    my_user = await rq.get_my_user(tg_link)
    return my_user

@app.get("/edit", response_model=UserModel)
async def get_my_user():
    my_user = await rq.get_my_user(tg_link)
    return my_user

@app.post("/edit_user", response_model=UserUpdateModel)
async def change_user_info(user: UserUpdateModel):
    await rq.change_user_info(user)
    return user

@app.post("/edit_interest", response_model=InterestModel)
async def add_interest(interest: InterestModel):
    my_user = await rq.get_my_user(tg_link)
    await rq.add_interest(interest, my_user)
    return interest

@app.post("/remove_interest/{interest_id}")
async def remove_interest(interest_id: int):
    interest = await rq.remove_interest(interest_id)
    if not interest:
        raise HTTPException(status_code=404, detail="Interest not found")
    return {"message": "Interest successfully removed", "interest_id": interest_id}

@app.get("/search/{user_id}", response_model=UserModel)
async def get_user_by_id(user_id: int):
    return await rq.get_user_by_id(user_id)

@app.get("/likes", response_model=List[UserUpdateModel])
async def get_likes():
    my_user = await rq.get_my_user(tg_link)
    return await rq.get_my_likes(my_user)

@app.post("/like_user", response_model=UserUpdateModel)
async def add_like(user: UserUpdateModel):
    my_user = await rq.get_my_user(tg_link)
    await rq.add_like(user, my_user)
    return user

@app.get("/likes/{user_id}", response_model=UserModel)
async def get_likes_user_by_id(user_id: int):
    print("user_id: ", user_id)
    return await rq.get_user_by_id(user_id-1)