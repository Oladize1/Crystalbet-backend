from fastapi import APIRouter, Depends, HTTPException, status, WebSocket
from pydantic import BaseModel, Field
from typing import List
from bson import ObjectId
from services.match import MatchService
from motor.motor_asyncio import AsyncIOMotorCollection
from db.mongodb import get_db, get_collection
from datetime import datetime
import asyncio

router = APIRouter()

class MatchResponse(BaseModel):
    id: str = Field(..., alias="_id")
    team_a: str
    team_b: str
    score: str
    status: str
    start_time: str
    markets: List[dict] = []

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            ObjectId: str
        }
async def get_live_match_updates():
    """
    Mock function to simulate live match updates.
    Replace this with actual data retrieval logic from your database or live source.
    """
    # Example data, replace with real match data fetching logic.
    return [
        {
            "_id": "64a32c12e8d7b3bcf5d5a123",
            "team_a": "Team A",
            "team_b": "Team B",
            "score": "2-1",
            "status": "ongoing",
            "start_time": datetime.now().isoformat(),
            "markets": [{"market_name": "Win", "odds": 1.5}, {"market_name": "Draw", "odds": 3.0}]
        },
        # Additional match updates can be added here.
    ]
@router.websocket("/ws/live-matches")
async def websocket_live_matches(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            match_updates = await get_live_match_updates()
            await websocket.send_json(match_updates)
            await asyncio.sleep(5)  # Adjust frequency as needed
    except Exception as e:
        await websocket.close(code=1001)  # Optional: Close WebSocket if error occurs

# Dependency to inject MatchService
def get_match_service(collection: AsyncIOMotorCollection = Depends(get_collection)):
    return MatchService(collection)

def validate_object_id(match_id: str):
    """Utility to validate and convert match_id to ObjectId if valid."""
    if not ObjectId.is_valid(match_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid match ID format")
    return ObjectId(match_id)

@router.websocket("/ws/live-matches")
async def websocket_live_matches(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            # Retrieve live match updates; ensure `get_live_match_updates` is defined.
            match_updates = await get_live_match_updates()
            await websocket.send_json(match_updates)
        except Exception as e:
            await websocket.close(code=1001)  # Optional: Close WebSocket if error occurs

@router.get("/", response_model=List[MatchResponse])
async def get_all_matches(service: MatchService = Depends(get_match_service)):
    matches = await service.get_all_matches()
    return matches

@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(match_id: str, service: MatchService = Depends(get_match_service)):
    match_object_id = validate_object_id(match_id)
    match = await service.get_match(match_object_id)
    if match is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    return match

@router.post("/", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
async def create_match(match: MatchResponse, service: MatchService = Depends(get_match_service)):
    new_match = await service.create_match(dict(match))
    return new_match

@router.put("/{match_id}", response_model=MatchResponse)
async def update_match(match_id: str, match: MatchResponse, service: MatchService = Depends(get_match_service)):
    match_object_id = validate_object_id(match_id)
    updated_match = await service.update_match(match_object_id, dict(match))
    if updated_match is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    return updated_match

@router.delete("/{match_id}", response_model=dict)
async def delete_match(match_id: str, service: MatchService = Depends(get_match_service)):
    match_object_id = validate_object_id(match_id)
    deleted = await service.delete_match(match_object_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    return {"detail": "Match deleted successfully"}

@router.get("/{match_id}/markets", response_model=List[dict])
async def get_match_markets(match_id: str, service: MatchService = Depends(get_match_service)):
    match_object_id = validate_object_id(match_id)
    match = await service.get_match(match_object_id)
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    return match.get("markets", [])
