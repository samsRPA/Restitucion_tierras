from typing import Optional
from pydantic import BaseModel

class OfficeDto(BaseModel):
    litigando_court_id:Optional[int] = None
    court_office: Optional[str] = None
    city: Optional[str] = None
    code: Optional[str] = None
    location_id:Optional[int] = None
