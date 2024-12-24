# api/virtuals.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pymongo.collection import Collection
from models.virtual import VirtualSport
from schemas.virtual import VirtualSportResponse, VirtualSportListResponse
from services.database import get_db

router = APIRouter()

@router.get("/", response_model=VirtualSportListResponse, summary="Retrieve all virtual sports")
async def get_all_virtual_sports(
    category: Optional[str] = None,
    status: Optional[str] = "active",
    db: Collection = Depends(get_db)
):
    """
    Retrieve a list of all virtual sports. 
    - Optional filters: `category`, `status`
    """
    query = {}
    if category:
        query["category"] = category
    if status:
        query["status"] = status

    virtual_sports = db.virtual_sports.find(query)
    return VirtualSportListResponse(data=list(virtual_sports))

@router.get("/{virtual_sport_id}", response_model=VirtualSportResponse, summary="Retrieve a specific virtual sport")
async def get_virtual_sport_by_id(virtual_sport_id: str, db: Collection = Depends(get_db)):
    """
    Retrieve details of a specific virtual sport by its ID.
    """
    virtual_sport = db.virtual_sports.find_one({"_id": virtual_sport_id})
    if not virtual_sport:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Virtual sport not found")
    
    return VirtualSportResponse(data=virtual_sport)

@router.get("/odds/{odds}", response_model=VirtualSportListResponse, summary="Filter virtual sports by odds")
async def get_virtual_sports_by_odds(
    odds: float, db: Collection = Depends(get_db)
):
    """
    Filter virtual sports by a specified `odds` value.
    """
    virtual_sports = db.virtual_sports.find({"odds": {"$lte": odds}})
    return VirtualSportListResponse(data=list(virtual_sports))
