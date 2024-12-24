from pymongo import MongoClient
from bson import ObjectId
from pymongo.errors import PyMongoError
from fastapi import HTTPException

class PaymentService:
    def __init__(self, db):
        self.db = db
        self.payments_collection = self.db["payments"]  # Ensure correct collection

    # Asynchronous method to initiate a payment
    async def initiate_payment(self, amount: float, currency: str, user_id: str):
        transaction_data = {
            "amount": amount,
            "currency": currency,
            "user_id": user_id,
            "status": "pending",  # Initial payment status
            "message": "Payment initiated"
        }

        try:
            # Insert the transaction data into the payments collection
            result = await self.payments_collection.insert_one(transaction_data)
            transaction_id = str(result.inserted_id)

            # Simulate payment processing logic
            return {
                "transaction_id": transaction_id,
                "status": "pending",
                "message": "Payment successfully initiated"
            }
        except PyMongoError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # Asynchronous method to verify a payment
    async def verify_payment(self, transaction_id: str):
        try:
            # Convert the string transaction ID to ObjectId
            transaction = await self.payments_collection.find_one({"_id": ObjectId(transaction_id)})

            if not transaction:
                raise HTTPException(status_code=404, detail="Transaction not found")

            # Simulate payment verification (e.g., call payment gateway)
            transaction["status"] = "verified"  # Simulating successful verification

            # Update the transaction status to "verified"
            await self.payments_collection.update_one(
                {"_id": ObjectId(transaction_id)}, {"$set": {"status": transaction["status"]}}
            )

            return {
                "transaction_id": transaction_id,
                "status": transaction["status"],
                "message": "Payment successfully verified"
            }
        except PyMongoError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error verifying payment: {str(e)}")
