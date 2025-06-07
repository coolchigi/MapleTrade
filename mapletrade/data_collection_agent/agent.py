
"""
MapleTrade Enhanced Data Collection Agent
Comprehensive market data gathering with Financial Modeling Prep integration
"""

import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os
from dotenv import load_dotenv
from google.adk.agents import Agent
import json
import time

# Load environment variables
load_dotenv()

# Configuration
FMP_API_KEY = os.getenv('FMP_API_KEY', 'demo')
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"
ENABLE_FMP_PREMIUM = os.getenv('ENABLE_FMP_PREMIUM', 'False').lower() == 'true'

# Enhanced TSX symbol list with sectors
TSX_SYMBOLS = {
    "major": {
        "SHOP.TO": {"name": "Shopify Inc", "sector": "Technology"},
        "TD.TO": {"name": "Toronto-Dominion Bank", "sector": "Financial"},
        "RY.TO": {"name": "Royal Bank of Canada", "sector": "Financial"},
        "CNR.TO": {"name": "Canadian National Railway", "sector": "Industrial"},
        "SU.TO": {"name": "Suncor Energy", "sector": "Energy"},
        "WEED.TO": {"name": "Canopy Growth", "sector": "Healthcare"},
        "AC.TO": {"name": "Air Canada", "sector": "Transportation"},
        "BBD-B.TO": {"name": "Bombardier Inc", "sector": "Industrial"}
    },
    "banking": ["TD.TO", "RY.TO", "BMO.TO", "BNS.TO", "CM.TO"],
    "energy": ["SU.TO", "CNQ.TO", "IMO.TO", "CVE.TO", "TOU.TO"],
    "tech": ["SHOP.TO", "OTEX.TO", "CGI.TO", "REAL.TO"],
    "mining": ["ABX.TO", "K.TO", "FM.TO", "TRI.TO"]
}

class DataCollectionError(Exception):
    """Custom exception for data collection errors"""
    pass

def fetch_fmp_data(endpoint: str, params: Dict = None) -> Dict:
    """
    Fetch data from Financial Modeling Prep API with error handling.
    
    Args:
        endpoint: FMP API endpoint (without base URL)
        params: Additional query parameters
        
    Returns:
        Dictionary with API response data
    """
    try:
        if params is None:
            params = {}
        
        # Add API key to parameters
        params['apikey'] = FMP_API_KEY
        
        url = f"{FMP_BASE_URL}/{endpoint}"
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Handle empty responses
        if not data:
            return {"error": "No data returned from FMP API", "endpoint": endpoint}
            
        return {"data": data, "source": "FMP", "timestamp": datetime.now().isoformat()}
        
    except requests.exceptions.RequestException as e:
        return {"error": f"FMP API request failed: {str(e)}", "endpoint": endpoint}
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON response from FMP: {str(e)}", "endpoint": endpoint}
    except Exception as e:
        return {"error": f"Unexpected error fetching from FMP: {str(e)}", "endpoint": endpoint}

