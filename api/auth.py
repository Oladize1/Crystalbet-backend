from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from core.security import verify_password, create_access_token, hash_password
from services.auth import create_user, send_reset_password_email, reset_password, authenticate_user
from schemas.auth import Token, UserCreate, PasswordResetRequest, PasswordReset, UserRead
from db.mongodb import get_db
from utils.token import decode_token
import logging

router = APIRouter()

# Set up logging
logger = logging.getLogger(__name__)

# Set up OAuth2 password bearer for protected routes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

@router.post("/token", response_model=Token, summary="User login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    """
    Log in a user and generate a JWT token for authenticated access.
    Allows login via either username or email.
    """
    try:
        # Attempt to find user by username or email
        user = await db["users"].find_one({
            "$or": [{"username": form_data.username}, {"email": form_data.username}]
        })

        if not user:
            logger.warning(f"Failed login attempt for username/email: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username, email or password"
            )
        
        # Authenticate the user (verify password)
        if not verify_password(form_data.password, user["password"]):
            logger.warning(f"Failed login attempt for username/email: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username, email or password"
            )
        
        # Generate access token for the authenticated user
        access_token = create_access_token({"sub": str(user["_id"])})
        logger.info(f"User {form_data.username} logged in successfully.")
        
        return {"access_token": access_token, "token_type": "bearer"}
    
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error during login"
        )

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db=Depends(get_db)):
    logger.info(f"Attempting to register user with email: {user.email}")
    try:
        # Check if email already exists
        if await db["users"].find_one({"email": user.email}):
            error_message = f"Email is already registered. (Email: '{user.email}')"
            logger.error(f"Registration error: {error_message}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)

        # Check if username already exists
        if await db["users"].find_one({"username": user.username}):
            error_message = f"Username is already taken. (Username: '{user.username}')"
            logger.error(f"Registration error: {error_message}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)

        # Proceed to create user if no issues found
        new_user = await create_user(db, user)
        logger.info(f"User registered successfully: {user.email}")
        return {"message": "User registered successfully", "user_id": new_user.id}

    except HTTPException:
        # Directly re-raise without re-logging
        raise
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user due to an internal error."
        )

@router.post("/password-reset-request", response_model=dict, status_code=status.HTTP_200_OK, summary="Request password reset")
async def password_reset_request(reset_request: PasswordResetRequest, db=Depends(get_db)):
    """
    Send a password reset email with a reset token.
    """
    try:
        # Check if user exists with the provided email
        user = await db["users"].find_one({"email": reset_request.email})
        if not user:
            logger.warning(f"Password reset requested for non-existing email: {reset_request.email}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email not found"
            )
        
        # Send the password reset email with a reset token
        await send_reset_password_email(reset_request.email, db)
        logger.info(f"Password reset email sent to {reset_request.email}")
        return {"message": "Password reset email sent"}
    except Exception as e:
        logger.error(f"Error sending password reset email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )

@router.post("/password-reset", response_model=dict, status_code=status.HTTP_200_OK, summary="Reset password")
async def password_reset(reset: PasswordReset, db=Depends(get_db)):
    """
    Reset the user's password using a provided reset token.
    """
    try:
        # Check if reset token is valid
        user = await db["users"].find_one({"reset_token": reset.token})
        if not user:
            logger.warning("Invalid or expired reset token.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token"
            )
        
        # Reset the user's password
        await reset_password(db, user, reset.new_password)
        logger.info(f"Password reset successful for user ID: {user['_id']}")
        return {"message": "Password updated successfully"}
    except Exception as e:
        logger.error(f"Error resetting password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )

@router.get("/me", response_model=UserRead, summary="Get logged-in user details")
async def read_users_me(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    """
    Retrieve details of the currently authenticated user.
    """
    try:
        # Decode the token to get the user ID
        user_info = await decode_token(token)
        user = await db["users"].find_one({"_id": user_info["sub"]})

        if not user:
            logger.warning("Authenticated user not found.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return user
    except Exception as e:
        logger.error(f"Error fetching authenticated user details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user details."
        )
