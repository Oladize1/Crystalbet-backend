from db.mongodb import get_db
from schemas.transaction import TransactionCreate, TransactionResponse
from bson import ObjectId
from pymongo.errors import PyMongoError
from fastapi import HTTPException
from pymongo import MongoClient

class TransactionService:
    def __init__(self, db: MongoClient):  # Corrected the type hint for db
        self.collection = db["transactions"]  # Use your transactions collection name

    async def create_transaction(self, transaction_data: TransactionCreate, user_id: str) -> TransactionResponse:
        transaction_dict = transaction_data.dict()
        transaction_dict["user_id"] = user_id  # Associate the transaction with the user

        try:
            result = await self.collection.insert_one(transaction_dict)
            transaction_dict["_id"] = str(result.inserted_id)
            return TransactionResponse(**transaction_dict)
        except PyMongoError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    async def get_transactions(self, user_id: str) -> list[TransactionResponse]:
        transactions = []
        async for transaction in self.collection.find({"user_id": user_id}):
            transaction["_id"] = str(transaction["_id"])  # Convert ObjectId to str
            transactions.append(TransactionResponse(**transaction))
        return transactions

    async def get_transaction(self, transaction_id: str, user_id: str) -> TransactionResponse:
        try:
            transaction = await self.collection.find_one({"_id": ObjectId(transaction_id), "user_id": user_id})
            if transaction:
                transaction["_id"] = str(transaction["_id"])  # Convert ObjectId to str
                return TransactionResponse(**transaction)
            raise HTTPException(status_code=404, detail="Transaction not found")  # Explicit not found handling
        except PyMongoError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving transaction: {str(e)}")