def fetch_comprehensive_stock_data(symbol: str) -> Dict:
    """
    Fetch comprehensive stock data from multiple sources with fallbacks.
    
    Args:
        symbol: Stock symbol (will be converted to TSX format)
        
    Returns:
        Dictionary with comprehensive stock data and educational insights
    """
    try:
        # Ensure TSX format
        tsx_symbol = symbol.upper()
        if not tsx_symbol.endswith('.TO'):
            tsx_symbol = f"{tsx_symbol}.TO"
        
        # Remove .TO for FMP API (it uses different format)
        fmp_symbol = tsx_symbol.replace('.TO', '.TRT')  # Toronto Stock Exchange format for FMP
        
        result = {
            "symbol": tsx_symbol,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S ET"),
            "data_sources": [],
            "market_data": {},
            "company_info": {},
            "alerts": [],
            "educational_notes": [],
            "errors": []
        }
        
        # 1. Try FMP for real-time data
        print(f"🔍 Fetching {tsx_symbol} data from Financial Modeling Prep...")
        fmp_quote = fetch_fmp_data(f"quote/{fmp_symbol}")
        
        if "data" in fmp_quote and fmp_quote["data"]:
            quote_data = fmp_quote["data"][0]
            result["data_sources"].append("FMP")
            result["market_data"].update({
                "current_price": quote_data.get("price", 0),
                "change": quote_data.get("change", 0),
                "change_percent": quote_data.get("changesPercentage", 0),
                "volume": quote_data.get("volume", 0),
                "market_cap": quote_data.get("marketCap", 0),
                "day_high": quote_data.get("dayHigh", 0),
                "day_low": quote_data.get("dayLow", 0),
                "year_high": quote_data.get("yearHigh", 0),
                "year_low": quote_data.get("yearLow", 0)
            })
        else:
            result["errors"].append(f"FMP data unavailable: {fmp_quote.get('error', 'Unknown error')}")
        
        # 2. Fallback to Yahoo Finance
        if not result["market_data"]:
            print(f"📈 Falling back to Yahoo Finance for {tsx_symbol}...")
            try:
                ticker = yf.Ticker(tsx_symbol)
                info = ticker.info
                hist = ticker.history(period="2d", interval="1h")
                
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    prev_close = info.get('previousClose', current_price)
                    change = current_price - prev_close
                    change_percent = (change / prev_close) * 100 if prev_close != 0 else 0
                    
                    result["data_sources"].append("Yahoo Finance")
                    result["market_data"].update({
                        "current_price": round(current_price, 2),
                        "change": round(change, 2),
                        "change_percent": round(change_percent, 2),
                        "volume": int(hist['Volume'].iloc[-1]),
                        "market_cap": info.get('marketCap', 0),
                        "day_high": round(hist['High'].iloc[-1], 2),
                        "day_low": round(hist['Low'].iloc[-1], 2),
                        "year_high": info.get('fiftyTwoWeekHigh', 0),
                        "year_low": info.get('fiftyTwoWeekLow', 0)
                    })
                    
                    result["company_info"] = {
                        "name": info.get('longName', 'Unknown'),
                        "sector": info.get('sector', 'Unknown'),
                        "industry": info.get('industry', 'Unknown'),
                        "employees": info.get('fullTimeEmployees', 0)
                    }
                    
            except Exception as e:
                result["errors"].append(f"Yahoo Finance error: {str(e)}")
        
        # 3. Generate educational insights and alerts
        if result["market_data"]:
            price = result["market_data"]["current_price"]
            change_pct = result["market_data"]["change_percent"]
            volume = result["market_data"]["volume"]
            
            # Price movement alerts
            if abs(change_pct) >= 3:
                alert_emoji = "🚀" if change_pct > 0 else "📉"
                result["alerts"].append({
                    "type": "price_movement",
                    "message": f"{alert_emoji} {tsx_symbol}: {change_pct:+.1f}% - Significant movement!",
                    "explanation": "📚 Moves >3% in a day often indicate news, earnings, or significant market events worth investigating."
                })
            
            # Volume analysis (simplified without historical average)
            if volume > 0:
                result["educational_notes"].append(
                    f"📊 Current volume: {volume:,} shares - Higher volume typically confirms price movements"
                )
            
            # Price level insights
            year_high = result["market_data"].get("year_high", 0)
            year_low = result["market_data"].get("year_low", 0)
            
            if year_high > 0 and year_low > 0:
                position_in_range = ((price - year_low) / (year_high - year_low)) * 100
                if position_in_range >= 90:
                    result["alerts"].append({
                        "type": "price_level",
                        "message": f"📈 {tsx_symbol} near 52-week high ({position_in_range:.0f}% of range)",
                        "explanation": "📚 Stocks near highs may face resistance, but can also indicate strong momentum."
                    })
                elif position_in_range <= 10:
                    result["alerts"].append({
                        "type": "price_level", 
                        "message": f"📉 {tsx_symbol} near 52-week low ({position_in_range:.0f}% of range)",
                        "explanation": "📚 Stocks near lows may find support, but could also indicate fundamental issues."
                    })
        
        # Add general educational notes
        result["educational_notes"].extend([
            "💡 For day trading, focus on stocks with >$2M daily volume for better liquidity",
            "💡 TSX trading hours: 9:30 AM - 4:00 PM ET, with best volume in first/last hour",
            "💡 Canadian stocks often move with commodity prices and USD/CAD exchange rate"
        ])
        
        return result
        
    except Exception as e:
        return {
            "symbol": symbol,
            "error": f"Critical error in data collection: {str(e)}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S ET")
        }

