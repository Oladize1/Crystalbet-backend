from bson import ObjectId
from fastapi import HTTPException, status

def validate_object_id(object_id: str) -> None:
    """Validate a given string as a valid MongoDB ObjectId."""
    try:
        # Try to convert the string to an ObjectId
        ObjectId(object_id)
    except Exception:
        # If it fails, raise an HTTP exception
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ObjectId format."
        )
