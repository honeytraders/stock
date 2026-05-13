from fastapi import FastAPI
import uvicorn
from honeytrade.config import config
import structlog

logger = structlog.get_logger()
app = FastAPI(title="HoneyTrade Backtesting Service", version="1.0.0")

@app.get("/health")
def health():
    return {"status": "healthy", "service": "backtesting"}

@app.post("/backtest")
def run_backtest():
    # TODO: Implement backtesting logic
    return {"message": "Backtesting endpoint - coming soon"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