def get_market_overview(sector: str = "major") -> Dict:
    """
    Get overview of multiple TSX stocks with sector analysis.
    
    Args:
        sector: Sector to analyze ("major", "banking", "energy", "tech", "mining")
        
    Returns:
        Dictionary with market overview and educational insights
    """
    try:
        if sector not in TSX_SYMBOLS:
            return {"error": f"Unknown sector: {sector}. Available: {list(TSX_SYMBOLS.keys())}"}
        
        symbols = TSX_SYMBOLS[sector]
        if isinstance(symbols, dict):
            symbols = list(symbols.keys())
        
        overview = {
            "sector": sector,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S ET"),
            "stocks_analyzed": len(symbols),
            "market_summary": {
                "gainers": [],
                "losers": [],
                "high_volume": [],
                "sector_performance": 0
            },
            "educational_insights": [],
            "alerts": []
        }
        
        print(f"🔍 Analyzing {len(symbols)} stocks in {sector} sector...")
        
        total_change = 0
        valid_stocks = 0
        
        for symbol in symbols:
            try:
                stock_data = fetch_comprehensive_stock_data(symbol)
                
                if "market_data" in stock_data and stock_data["market_data"]:
                    market_data = stock_data["market_data"]
                    change_pct = market_data.get("change_percent", 0)
                    volume = market_data.get("volume", 0)
                    
                    # Track sector performance
                    total_change += change_pct
                    valid_stocks += 1
                    
                    # Identify notable movers
                    if change_pct >= 2:
                        overview["market_summary"]["gainers"].append({
                            "symbol": symbol,
                            "change": change_pct,
                            "price": market_data.get("current_price", 0)
                        })
                    elif change_pct <= -2:
                        overview["market_summary"]["losers"].append({
                            "symbol": symbol,
                            "change": change_pct,
                            "price": market_data.get("current_price", 0)
                        })
                    
                    # High volume detection (simplified)
                    if volume > 1000000:  # 1M+ shares
                        overview["market_summary"]["high_volume"].append({
                            "symbol": symbol,
                            "volume": volume,
                            "change": change_pct
                        })
                
                # Be respectful with API calls
                time.sleep(0.2)
                
            except Exception as e:
                print(f"⚠️ Error analyzing {symbol}: {str(e)}")
                continue
        
        # Calculate sector performance
        if valid_stocks > 0:
            overview["market_summary"]["sector_performance"] = round(total_change / valid_stocks, 2)
        
        # Generate educational insights
        sector_perf = overview["market_summary"]["sector_performance"]
        if sector_perf > 1:
            overview["educational_insights"].append(
                f"📈 {sector.title()} sector showing strength (+{sector_perf:.1f}% avg) - look for momentum plays"
            )
        elif sector_perf < -1:
            overview["educational_insights"].append(
                f"📉 {sector.title()} sector under pressure ({sector_perf:.1f}% avg) - potential oversold opportunities"
            )
        else:
            overview["educational_insights"].append(
                f"➡️ {sector.title()} sector neutral ({sector_perf:.1f}% avg) - range-bound trading"
            )
        
        # Sort lists by change percentage
        overview["market_summary"]["gainers"].sort(key=lambda x: x["change"], reverse=True)
        overview["market_summary"]["losers"].sort(key=lambda x: x["change"])
        overview["market_summary"]["high_volume"].sort(key=lambda x: x["volume"], reverse=True)
        
        return overview
        
    except Exception as e:
        return {"error": f"Market overview failed: {str(e)}"}

