from fastapi import FastAPI, HTTPException
from honeytrade.license import LicenseValidationRequest, LicenseValidationResponse, LicenseInfo
from datetime import datetime
import uvicorn

app = FastAPI(title="HoneyTrade License Server")

# Simple in-memory store (production'da SQLite veya Redis olacak)
LICENSE_DB = {}

@app.post("/validate")
async def validate_license(req: LicenseValidationRequest) -> LicenseValidationResponse:
    # Basit validation logic (gerçekte hardware fingerprint + DB kontrolü yapılacak)
    if req.license_key.startswith("ht-"):
        license_info = LicenseInfo(
            license_key=req.license_key,
            machine_id=req.machine_id,
            is_valid=True,
            expires_at=datetime(2027, 12, 31),
            plan="pro"
        )
        LICENSE_DB[req.machine_id] = license_info
        return LicenseValidationResponse(
            valid=True,
            message="License validated successfully",
            license_info=license_info
        )
    else:
        return LicenseValidationResponse(
            valid=False,
            message="Invalid license key"
        )

@app.get("/health")
def health():
    return {"status": "healthy", "service": "license-server"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
