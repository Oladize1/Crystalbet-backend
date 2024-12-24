from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

    class Config:
        # You can add any configuration settings here if needed
        arbitrary_types_allowed = True  # For future use if you need to allow custom types
