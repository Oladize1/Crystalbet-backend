from fastapi import APIRouter, HTTPException, Depends, WebSocket
from typing import List
from schemas.casino import CasinoGame, CasinoGameCreate, CasinoGameUpdate
from services.casino import CasinoService
from db.mongodb import get_db  # Assuming you have a function to get the DB connection

router = APIRouter()
async def get_live_casino_data(db=Depends(get_db)):
    # Assuming you're querying the database to get live game data
    try:
        # Example: Fetch live data of games from your database (replace with actual query)
        live_games = await db["casino_games"].find({"status": "live"}).to_list(length=10)
        return live_games  # This should be a list of live casino game data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching live casino data: {str(e)}")

@router.websocket("/ws/casino-live")
async def websocket_casino_live(websocket: WebSocket):
    await websocket.accept()
    while True:
        # Real-time data for live casino games
        casino_data = await get_live_casino_data()  # Replace with actual function to fetch live data
        await websocket.send_json(casino_data)

@router.get("/", response_model=List[CasinoGame])
async def get_casino_games(db=Depends(get_db)):
    """Get a list of casino games."""
    casino_service = CasinoService(db)  # Pass the database connection to the service
    games = await casino_service.get_all_games()
    return games

@router.get("/{game_id}", response_model=CasinoGame)
async def get_casino_game(game_id: str, db=Depends(get_db)):
    """Get details of a specific casino game by ID."""
    casino_service = CasinoService(db)  # Pass the database connection to the service
    game = await casino_service.get_game(game_id)
    return game

@router.post("/", response_model=CasinoGame)
async def create_casino_game(game: CasinoGameCreate, db=Depends(get_db)):
    """Create a new casino game."""
    casino_service = CasinoService(db)  # Pass the database connection to the service
    new_game = await casino_service.create_game(game)
    return new_game

@router.put("/{game_id}", response_model=CasinoGame)
async def update_casino_game(game_id: str, game: CasinoGameUpdate, db=Depends(get_db)):
    """Update an existing casino game by ID."""
    casino_service = CasinoService(db)  # Pass the database connection to the service
    updated_game = await casino_service.update_game(game_id, game)
    return updated_game

@router.delete("/{game_id}")
async def delete_casino_game(game_id: str, db=Depends(get_db)):
    """Delete a casino game by ID."""
    casino_service = CasinoService(db)  # Pass the database connection to the service
    result = await casino_service.delete_game(game_id)
    return result
