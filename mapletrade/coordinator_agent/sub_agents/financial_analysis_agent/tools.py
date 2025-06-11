# financial_analysis_agent/tools.py
"""
Financial analysis tools - separated for better organization
"""

from typing import Dict
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def calculate_basic_ratios(symbol: str) -> Dict:
    """
    Calculate basic financial ratios for a single stock.
    
    Args:
        symbol: Stock symbol (e.g., 'TD.TO')
        
    Returns:
        Dictionary with basic ratios and educational explanations
    """
    api_key = os.getenv('FMP_API_KEY', 'demo')
    
    # Normalize Canadian symbol
    if not symbol.endswith('.TO'):
        symbol = f"{symbol}.TO"
    
    fmp_symbol = symbol.replace('.TO', '.TRT')
    
    try:
        # Try FMP first
        url = f"https://financialmodelingprep.com/api/v3/ratios-ttm/{fmp_symbol}"
        response = requests.get(url, params={'apikey': api_key}, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                ratios = data[0]
                
                result = {
                    "symbol": symbol,
                    "data_source": "Financial Modeling Prep API",
                    "raw_data": {
                        "pe_ratio": ratios.get("priceEarningsRatio"),
                        "roe": ratios.get("returnOnEquity"), 
                        "current_ratio": ratios.get("currentRatio"),
                        "debt_to_equity": ratios.get("debtEquityRatio")
                    },
                    "calculation_formulas": {
                        "pe_ratio": "Stock Price ÷ Earnings Per Share",
                        "roe": "Net Income ÷ Shareholders' Equity", 
                        "current_ratio": "Current Assets ÷ Current Liabilities",
                        "debt_to_equity": "Total Debt ÷ Shareholders' Equity"
                    },
                    "verification_sources": [
                        "https://www.investopedia.com/terms/p/price-earningsratio.asp",
                        "https://www.investopedia.com/terms/r/returnonequity.asp",
                        "https://www.investopedia.com/terms/c/currentratio.asp",
                        "https://www.investopedia.com/terms/d/debtequityratio.asp"
                    ],
                    "educational_warning": "⚠️ VERIFY THESE CALCULATIONS: This data comes from FMP API. Always cross-check with company financial statements, Yahoo Finance, or other sources before making decisions.",
                    "disclaimers": [
                        "📋 Data source: Financial Modeling Prep API - not this agent",
                        "📋 Calculations done by FMP using company filings",
                        "📋 This agent only displays and explains the data",
                        "📋 Always verify with multiple sources",
                        "📋 Consult financial professionals for investment advice"
                    ]
                }
                return result
        
        # Fallback to Yahoo Finance if FMP fails
        print(f"📈 FMP failed, falling back to Yahoo Finance for {symbol}...")
        import yfinance as yf
        
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        if info:
            result = {
                "symbol": symbol,
                "data_source": "Yahoo Finance (Fallback)",
                "raw_data": {
                    "pe_ratio": info.get('trailingPE'),
                    "roe": info.get('returnOnEquity'),
                    "current_ratio": info.get('currentRatio'),
                    "debt_to_equity": info.get('debtToEquity')
                },
                "calculation_formulas": {
                    "pe_ratio": "Stock Price ÷ Earnings Per Share",
                    "roe": "Net Income ÷ Shareholders' Equity", 
                    "current_ratio": "Current Assets ÷ Current Liabilities",
                    "debt_to_equity": "Total Debt ÷ Shareholders' Equity"
                },
                "verification_sources": [
                    "https://www.investopedia.com/terms/p/price-earningsratio.asp",
                    "https://www.investopedia.com/terms/r/returnonequity.asp",
                    "https://www.investopedia.com/terms/c/currentratio.asp",
                    "https://www.investopedia.com/terms/d/debtequityratio.asp"
                ],
                "educational_warning": "⚠️ VERIFY THESE CALCULATIONS: This data comes from Yahoo Finance. Always cross-check with company financial statements or other sources before making decisions.",
                "disclaimers": [
                    "📋 Data source: Yahoo Finance API - not this agent",
                    "📋 Calculations done by Yahoo using various data providers",
                    "📋 This agent only displays and explains the data",
                    "📋 Always verify with multiple sources",
                    "📋 Consult financial professionals for investment advice"
                ]
            }
            return result
        
        return {
            "error": f"Could not fetch ratios for {symbol}", 
            "source": "Both FMP and Yahoo Finance failed",
            "fallback_options": [
                "Try Yahoo Finance manually",
                "Check company investor relations page", 
                "Use financial websites like Morningstar"
            ]
        }
        
    except Exception as e:
        return {
            "error": f"Analysis failed: {str(e)}", 
            "source": "Financial Analysis Agent",
            "manual_alternatives": [
                "Calculate P/E: Current Price ÷ EPS from latest earnings",
                "Find ROE in company's annual report",
                "Get ratios from Yahoo Finance or Morningstar"
            ]
        }