from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from datetime import datetime
from typing import List, Dict, Any

from bot import execute_buy, execute_sell, close_all, get_account_summary

app = FastAPI()

# Allow your phone / emulator to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
#  GLOBAL STATE
# ============================================

AUTOBOT_ENABLED: bool = False
TRADE_HISTORY: List[Dict[str, Any]] = []
LAST_ACTION: str | None = None


def _add_history(entry: Dict[str, Any]) -> None:
    TRADE_HISTORY.append(entry)


# ============================================
#  API ENDPOINTS – BUTTONS
# ============================================

@app.post("/buy")
async def buy():
    global LAST_ACTION
    result = execute_buy()
    LAST_ACTION = "BUY"

    _add_history(
        {
            "time": datetime.utcnow().isoformat(),
            "action": "BUY",
            "ok": result["ok"],
            "price": result.get("price"),
            "message": result["message"],
        }
    )

    return {"ok": result["ok"], "detail": result["message"]}


@app.post("/sell")
async def sell():
    global LAST_ACTION
    result = execute_sell()
    LAST_ACTION = "SELL"

    _add_history(
        {
            "time": datetime.utcnow().isoformat(),
            "action": "SELL",
            "ok": result["ok"],
            "price": result.get("price"),
            "message": result["message"],
        }
    )

    return {"ok": result["ok"], "detail": result["message"]}


@app.post("/close")
async def close():
    global LAST_ACTION
    result = close_all()
    LAST_ACTION = "CLOSE"

    _add_history(
        {
            "time": datetime.utcnow().isoformat(),
            "action": "CLOSE",
            "ok": result["ok"],
            "price": None,
            "message": result["message"],
        }
    )

    return {"ok": result["ok"], "detail": result["message"]}


# ============================================
#  STATUS + HISTORY
# ============================================

@app.get("/status")
async def status():
    acc = get_account_summary()
    return {
        "autobot_enabled": AUTOBOT_ENABLED,
        "balance": acc["balance"],
        "unrealizedPL": acc["unrealizedPL"],
        "openTradeCount": acc["openTradeCount"],
        "last_action": LAST_ACTION,
        "history_count": len(TRADE_HISTORY),
    }


@app.get("/history")
async def history():
    # last 20 trades
    return {"history": TRADE_HISTORY[-20:]}


# ============================================
#  AUTOBOT – SET & FORGET
# ============================================

@app.post("/autobot/start")
async def start_autobot():
    global AUTOBOT_ENABLED
    AUTOBOT_ENABLED = True
    _add_history(
        {
            "time": datetime.utcnow().isoformat(),
            "action": "AUTOBOT_ON",
            "ok": True,
            "price": None,
            "message": "Autobot enabled",
        }
    )
    return {"autobot_enabled": AUTOBOT_ENABLED}


@app.post("/autobot/stop")
async def stop_autobot():
    global AUTOBOT_ENABLED
    AUTOBOT_ENABLED = False
    _add_history(
        {
            "time": datetime.utcnow().isoformat(),
            "action": "AUTOBOT_OFF",
            "ok": True,
            "price": None,
            "message": "Autobot disabled",
        }
    )
    return {"autobot_enabled": AUTOBOT_ENABLED}


# ============================================
#  TRADINGVIEW WEBHOOK
# ============================================

WEBHOOK_SECRET = "changeme-if-you-want-extra-security"


@app.post("/webhook")
async def webhook(request: Request):
    """
    TradingView alert JSON example:

    {
      "secret": "changeme-if-you-want-extra-security",
      "signal": "buy"
    }
    """
    data = await request.json()
    secret = data.get("secret")
    signal = data.get("signal")

    if secret and secret != WEBHOOK_SECRET:
        return {"ok": False, "detail": "Invalid secret"}

    if signal == "buy":
        return await buy()
    elif signal == "sell":
        return await sell()
    elif signal in ("close", "flat"):
        return await close()
    else:
        return {"ok": False, "detail": f"Unknown signal '{signal}'"}


# ============================================
#  SIMPLE STRATEGY LOOP (AUTOBOT)
# ============================================

async def strategy_loop():
    """
    VERY SIMPLE EXAMPLE:
    - Every 60s, if AUTOBOT_ENABLED:
        * If no open trades -> send BUY
        * If there ARE open trades -> do nothing
    You can later replace this logic with RSI / EMA / whatever you like.
    """
    global AUTOBOT_ENABLED

    while True:
        await asyncio.sleep(60)  # wait 60 seconds between checks

        if not AUTOBOT_ENABLED:
            continue

        print("AUTOBOT: running strategy tick…")

        acc = get_account_summary()
        open_count = acc["openTradeCount"]

        if open_count == 0:
            print("AUTOBOT: no open trades, sending BUY…")
            await buy()
        else:
            print(f"AUTOBOT: {open_count} open trade(s), doing nothing this tick.")


@app.on_event("startup")
async def on_startup():
    # fire-and-forget strategy loop
    asyncio.create_task(strategy_loop())


# ============================================
#  MAIN
# ============================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
