# services/virtual.py

from bson import ObjectId
from pymongo.collection import Collection
from pydantic import BaseModel
from typing import List
from db.mongodb import get_db

class VirtualSport(BaseModel):
    id: str
    name: str
    odds: float

class VirtualService:
    
    @staticmethod
    async def get_virtual_sports(db: Collection) -> List[VirtualSport]:
        """
        Fetches all virtual sports from the get_db.
        """
        virtual_sports = await db.virtuals.find().to_list(length=None)
        return [
            VirtualSport(
                id=str(sport["_id"]),
                name=sport["name"],
                odds=sport["odds"]
            )
            for sport in virtual_sports
        ]

    @staticmethod
    async def create_virtual_sport(db: Collection, virtual_sport: VirtualSport) -> VirtualSport:
        """
        Creates a new virtual sport in the get_db.
        """
        sport_data = virtual_sport.dict(exclude_unset=True)
        result = await db.virtuals.insert_one(sport_data)
        return VirtualSport(id=str(result.inserted_id), **sport_data)
