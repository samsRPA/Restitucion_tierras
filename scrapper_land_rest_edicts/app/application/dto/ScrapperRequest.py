import json
from typing import Optional

from pydantic import BaseModel
from pydantic import ValidationError

class ScrapperRequest(BaseModel):
    litigando_court_id:Optional[int] = None
    court_office: Optional[str] = None
    city: Optional[str] = None
    code: Optional[str] = None
    location_id:Optional[int]  = None


   
         


    @classmethod
    def fromRaw(cls, rawBody: str):
        try:
            data = json.loads(rawBody)
            return cls(**data)
        except (json.JSONDecodeError, ValidationError) as e:
            raise ValueError(f"Invalid scrapper request data: {e}")

