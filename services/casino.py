from pymongo import MongoClient
from bson import ObjectId
from pymongo.errors import PyMongoError
from fastapi import HTTPException
from typing import List, Optional
from models.casino import CasinoGame, CasinoGameCreate, CasinoGameUpdate  # Importing the models

class CasinoService:
    def __init__(self, db: MongoClient):
        self.db = db
        self.games_collection = db["casino_games"]  # Assuming the collection name is "casino_games"

    # Create a new casino game
    async def create_game(self, game_data: CasinoGameCreate) -> CasinoGame:
        try:
            # Insert new game data into the collection
            game_dict = game_data.dict()
            result = await self.games_collection.insert_one(game_dict)
            game_dict["_id"] = str(result.inserted_id)  # Convert ObjectId to string

            # Return the newly created game as a CasinoGame object
            return CasinoGame(**game_dict)
        except PyMongoError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # Get a game by its ID
    async def get_game(self, game_id: str) -> CasinoGame:
        try:
            # Fetch the game by its ObjectId
            game = await self.games_collection.find_one({"_id": ObjectId(game_id)})

            if not game:
                raise HTTPException(status_code=404, detail="Game not found")

            # Return the game data as a CasinoGame object
            return CasinoGame(**game)
        except PyMongoError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching game: {str(e)}")

    # Get a list of all games
    async def get_all_games(self, limit: int = 10, skip: int = 0) -> List[CasinoGame]:
        try:
            # Fetch all games with pagination (limit and skip)
            cursor = self.games_collection.find().skip(skip).limit(limit)
            games = await cursor.to_list(length=limit)

            # Convert each game to a CasinoGame object
            return [CasinoGame(**game) for game in games]
        except PyMongoError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # Update a game by its ID
    async def update_game(self, game_id: str, game_update: CasinoGameUpdate) -> CasinoGame:
        try:
            # Prepare the updated data
            update_data = {k: v for k, v in game_update.dict().items() if v is not None}

            # Update the game in the collection
            result = await self.games_collection.update_one(
                {"_id": ObjectId(game_id)}, {"$set": update_data}
            )

            if result.matched_count == 0:
                raise HTTPException(status_code=404, detail="Game not found")

            # Fetch the updated game and return it
            updated_game = await self.get_game(game_id)
            return updated_game
        except PyMongoError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating game: {str(e)}")

    # Delete a game by its ID
    async def delete_game(self, game_id: str) -> dict:
        try:
            result = await self.games_collection.delete_one({"_id": ObjectId(game_id)})

            if result.deleted_count == 0:
                raise HTTPException(status_code=404, detail="Game not found")

            # Return a success message
            return {"status": "success", "message": "Game deleted successfully"}
        except PyMongoError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting game: {str(e)}")
