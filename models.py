from pydantic import BaseModel


class Coordinates(BaseModel):
    latitude: float
    longtitude: float


class PostResponse(BaseModel):
    cities: list[str]