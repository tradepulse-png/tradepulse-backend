from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class TradeRequest(BaseModel):
    symbol: str


@app.get("/")
def home():
    return {"status": "TradePulse backend running"}


@app.post("/buy")
def buy(req: TradeRequest):
    return {"message": f"BUY order placed for {req.symbol}"}


@app.post("/sell")
def sell(req: TradeRequest):
    return {"message": f"SELL order placed for {req.symbol}"}


@app.post("/close")
def close_all():
    return {"message": "All positions closed"}
