from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket, WebSocketDisconnect
from typing import List
from db.mongodb import get_db
from services.match import MatchService
from utils.jwt import get_current_user
from schemas.match import (
    MatchResponse,
    MatchDetailResponse,
    LiveMatchResponse,
    SportCategoryResponse,
    BetHistoryResponse,
    PlaceBetRequest
)
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
import logging

# Initialize router
router = APIRouter(
    prefix="/api/matches",
    tags=["Matches"]
)

# Initialize logger
logger = logging.getLogger("uvicorn.error")

# Dependency for MatchService
def get_match_service(db=Depends(get_db)) -> MatchService:
    collection: AsyncIOMotorCollection = db["matches"]
    return MatchService(collection, db)

# Reusable pagination dependency
def pagination_params(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)):
    return {"page": page, "page_size": page_size}

# Helper function to validate ObjectId format
def validate_object_id(id: str):
    try:
        ObjectId(id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid ID format: {id}"
        )

@router.websocket("/ws/live-bets")
async def websocket_live_bets(websocket: WebSocket, match_service: MatchService = Depends(get_match_service)):
    await websocket.accept()
    try:
        while True:
            odds_data = await match_service.get_live_odds_data()  # Ensure this method exists in MatchService
            await websocket.send_json(odds_data)
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()


@router.post("/place-bet", response_model=dict)
async def place_bet(
    bet_request: PlaceBetRequest,
    user_id: str = Depends(get_current_user),
    match_service: MatchService = Depends(get_match_service)
):
    """Place a bet for a specific match."""
    try:
        result = await match_service.place_bet(user_id, bet_request)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error placing bet: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error placing bet.")

@router.get("/", response_model=List[MatchResponse])
async def get_all_matches(
    pagination: dict = Depends(pagination_params),
    match_service: MatchService = Depends(get_match_service)
):
    """Retrieve all available matches with optional pagination."""
    try:
        matches = await match_service.get_all_matches(**pagination)
        if not matches:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No matches found.")
        return matches
    except Exception as e:
        logger.error(f"Error fetching matches: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching matches.")

@router.get("/live", response_model=List[LiveMatchResponse])
async def get_live_matches(
    pagination: dict = Depends(pagination_params),
    match_service: MatchService = Depends(get_match_service)
):
    """Retrieve all live matches with live betting options and optional pagination."""
    try:
        live_matches = await match_service.get_live_matches(**pagination)
        if not live_matches:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No live matches found.")
        return live_matches
    except Exception as e:
        logger.error(f"Error fetching live matches: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching live matches.")

@router.get("/{match_id}", response_model=MatchDetailResponse)
async def get_match_by_id(
    match_id: str,
    match_service: MatchService = Depends(get_match_service)
):
    """Retrieve detailed information for a specific match by match ID."""
    validate_object_id(match_id)
    try:
        match = await match_service.get_match_by_id(match_id)
        if not match:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found.")
        return match
    except Exception as e:
        logger.error(f"Error fetching match details for ID {match_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching match details.")

@router.get("/sports/{category}", response_model=List[SportCategoryResponse])
async def get_matches_by_sport_category(
    category: str,
    match_service: MatchService = Depends(get_match_service)
):
    """Retrieve matches filtered by a specified sports category."""
    try:
        matches = await match_service.get_matches_by_category(category)
        if not matches:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No matches found for category '{category}'.")
        return matches
    except Exception as e:
        logger.error(f"Error fetching matches for category {category}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching category matches.")

@router.get("/today", response_model=List[MatchResponse])
async def get_todays_matches(
    pagination: dict = Depends(pagination_params),
    match_service: MatchService = Depends(get_match_service)
):
    """Retrieve all matches scheduled for today with optional pagination."""
    try:
        todays_matches = await match_service.get_todays_matches(**pagination)
        if not todays_matches:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No matches available for today.")
        return todays_matches
    except Exception as e:
        logger.error(f"Error fetching today's matches: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching today's matches.")

@router.get("/upcoming", response_model=List[MatchResponse])
async def get_upcoming_matches(
    pagination: dict = Depends(pagination_params),
    match_service: MatchService = Depends(get_match_service)
):
    """Retrieve all upcoming matches with optional pagination."""
    try:
        upcoming_matches = await match_service.get_upcoming_matches(**pagination)
        if not upcoming_matches:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No upcoming matches found.")
        return upcoming_matches
    except Exception as e:
        logger.error(f"Error fetching upcoming matches: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching upcoming matches.")

@router.get("/history", response_model=List[BetHistoryResponse])
async def get_bet_history(
    user_id: str = Depends(get_current_user),
    pagination: dict = Depends(pagination_params),
    match_service: MatchService = Depends(get_match_service)
):
    """Retrieve the betting history for the authenticated user with optional pagination."""
    try:
        bet_history = await match_service.get_bet_history(user_id, **pagination)
        if not bet_history:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No bet history found.")
        return bet_history
    except Exception as e:
        logger.error(f"Error fetching bet history for user {user_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching bet history.")
