from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LicenseInfo(BaseModel):
    license_key: str
    machine_id: str
    is_valid: bool
    expires_at: Optional[datetime] = None
    plan: str = "pro"
    features: list[str] = []

class LicenseValidationRequest(BaseModel):
    license_key: str
    machine_id: str

class LicenseValidationResponse(BaseModel):
    valid: bool
    message: str
    license_info: Optional[LicenseInfo] = None