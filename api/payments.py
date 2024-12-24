# api/payments.py

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional
from core.security import verify_access_token  # JWT authentication
import stripe  # Replace with actual payment provider if different

# Initialize the router
router = APIRouter()

# Load environment variables for payment secret keys
import os
from dotenv import load_dotenv
load_dotenv()

# Stripe API Key from environment variables
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

class PaymentInitiateRequest(BaseModel):
    amount: float  # Amount in your currency's minor unit (e.g., cents for USD)
    currency: str  # E.g., "usd"
    description: Optional[str] = "Payment for services"
    customer_email: Optional[str] = None

class PaymentVerificationRequest(BaseModel):
    payment_intent_id: str  # Stripe-specific; replace with equivalent for other providers


@router.post("/initiate", summary="Initiate a new payment")
async def initiate_payment(payment_request: PaymentInitiateRequest):
    """
    Initiates a new payment using Stripe (or other provider).
    """
    try:
        # Create a payment intent with Stripe (modify if using a different provider)
        payment_intent = stripe.PaymentIntent.create(
            amount=int(payment_request.amount * 100),  # Stripe requires cents for USD
            currency=payment_request.currency,
            description=payment_request.description,
            receipt_email=payment_request.customer_email,
        )

        return {
            "success": True,
            "message": "Payment initiated successfully.",
            "payment_intent_id": payment_intent.id,
            "client_secret": payment_intent.client_secret  # Send this to the client for confirmation
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment initiation failed: {e}"
        )


@router.get("/verify", summary="Verify payment status")
async def verify_payment(payment_verification: PaymentVerificationRequest):
    """
    Verifies the status of a payment.
    """
    try:
        # Retrieve the payment intent from Stripe (or other provider)
        payment_intent = stripe.PaymentIntent.retrieve(payment_verification.payment_intent_id)

        # Check status and return appropriate response
        if payment_intent.status == "succeeded":
            return {
                "success": True,
                "message": "Payment verified successfully.",
                "status": payment_intent.status
            }
        elif payment_intent.status in ["requires_payment_method", "requires_action"]:
            return {
                "success": False,
                "message": "Payment requires further action or has incomplete status.",
                "status": payment_intent.status
            }
        else:
            return {
                "success": False,
                "message": "Payment verification incomplete or failed.",
                "status": payment_intent.status
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment verification failed: {e}"
        )

