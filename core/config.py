from pydantic_settings import BaseSettings, SettingsConfigDict  # Adjust import for Pydantic v2
from dotenv import load_dotenv
import logging
import bcrypt
import motor.motor_asyncio
from jose import JWTError, jwt  # JWT handling for security
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from schemas.auth import Token  # Assuming you have a Token schema for decoding JWTs
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

# Load environment variables from .env file
load_dotenv()

# Initialize logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("config.log"),
    ]
)
logger = logging.getLogger(__name__)

from typing import Optional

class Settings(BaseSettings):
    # App-related settings
    ALLOW_ORIGINS: str
    TRUSTED_HOSTS: str
    
    # JWT settings
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    RESET_TOKEN_EXPIRE_MINUTES: int
    
    # MongoDB settings
    MONGO_URI: str
    DATABASE_NAME: str
    MAX_POOL_SIZE: int
    MIN_POOL_SIZE: int
    
    # Environment setting
    ENVIRONMENT: str
    
    # Optional frontend URL
    FRONTEND_URL: Optional[str] = None
    
    # Mail settings
    MAIL_HOST: str
    MAIL_PORT: int
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_TLS: bool
    MAIL_SSL: bool

    # Pydantic v2 config (replaces `class Config` in v1)
    model_config = SettingsConfigDict(env_file=".env")
# Initialize the settings object
settings = Settings()

# Log configuration loading
logger.info(f"ALLOW_ORIGINS set to: {settings.ALLOW_ORIGINS}")
logger.info(f"TRUSTED_HOSTS set to: {settings.TRUSTED_HOSTS}")
logger.info("SECRET_KEY loaded successfully")
logger.info(f"ALGORITHM set to: {settings.ALGORITHM}")
logger.info(f"ACCESS_TOKEN_EXPIRE_MINUTES set to: {settings.ACCESS_TOKEN_EXPIRE_MINUTES}")
logger.info(f"MONGO_URI set to: {settings.MONGO_URI}")
logger.info(f"DATABASE_NAME set to: {settings.DATABASE_NAME}")
logger.info(f"MAX_POOL_SIZE set to: {settings.MAX_POOL_SIZE}")
logger.info(f"MIN_POOL_SIZE set to: {settings.MIN_POOL_SIZE}")
logger.info(f"ENVIRONMENT set to: {settings.ENVIRONMENT}")
logger.info("Configuration loaded successfully")

# MongoDB setup using the settings (Initialize MongoDB client once)
client = motor.motor_asyncio.AsyncIOMotorClient(
    settings.MONGO_URI,
    maxPoolSize=settings.MAX_POOL_SIZE,
    minPoolSize=settings.MIN_POOL_SIZE
)
DATABASE_NAME = client[settings.DATABASE_NAME]

# CORS Middleware setup
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.ALLOW_ORIGINS.split(",")],  # Ensure stripping spaces
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Corrected line without extra text
RESET_TOKEN_EXPIRE_MINUTES = settings.RESET_TOKEN_EXPIRE_MINUTES
