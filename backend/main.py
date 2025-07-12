
import json
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Optional
import uuid

load_dotenv()

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory user store for demo (replace with DB in production)
users_db = {}
user_sessions = {}  # session_token: username

class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserProfile(BaseModel):
    username: str
    favorites: List[str] = []  # list of parking lot names
    search_history: List[str] = []

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    username = user_sessions.get(token)
    if not username or username not in users_db:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return users_db[username]

# --- User Registration ---
@app.post("/register")
def register(user: UserRegister):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Username already exists")
    users_db[user.username] = {
        "username": user.username,
        "password": user.password,  # In production, hash this!
        "favorites": [],
        "search_history": []
    }
    return {"message": "User registered successfully"}

# --- User Login ---
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    # Generate a simple session token
    token = str(uuid.uuid4())
    user_sessions[token] = form_data.username
    return {"access_token": token, "token_type": "bearer"}

# --- Get User Profile ---
@app.get("/profile", response_model=UserProfile)
def get_profile(current_user: dict = Depends(get_current_user)):
    return UserProfile(
        username=current_user["username"],
        favorites=current_user["favorites"],
        search_history=current_user["search_history"]
    )

# --- Add/Remove Favorite Parking Lot ---
@app.post("/favorite/{lot_name}")
def add_favorite(lot_name: str, current_user: dict = Depends(get_current_user)):
    if lot_name not in current_user["favorites"]:
        current_user["favorites"].append(lot_name)
    return {"message": f"Added {lot_name} to favorites"}

@app.delete("/favorite/{lot_name}")
def remove_favorite(lot_name: str, current_user: dict = Depends(get_current_user)):
    if lot_name in current_user["favorites"]:
        current_user["favorites"].remove(lot_name)
    return {"message": f"Removed {lot_name} from favorites"}

# --- Add to Search History ---
@app.post("/search_history")
def add_search_history(query: str, current_user: dict = Depends(get_current_user)):
    current_user["search_history"].append(query)
    # Optionally limit history length
    if len(current_user["search_history"]) > 20:
        current_user["search_history"] = current_user["search_history"][-20:]
    return {"message": "Search history updated"}

class ParkingLot(BaseModel):
    name: str
    lat: float
    lng: float
    price: int
    spaces: int
    eletric: bool

@app.get("/")
async def read_root():
    return {"message": "success"} 

@app.post("/save")
def save(lot: ParkingLot):
    data = []
    with open("../parking_data.json", "r") as file:
        data = json.load(file)
        data.append(lot.dict())
    with open("../parking_data.json", "w") as file:
        json.dump(data, file, indent=4)
    return {"message": "Parking lot saved successfully"}

@app.get("/getsavedlots")
def get_saved_lots():
    try:
        with open("../parking_data.json", "r") as file:
            data = json.load(file)
        return {"saved_lots": data}
    except FileNotFoundError:
        return {"message": "No saved parking lots found"}
        

