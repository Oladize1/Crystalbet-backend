from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from pymongo.collection import Collection
from bson import ObjectId
from db.mongodb import get_db
from models.transaction import TransactionModel  # Assuming a TransactionModel schema exists in models
from schemas.transaction import TransactionCreate, TransactionResponse  # Assuming schema files exist

router = APIRouter()

# Helper function to retrieve a single transaction by ID
async def get_transaction_by_id(db: Collection, transaction_id: str) -> Optional[TransactionResponse]:
    transaction = await db.find_one({"_id": ObjectId(transaction_id)})
    if transaction:
        return TransactionResponse(**transaction)
    return None

# Endpoint to create a new transaction
@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction: TransactionCreate,
    db: Collection = Depends(lambda: get_db("transactions"))
) -> TransactionResponse:
    """
    Create a new transaction record.
    """
    transaction_data = transaction.dict()
    transaction_data["created_at"] = datetime.utcnow()
    result = await db.insert_one(transaction_data)
    if not result.inserted_id:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Transaction creation failed.")
    created_transaction = await db.find_one({"_id": result.inserted_id})
    return TransactionResponse(**created_transaction)

# Endpoint to get a list of all transactions, with optional filtering by user ID
@router.get("/", response_model=List[TransactionResponse], status_code=status.HTTP_200_OK)
async def get_transactions(
    user_id: Optional[str] = None,
    db: Collection = Depends(lambda: get_db("transactions"))
) -> List[TransactionResponse]:
    """
    Retrieve all transactions, optionally filtered by user ID.
    """
    query = {"user_id": user_id} if user_id else {}
    transactions = db.find(query)
    results = []
    async for t in transactions:
        results.append(TransactionResponse(**t))
    return results

# Endpoint to retrieve a specific transaction by ID
@router.get("/{transaction_id}", response_model=TransactionResponse, status_code=status.HTTP_200_OK)
async def get_transaction(
    transaction_id: str,
    db: Collection = Depends(lambda: get_db("transactions"))
) -> TransactionResponse:
    """
    Get details of a specific transaction by ID.
    """
    transaction = await get_transaction_by_id(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found.")
    return transaction

# Endpoint to update an existing transaction
@router.put("/{transaction_id}", response_model=TransactionResponse, status_code=status.HTTP_200_OK)
async def update_transaction(
    transaction_id: str,
    transaction: TransactionCreate,
    db: Collection = Depends(lambda: get_db("transactions"))
) -> TransactionResponse:
    """
    Update an existing transaction by ID.
    """
    transaction_data = transaction.dict()
    result = await db.update_one({"_id": ObjectId(transaction_id)}, {"$set": transaction_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found.")
    updated_transaction = await get_transaction_by_id(db, transaction_id)
    return updated_transaction

# Endpoint to delete a transaction by ID
@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: str,
    db: Collection = Depends(lambda: get_db("transactions"))
) -> None:
    """
    Delete a transaction by ID.
    """
    result = await db.delete_one({"_id": ObjectId(transaction_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found.")
    return
