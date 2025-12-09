import json
import time
from datetime import datetime
from typing import Dict, Any

import requests

# ============================================
#  CONFIG – EDIT THESE FOR YOUR OANDA ACCOUNT
# ============================================

API_KEY = "078a98b1299e9e060a9953ce3123e47f-cc4b3517fe774e3cb0325abb1bc5753e"
ACCOUNT_ID = "001-004-19482881-001"

# Practice URL (for live, change to live URL from OANDA docs)
OANDA_API_URL = "https://api-fxpractice.oanda.com/v3"

# Default instrument and size
INSTRUMENT = "GBP_USD"   # you can change to "XAU_USD", "NAS100_USD" etc.
UNITS = 5000             # 5000 units = 0.05 lots (because 1 lot is 100,000)

# ============================================
#  HELPERS
# ============================================

def _oanda_headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }


def _place_market_order(side: str, units: int) -> Dict[str, Any]:
    """
    side: "buy" or "sell"
    units: positive int (we'll flip sign for sell)
    """
    if side not in ("buy", "sell"):
        raise ValueError("side must be 'buy' or 'sell'")

    signed_units = units if side == "buy" else -units

    url = f"{OANDA_API_URL}/accounts/{ACCOUNT_ID}/orders"
    payload = {
        "order": {
            "instrument": INSTRUMENT,
            "units": str(signed_units),
            "type": "MARKET",
            "timeInForce": "FOK",
            "positionFill": "DEFAULT",
        }
    }

    resp = requests.post(url, headers=_oanda_headers(), data=json.dumps(payload))
    data = resp.json()

    ok = resp.status_code in (200, 201)

    price = None
    try:
        price = (
            data.get("orderFillTransaction", {})
            .get("price")
        )
    except Exception:
        pass

    return {
        "ok": ok,
        "status_code": resp.status_code,
        "side": side,
        "units": signed_units,
        "price": price,
        "raw": data,
        "message": json.dumps(data),
    }


def _close_all_positions() -> Dict[str, Any]:
    """
    Attempts to close all open positions for INSTRUMENT.
    """
    url = f"{OANDA_API_URL}/accounts/{ACCOUNT_ID}/positions/{INSTRUMENT}/close"
    payload = {"longUnits": "ALL", "shortUnits": "ALL"}

    resp = requests.put(url, headers=_oanda_headers(), data=json.dumps(payload))
    data = resp.json()

    ok = resp.status_code in (200, 201)

    return {
        "ok": ok,
        "status_code": resp.status_code,
        "raw": data,
        "message": json.dumps(data),
    }


def get_account_summary() -> Dict[str, Any]:
    """
    Balance + unrealized P/L for dashboard.
    """
    url = f"{OANDA_API_URL}/accounts/{ACCOUNT_ID}/summary"
    resp = requests.get(url, headers=_oanda_headers())
    data = resp.json().get("account", {})
    return {
        "balance": float(data.get("balance", 0.0)),
        "unrealizedPL": float(data.get("unrealizedPL", 0.0)),
        "openTradeCount": int(data.get("openTradeCount", 0)),
    }


# ============================================
#  SIMPLE PUBLIC FUNCTIONS USED BY server.py
# ============================================

def execute_buy() -> Dict[str, Any]:
    print("BOT: BUY order requested…")
    result = _place_market_order("buy", UNITS)
    print("BOT: BUY result:", result["message"])
    return result


def execute_sell() -> Dict[str, Any]:
    print("BOT: SELL order requested…")
    result = _place_market_order("sell", UNITS)
    print("BOT: SELL result:", result["message"])
    return result


def close_all() -> Dict[str, Any]:
    print("BOT: Close all positions requested…")
    result = _close_all_positions()
    print("BOT: CLOSE result:", result["message"])
    return result
