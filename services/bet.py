import logging
from datetime import datetime
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
from fastapi import HTTPException, status
from schemas.bet import PlaceBetRequest  # Assuming this schema exists for bet validation
from utils.util import validate_object_id  # Assuming a utility function for validating ObjectIds

logger = logging.getLogger(__name__)

class MatchService:
    def __init__(self, collection: AsyncIOMotorCollection, db):
        self.collection = collection
        self.db = db

    async def get_live_odds_data(self) -> List[Dict[str, Any]]:
        """Fetch live odds data for matches."""
        try:
            live_matches = await self.collection.find({"status": "live"}).to_list(length=100)
            odds_data = [{"match_id": str(match["_id"]), "odds": match.get("odds", {})} for match in live_matches]
            return odds_data
        except Exception as e:
            logger.error(f"Error fetching live odds data: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching live odds data.")

    async def place_bet(self, user_id: str, bet_request: PlaceBetRequest) -> Dict[str, Any]:
        """Place a bet for a specific match."""
        try:
            match_id = bet_request.match_id
            validate_object_id(match_id)

            match = await self.collection.find_one({"_id": ObjectId(match_id)})
            if not match or match.get("status") != "live":
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Match is not available for betting.")
            
            bet_data = {
                "user_id": user_id,
                "match_id": match_id,
                "amount": bet_request.amount,
                "odds": bet_request.odds,
                "placed_at": datetime.utcnow(),
                "status": "pending"
            }

            # Insert bet into the "bets" collection and handle any possible error during insertion
            result = await self.db["bets"].insert_one(bet_data)
            return {"bet_id": str(result.inserted_id), "status": "Bet placed successfully"}
        except HTTPException as http_err:
            raise http_err  # Re-raise known HTTP exceptions
        except Exception as e:
            logger.error(f"Error placing bet for match {bet_request.match_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error placing bet.")

    async def get_all_matches(self, page: int, page_size: int) -> List[Dict[str, Any]]:
        """Retrieve all available matches with pagination."""
        try:
            skips = page_size * (page - 1)
            matches = await self.collection.find({}).skip(skips).limit(page_size).to_list(length=page_size)
            return matches
        except Exception as e:
            logger.error(f"Error fetching all matches: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching all matches.")

    async def get_live_matches(self, page: int, page_size: int) -> List[Dict[str, Any]]:
        """Retrieve live matches with pagination."""
        try:
            skips = page_size * (page - 1)
            live_matches = await self.collection.find({"status": "live"}).skip(skips).limit(page_size).to_list(length=page_size)
            return live_matches
        except Exception as e:
            logger.error(f"Error fetching live matches: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching live matches.")

    async def get_match_by_id(self, match_id: str) -> Dict[str, Any]:
        """Retrieve a specific match by its ID."""
        try:
            validate_object_id(match_id)
            match = await self.collection.find_one({"_id": ObjectId(match_id)})
            if not match:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found.")
            return match
        except Exception as e:
            logger.error(f"Error fetching match with ID {match_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching match.")

    async def get_matches_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Retrieve matches filtered by sports category."""
        try:
            matches = await self.collection.find({"category": category}).to_list(length=100)
            return matches
        except Exception as e:
            logger.error(f"Error fetching matches by category {category}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching category matches.")

    async def get_todays_matches(self, page: int, page_size: int) -> List[Dict[str, Any]]:
        """Retrieve all matches scheduled for today with pagination."""
        try:
            today = datetime.utcnow().date()
            skips = page_size * (page - 1)
            todays_matches = await self.collection.find({"date": today}).skip(skips).limit(page_size).to_list(length=page_size)
            return todays_matches
        except Exception as e:
            logger.error(f"Error fetching today's matches: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching today's matches.")

    async def get_upcoming_matches(self, page: int, page_size: int) -> List[Dict[str, Any]]:
        """Retrieve all upcoming matches with pagination."""
        try:
            today = datetime.utcnow().date()
            skips = page_size * (page - 1)
            upcoming_matches = await self.collection.find({"date": {"$gt": today}}).skip(skips).limit(page_size).to_list(length=page_size)
            return upcoming_matches
        except Exception as e:
            logger.error(f"Error fetching upcoming matches: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching upcoming matches.")

    async def get_bet_history(self, user_id: str, page: int, page_size: int) -> List[Dict[str, Any]]:
        """Retrieve the betting history for a user with pagination."""
        try:
            skips = page_size * (page - 1)
            bet_history = await self.db["bets"].find({"user_id": user_id}).skip(skips).limit(page_size).to_list(length=page_size)
            return bet_history
        except Exception as e:
            logger.error(f"Error fetching bet history for user {user_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching bet history.")
