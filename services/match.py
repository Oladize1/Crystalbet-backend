from models.match import Match
from schemas.match import MatchResponse, MatchCreate, MatchUpdate, PlaceBetRequest
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
from fastapi import HTTPException, status
from db.mongodb import get_db
from pymongo.client_session import ClientSession
import requests  # For making API calls (ensure requests package is installed)
import logging
from datetime import datetime

class MatchService:
    def __init__(self, collection: AsyncIOMotorCollection, db):
        self.collection = collection
        self.db = db  # The database should be passed as part of the initialization

    def validate_object_id(self, obj_id: str):
        if not ObjectId.is_valid(obj_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format")

    async def get_all_matches(self, page: int = 1, page_size: int = 10):
        skip = (page - 1) * page_size
        matches = []
        async for match in self.collection.find().skip(skip).limit(page_size):
            matches.append(MatchResponse(**match))
        return matches

    async def get_match_by_id(self, match_id: str):
        self.validate_object_id(match_id)
        match_data = await self.collection.find_one({"_id": ObjectId(match_id)})
        if match_data:
            return MatchResponse(**match_data)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")

    async def create_match(self, match_data: MatchCreate):
        match = Match.from_dict(match_data.dict())
        result = await self.collection.insert_one(match.dict())
        created_match = await self.collection.find_one({"_id": result.inserted_id})
        return MatchResponse(**created_match)

    async def update_match(self, match_id: str, match_data: MatchUpdate):
        self.validate_object_id(match_id)
        updated_match = await self.collection.find_one_and_update(
            {"_id": ObjectId(match_id)},
            {"$set": match_data.dict()},
            return_document=True
        )
        if updated_match:
            return MatchResponse(**updated_match)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")

    async def delete_match(self, match_id: str):
        self.validate_object_id(match_id)
        result = await self.collection.delete_one({"_id": ObjectId(match_id)})
        if result.deleted_count > 0:
            return True
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")

    async def place_bet(self, user_id: str, bet_request: PlaceBetRequest):
        self.validate_object_id(bet_request.match_id)
        self.validate_object_id(user_id)

        async with await self.db.client.start_session() as session:
            async with session.start_transaction():
                match = await self.collection.find_one({"_id": ObjectId(bet_request.match_id)})
                if not match or match["status"] != "open":
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Match not available for betting")

                user_balance = await self.db["users"].find_one({"_id": ObjectId(user_id)})
                if not user_balance or user_balance["balance"] < bet_request.amount:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds")

                bet_data = {
                    "user_id": ObjectId(user_id),
                    "match_id": ObjectId(bet_request.match_id),
                    "amount": bet_request.amount,
                    "team": bet_request.team,
                    "status": "pending",
                }
                bet_result = await self.db["bets"].insert_one(bet_data, session=session)

                new_balance = user_balance["balance"] - bet_request.amount
                await self.db["users"].update_one({"_id": ObjectId(user_id)}, {"$set": {"balance": new_balance}}, session=session)

                return {"bet_id": str(bet_result.inserted_id), "status": "Bet placed successfully"}

    async def get_live_match_updates(self, external_api_url: str, headers: dict = None):
        """
        Fetch real-time match updates from an external API and update the local match collection.
        
        :param external_api_url: URL of the external API providing live match updates.
        :param headers: Optional headers for API authentication or other purposes.
        :return: A list of updated matches.
        """
        try:
            # Fetch live match data from an external source
            response = requests.get(external_api_url, headers=headers)
            response.raise_for_status()
            live_matches = response.json()  # Assuming the API returns JSON data

            updated_matches = []
            for match_data in live_matches:
                # Here you would parse the match data according to your schema
                match_id = match_data.get("match_id")  # Assuming the API returns a match ID
                update_data = {
                    "score": match_data.get("score"),
                    "status": match_data.get("status"),
                    "last_updated": datetime.utcnow(),
                    # Include other fields as per API response
                }

                # Update match details in the database
                updated_match = await self.collection.find_one_and_update(
                    {"_id": ObjectId(match_id)},
                    {"$set": update_data},
                    return_document=True
                )
                if updated_match:
                    updated_matches.append(MatchResponse(**updated_match))

            logging.info("Live match updates applied successfully.")
            return updated_matches

        except requests.RequestException as e:
            logging.error(f"Failed to fetch live match updates: {e}")
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Failed to fetch live match updates")
        except Exception as e:
            logging.error(f"An unexpected error occurred during live updates: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error during live match updates")

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
