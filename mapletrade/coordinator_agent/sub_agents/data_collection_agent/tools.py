# coordinator_agent/sub_agents/data_collection_agent/tools.py
"""
Data collection tools for TSX market data
"""

from typing import Dict, List
import yfinance as yf
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def collect_tsx_data(symbol: str) -> Dict:
    """
    Collect real-time TSX market data from multiple sources.
    
    Args:
        symbol: TSX stock symbol (e.g., 'TD.TO')
        
    Returns:
        Market data with source attribution and storage instructions
    """
    # Normalize symbol
    if not symbol.endswith('.TO'):
        symbol = f"{symbol}.TO"
    
    try:
        # Primary: Yahoo Finance for TSX
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="1d", interval="1m")
        
        if not hist.empty:
            current_price = hist['Close'].iloc[-1]
            volume = hist['Volume'].iloc[-1]
            
            result = {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "market_data": {
                    "price": round(float(current_price), 2),
                    "volume": int(volume),
                    "market_cap": info.get('marketCap'),
                    "currency": "CAD"
                },
                "data_source": "Yahoo Finance API",
                "collection_method": "Real-time via yfinance library",
                "verification_links": [
                    f"https://finance.yahoo.com/quote/{symbol}",
                    "https://www.tsx.com/"
                ],
                "educational_info": [
                    "📊 Data collected from Yahoo Finance - same source as financial websites",
                    "🕐 Real-time during TSX hours (9:30 AM - 4:00 PM ET)",
                    "💱 Prices in Canadian dollars (CAD)",
                    "🔍 Verify by checking Yahoo Finance directly"
                ],
                "storage_ready": True,
                "next_step": "Store in BigQuery for historical analysis"
            }
            
            return result
        else:
            return _handle_collection_error(symbol, "No recent trading data available")
            
    except Exception as e:
        return _handle_collection_error(symbol, str(e))

def collect_multiple_stocks(symbols: List[str]) -> Dict:
    """
    Collect data for multiple TSX stocks efficiently.
    
    Args:
        symbols: List of stock symbols
        
    Returns:
        Batch collection results
    """
    results = {
        "batch_timestamp": datetime.now().isoformat(),
        "total_symbols": len(symbols),
        "successful": [],
        "failed": [],
        "summary": {}
    }
    
    for symbol in symbols[:5]:  # Limit to 5 to avoid rate limits
        data = collect_tsx_data(symbol)
        
        if "market_data" in data:
            results["successful"].append({
                "symbol": symbol,
                "price": data["market_data"]["price"],
                "volume": data["market_data"]["volume"]
            })
        else:
            results["failed"].append({
                "symbol": symbol,
                "error": data.get("error", "Unknown error")
            })
    
    results["summary"] = {
        "success_rate": f"{len(results['successful'])}/{len(symbols)}",
        "ready_for_storage": len(results["successful"]),
        "educational_note": "📈 Batch collection enables portfolio-wide analysis"
    }
    
    return results

def check_market_status() -> Dict:
    """
    Check if TSX is currently open for trading.
    
    Returns:
        Market status with trading hours info
    """
    now = datetime.now()
    
    # TSX hours: 9:30 AM - 4:00 PM ET, Monday-Friday
    market_open = now.replace(hour=9, minute=30, second=0)
    market_close = now.replace(hour=16, minute=0, second=0)
    is_weekday = now.weekday() < 5
    is_trading_hours = market_open <= now <= market_close
    is_open = is_weekday and is_trading_hours
    
    return {
        "market_status": "OPEN" if is_open else "CLOSED",
        "current_time": now.strftime("%Y-%m-%d %H:%M:%S ET"),
        "trading_hours": "9:30 AM - 4:00 PM ET, Monday-Friday",
        "data_freshness": "Real-time" if is_open else "End-of-day prices",
        "educational_info": [
            "🕐 TSX trading hours: 9:30 AM - 4:00 PM Eastern Time",
            "📊 Best liquidity in first/last trading hour",
            "🌙 After-hours: Limited trading, wider spreads"
        ],
        "verification_link": "https://www.tsx.com/trading/calendars-and-trading-hours"
    }

def _handle_collection_error(symbol: str, error_msg: str) -> Dict:
    """Handle data collection errors with educational fallbacks."""
    return {
        "symbol": symbol,
        "error": f"Data collection failed: {error_msg}",
        "manual_alternatives": [
            f"Check Yahoo Finance: https://finance.yahoo.com/quote/{symbol}",
            f"Visit TSX directly: https://www.tsx.com/",
            "Use financial websites like Morningstar or Globe and Mail"
        ],
        "educational_notes": [
            "⚠️ Data collection can fail due to network issues or API limits",
            "💡 Always have backup data sources for trading decisions",
            "📱 Consider using multiple financial apps for verification"
        ],
        "troubleshooting": [
            "Verify symbol format (should end with .TO for TSX)",
            "Check if stock is actively traded",
            "Ensure internet connection is stable"
        ]
    }