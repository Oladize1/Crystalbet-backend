# models/match.py
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId

class Match:
    def __init__(self, team_a: str, team_b: str, score: str, status: str, start_time: str):
        self.team_a = team_a
        self.team_b = team_b
        self.score = score
        self.status = status
        self.start_time = start_time

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            team_a=data.get("team_a"),
            team_b=data.get("team_b"),
            score=data.get("score"),
            status=data.get("status"),
            start_time=data.get("start_time"),
        )

    def to_dict(self):
        return {
            "_id": str(ObjectId()),  # Generate a new ObjectId
            "team_a": self.team_a,
            "team_b": self.team_b,
            "score": self.score,
            "status": self.status,
            "start_time": self.start_time,
        }

# Example async function to interact with MongoDB
async def create_match(collection: AsyncIOMotorCollection, match_data: Match):
    match_dict = match_data.to_dict()
    result = await collection.insert_one(match_dict)
    match_dict["_id"] = str(result.inserted_id)  # Add the generated ID
    return match_dict

class Match:
    def __init__(self, team_a: str, team_b: str, score: str, status: str, start_time: str):
        self.team_a = team_a
        self.team_b = team_b
        self.score = score
        self.status = status
        self.start_time = start_time

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            team_a=data.get("team_a"),
            team_b=data.get("team_b"),
            score=data.get("score"),
            status=data.get("status"),
            start_time=data.get("start_time"),
        )

    def to_dict(self):
        return {
            "_id": str(ObjectId()),  # Generate a new ObjectId
            "team_a": self.team_a,
            "team_b": self.team_b,
            "score": self.score,
            "status": self.status,
            "start_time": self.start_time,
        }

class LiveMatch(Match):
    def __init__(self, team_a: str, team_b: str, score: str, status: str, start_time: str, live_updates: list = None):
        super().__init__(team_a, team_b, score, status, start_time)
        self.live_updates = live_updates or []

    @classmethod
    def from_dict(cls, data: dict):
        instance = super().from_dict(data)
        instance.live_updates = data.get("live_updates", [])
        return instance

    def to_dict(self):
        match_dict = super().to_dict()
        match_dict.update({"live_updates": self.live_updates})
        return match_dict

# Example async function to interact with MongoDB
async def create_match(collection: AsyncIOMotorCollection, match_data: Match):
    match_dict = match_data.to_dict()
    result = await collection.insert_one(match_dict)
    match_dict["_id"] = str(result.inserted_id)  # Add the generated ID
    return match_dict