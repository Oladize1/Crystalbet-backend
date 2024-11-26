# app/api/main.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List

router = APIRouter()

class HomeResponse(BaseModel):
    message: str
    status: str

@router.get("/", response_model=HomeResponse)
async def read_home():
    return {"message": "Welcome to the Betting Application!", "status": "success"}

@router.get("/api/az-menu", response_model=List[str])
async def get_az_menu():
    # Sample AZ menu items; replace with dynamic data if necessary
    az_menu_items = ["A", "B", "C", "D", "E"]
    return az_menu_items

@router.get("/api/quick-links", response_model=List[str])
async def get_quick_links():
    # Sample quick links; replace with dynamic data if necessary
    quick_links = ["Link1", "Link2", "Link3"]
    return quick_links
