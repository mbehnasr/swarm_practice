from fastapi import FastAPI, HTTPException, Body, Path
from pydantic import BaseModel
import json
import secrets

app = FastAPI()

USERS_FILE = "users.json"

class User(BaseModel):
    username: str
    password: str

class TokenValidationRequest(BaseModel):
    token: str

@app.post("/signup")
def signup(user: User):
    try:
        with open(USERS_FILE, "r") as file:
            users = json.load(file)
    except FileNotFoundError:
        users = {}

    if user.username in users:
        raise HTTPException(status_code=400, detail="Username already exists")

    users[user.username] = {"username": user.username, "password": user.password}

    with open(USERS_FILE, "w") as file:
        json.dump(users, file)

    return {"message": "User created successfully"}


@app.post("/login")
def login(user: User):
    try:
        with open(USERS_FILE, "r") as file:
            users = json.load(file)
    except FileNotFoundError:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if user.username not in users or users[user.username]["password"] != user.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if "token" in users[user.username]:
        raise HTTPException(status_code=403, detail="User is already logged in")

    token = generate_token(user.username)

    users[user.username]["token"] = token

    with open(USERS_FILE, "w") as file:
        json.dump(users, file)
    return {"token": token}


def generate_token(username: str) -> str:
    token = secrets.token_hex(16)
    return token


@app.delete("/logout")
def logout(user: User):
    try:
        with open(USERS_FILE, "r") as file:
            users = json.load(file)
    except FileNotFoundError:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if user.username not in users or users[user.username]["password"] != user.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if "token" not in users[user.username]:
        raise HTTPException(status_code=400, detail="User is not logged in")

    del users[user.username]["token"]

    with open(USERS_FILE, "w") as file:
        json.dump(users, file)

    return {"message": "User logged out successfully"}



@app.get("/check_token")
def check_token(request: TokenValidationRequest):
    try:
        with open(USERS_FILE, "r") as file:
            users = json.load(file)
    except FileNotFoundError:
        raise HTTPException(status_code=401, detail="Token validation failed")

    for user in users.values():
        if "token" in user and user["token"] == request.token:
            return {"valid": True}

    raise HTTPException(status_code=401, detail="Token validation failed")

