# app/services/main.py
from typing import List
from fastapi import HTTPException
from db.mongodb import get_dbS

class MainService:
    @staticmethod
    async def get_home_message() -> dict:
        return {"message": "Welcome to the Betting Application!", "status": "success"}

    @staticmethod
    async def get_az_menu_items() -> List[str]:
        # Replace this with database retrieval logic if necessary
        az_menu_items = ["A", "B", "C", "D", "E"]
        return az_menu_items

    @staticmethod
    async def get_quick_links() -> List[str]:
        # Replace this with database retrieval logic if necessary
        quick_links = ["Link1", "Link2", "Link3"]
        return quick_links
