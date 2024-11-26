from typing import List, Dict, Optional
from bson import ObjectId
from fastapi import HTTPException
from db.mongodb import get_collection, get_db, find_one, insert_one, update_one, delete_one, is_valid_object_id  # Imported helper functions for MongoDB interaction
from models.user import UserModel
from models.bet import Bet
from models.match import Match
from models.transaction import TransactionModel
from models.payment import Payment
from models.coupon import CouponModel
from models.casino import CasinoGame
from models.virtual import VirtualSport
from models.admin import AdminContentModel

# Admin Services
async def create_admin(admin_data: AdminContentModel):
    collection = get_collection("admins")
    result = await collection.insert_one(admin_data.model_dump())  # Use model_dump in Pydantic v2 for serialization
    return {"_id": str(result.inserted_id)}

async def get_admin(admin_id: str):
    if not is_valid_object_id(admin_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    collection = get_collection("admins")
    admin = await collection.find_one({"_id": ObjectId(admin_id)})
    if admin:
        return {**admin, "_id": str(admin["_id"])}
    
    raise HTTPException(status_code=404, detail="Admin not found")

# Authentication Services
async def create_user(user_data: UserModel):
    collection = get_collection("users")
    result = await collection.insert_one(user_data.model_dump())
    return {"_id": str(result.inserted_id)}

async def get_user(user_id: str):
    if not is_valid_object_id(user_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    collection = get_collection("users")
    user = await collection.find_one({"_id": ObjectId(user_id)})
    if user:
        return {**user, "_id": str(user["_id"])}
    
    raise HTTPException(status_code=404, detail="User not found")

# Bet Services
async def create_bet(bet_data: Bet):
    collection = get_collection("bets")
    result = await collection.insert_one(bet_data.model_dump())
    return {"_id": str(result.inserted_id)}

async def get_all_bets() -> List[Dict]:
    collection = get_collection("bets")
    bets = await collection.find().to_list(None)
    return [{**bet, "_id": str(bet["_id"])} for bet in bets]

# Match Services
async def create_match(match_data: Match):
    collection = get_collection("matches")
    result = await collection.insert_one(match_data.model_dump())
    return {"_id": str(result.inserted_id)}

async def get_match(match_id: str):
    if not is_valid_object_id(match_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    collection = get_collection("matches")
    match = await collection.find_one({"_id": ObjectId(match_id)})
    if match:
        return {**match, "_id": str(match["_id"])}
    
    raise HTTPException(status_code=404, detail="Match not found")

# Payment Services
async def create_payment(payment_data: Payment):
    collection = get_collection("payments")
    result = await collection.insert_one(payment_data.model_dump())
    return {"_id": str(result.inserted_id)}

async def get_payment(payment_id: str):
    if not is_valid_object_id(payment_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    collection = get_collection("payments")
    payment = await collection.find_one({"_id": ObjectId(payment_id)})
    if payment:
        return {**payment, "_id": str(payment["_id"])}
    
    raise HTTPException(status_code=404, detail="Payment not found")

# Transaction Services
async def create_transaction(transaction_data: TransactionModel):
    collection = get_collection("transactions")
    result = await collection.insert_one(transaction_data.model_dump())
    return {"_id": str(result.inserted_id)}

async def get_all_transactions() -> List[Dict]:
    collection = get_collection("transactions")
    transactions = await collection.find().to_list(None)
    return [{**transaction, "_id": str(transaction["_id"])} for transaction in transactions]

# Coupon Services
async def validate_coupon(coupon_data: CouponModel):
    collection = get_collection("coupons")
    coupon = await collection.find_one({"code": coupon_data.code})
    if coupon:
        return {**coupon, "_id": str(coupon["_id"])}
    
    raise HTTPException(status_code=404, detail="Coupon not found")

# Casino Services
async def get_casino_games() -> List[Dict]:
    collection = get_collection("casino")
    games = await collection.find().to_list(None)
    return [{**game, "_id": str(game["_id"])} for game in games]

# Virtual Sports Services
async def get_virtual_sports() -> List[Dict]:
    collection = get_collection("virtuals")
    virtuals = await collection.find().to_list(None)
    return [{**virtual, "_id": str(virtual["_id"])} for virtual in virtuals]