def check_tsx_market_status() -> Dict:
    """
    Enhanced market status check with Canadian market specifics.
    
    Returns:
        Dictionary with detailed market status and educational context
    """
    now = datetime.now()
    
    # TSX trading hours: 9:30 AM - 4:00 PM ET, Monday-Friday
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
    
    is_weekday = now.weekday() < 5
    is_market_hours = market_open <= now <= market_close
    is_open = is_weekday and is_market_hours
    
    # Calculate time until next open/close
    if is_open:
        time_until_close = market_close - now
        next_event = f"Market closes in {time_until_close}"
    elif is_weekday and now < market_open:
        time_until_open = market_open - now
        next_event = f"Market opens in {time_until_open}"
    elif is_weekday and now > market_close:
        next_open = (now + timedelta(days=1)).replace(hour=9, minute=30, second=0, microsecond=0)
        time_until_open = next_open - now
        next_event = f"Market opens tomorrow in {time_until_open}"
    else:
        # Weekend
        days_until_monday = (7 - now.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 1
        next_monday = now + timedelta(days=days_until_monday)
        next_open = next_monday.replace(hour=9, minute=30, second=0, microsecond=0)
        next_event = f"Market opens Monday at 9:30 AM ET"
    
    status = {
        "is_open": is_open,
        "current_time": now.strftime("%Y-%m-%d %H:%M:%S ET"),
        "status_emoji": "🟢" if is_open else "🔴",
        "status_message": "TSX is OPEN for trading" if is_open else "TSX is CLOSED",
        "next_event": next_event,
        "trading_session": get_trading_session_info(now, is_open),
        "educational_info": get_market_timing_education(now, is_open)
    }
    
    return status

def get_trading_session_info(now: datetime, is_open: bool) -> Dict:
    """Get information about current trading session."""
    if not is_open:
        return {"session": "Closed", "characteristics": "No active trading"}
    
    hour = now.hour
    minute = now.minute
    
    if hour == 9 and minute < 60:
        return {
            "session": "Market Open",
            "characteristics": "High volume, price discovery, gap fills"
        }
    elif hour < 12:
        return {
            "session": "Morning Session", 
            "characteristics": "Institutional activity, trend establishment"
        }
    elif 12 <= hour < 14:
        return {
            "session": "Lunch Period",
            "characteristics": "Lower volume, consolidation patterns"
        }
    elif hour < 15:
        return {
            "session": "Afternoon Session",
            "characteristics": "Moderate activity, position adjustments"
        }
    else:
        return {
            "session": "Market Close",
            "characteristics": "High volume, institutional rebalancing"
        }

def get_market_timing_education(now: datetime, is_open: bool) -> List[str]:
    """Get educational information about market timing."""
    if is_open:
        return [
            "💡 First 30 minutes often show highest volatility as markets digest overnight news",
            "💡 Lunch period (12-1 PM ET) typically has lower volume - fewer trading opportunities",
            "💡 Last hour often sees increased volume as funds and institutions rebalance",
            "💡 Watch for Bank of Canada announcements - they significantly impact Canadian stocks"
        ]
    else:
        if now.weekday() >= 5:  # Weekend
            return [
                "💡 Use weekends to research potential trades and review market analysis",
                "💡 Monitor overnight futures and international markets for Monday gaps",
                "💡 Sunday evening news can impact Monday opening prices",
                "💡 Plan your trading strategy when markets are closed and emotions are neutral"
            ]
        else:  # Weekday after hours
            return [
                "💡 After-hours news can create significant gaps at tomorrow's open",
                "💡 Review today's trading performance and plan improvements",
                "💡 Check Asian and European markets for global trends affecting TSX",
                "💡 Set alerts for overnight developments in your watched stocks"
            ]

# Create the Enhanced Data Collection Agent
data_collection_agent = Agent(
    name="data_collection_agent",
    model="gemini-2.0-flash",
    description="Comprehensive TSX market data collection with Financial Modeling Prep integration and educational insights",
    instruction="""You are an advanced market data specialist for Canadian day traders. Your capabilities include:

COMPREHENSIVE DATA COLLECTION:
- Fetch real-time TSX stock data using Financial Modeling Prep API (primary) and Yahoo Finance (fallback)
- Cross-validate data between multiple sources for accuracy
- Provide detailed company information, financial metrics, and market positioning

EDUCATIONAL MARKET ANALYSIS:
- Explain what market data means in practical terms for day traders
- Identify significant price movements (>3% changes) and volume anomalies
- Provide context about TSX trading sessions and optimal trading times
- Include Canadian market-specific insights (currency impacts, commodity correlations)

SECTOR AND MARKET OVERVIEW:
- Analyze entire sectors (banking, energy, tech, mining) for broader market trends
- Identify top gainers, losers, and high-volume stocks
- Calculate sector performance averages with educational context

CANADIAN MARKET EXPERTISE:
- Understand TSX trading hours and market structure
- Explain how Canadian economics (BoC rates, commodity prices, USD/CAD) affect stocks
- Provide beginner-friendly explanations with emoji indicators for easy scanning

Always prioritize data accuracy, provide fallback information when primary sources fail, and maintain an educational tone that helps new traders understand market dynamics.""",
    tools=[fetch_comprehensive_stock_data, get_market_overview, check_tsx_market_status]
)

if __name__ == "__main__":
    print("🍁 MapleTrade Enhanced Data Collection Agent initialized!")
    print("🔧 Available tools:")
    print("   - fetch_comprehensive_stock_data(): Complete stock analysis with FMP + Yahoo Finance")
    print("   - get_market_overview(): Sector analysis and market trends")
    print("   - check_tsx_market_status(): TSX trading status with educational context")
    print(f"\n🔑 FMP API Status: {'✅ Configured' if FMP_API_KEY != 'demo' else '⚠️ Using demo key'}")
    print("💡 Run with: adk run data_collection_agent")