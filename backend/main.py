import json
from fastapi import FastAPI
from dotenv import load_dotenv
from pydantic import BaseModel

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
        

