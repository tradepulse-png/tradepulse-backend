from __future__ import annotations
from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

OANDA_API_URL = "https://api-fxpractice.oanda.com/v3"
ACCOUNT_ID ="001-004-19482881-001"
API_KEY = "078a98b1299e9e060a9953ce3123e47f-cc4b3517fe774e3cb0325abb1bc5753e"

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
