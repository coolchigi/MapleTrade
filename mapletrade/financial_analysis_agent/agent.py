"""
MapleTrade Financial Analysis Agent
Comprehensive financial analysis with accurate Canadian stock support and educational insights
"""

import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import os
from dotenv import load_dotenv
from google.adk.agents import Agent
import json
import time
import numpy as np

# Load environment variables
load_dotenv()

# Configuration
FMP_API_KEY = os.getenv('FMP_API_KEY', 'demo')
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"
ENABLE_FMP_PREMIUM = os.getenv('ENABLE_FMP_PREMIUM', 'False').lower() == 'true'

# Canadian major stocks with proper sector classification
TSX_MAJOR_STOCKS = {
    "SHOP.TO": {"name": "Shopify Inc", "sector": "Technology", "fmp_symbol": "SHOP.TRT"},
    "TD.TO": {"name": "Toronto-Dominion Bank", "sector": "Financial Services", "fmp_symbol": "TD.TRT"},
    "RY.TO": {"name": "Royal Bank of Canada", "sector": "Financial Services", "fmp_symbol": "RY.TRT"},
    "CNR.TO": {"name": "Canadian National Railway", "sector": "Industrials", "fmp_symbol": "CNR.TRT"},
    "SU.TO": {"name": "Suncor Energy", "sector": "Energy", "fmp_symbol": "SU.TRT"},
    "WEED.TO": {"name": "Canopy Growth", "sector": "Healthcare", "fmp_symbol": "WEED.TRT"},
    "AC.TO": {"name": "Air Canada", "sector": "Industrials", "fmp_symbol": "AC.TRT"},
    "BBD-B.TO": {"name": "Bombardier Inc", "sector": "Industrials", "fmp_symbol": "BBD-B.TRT"}
}

class FinancialAnalysisError(Exception):
    """Custom exception for financial analysis errors"""
    pass

def fetch_fmp_data_with_retry(endpoint: str, params: Dict = None, max_retries: int = 3) -> Dict:
    """
    Fetch data from Financial Modeling Prep API with robust error handling and retries.
    
    Args:
        endpoint: FMP API endpoint (without base URL)
        params: Additional query parameters
        max_retries: Maximum number of retry attempts
        
    Returns:
        Dictionary with API response data or error information
    """
    for attempt in range(max_retries):
        try:
            if params is None:
                params = {}
            
            # Add API key to parameters
            params['apikey'] = FMP_API_KEY
            
            url = f"{FMP_BASE_URL}/{endpoint}"
            response = requests.get(url, params=params, timeout=15)
            
            # Log the request for debugging
            if attempt == 0:  # Only log on first attempt
                print(f"🔍 FMP Request: {url}")
            
            response.raise_for_status()
            
            data = response.json()
            
            # Handle various response scenarios
            if not data:
                if attempt < max_retries - 1:
                    print(f"⚠️ Empty response, retrying... (attempt {attempt + 1})")
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                return {"error": "No data returned from FMP API", "endpoint": endpoint}
            
            # Check for API error messages in response
            if isinstance(data, dict) and "Error Message" in data:
                return {"error": f"FMP API Error: {data['Error Message']}", "endpoint": endpoint}
            
            return {"data": data, "source": "FMP", "timestamp": datetime.now().isoformat()}
            
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                print(f"⚠️ Request failed, retrying... (attempt {attempt + 1}): {str(e)}")
                time.sleep(2 ** attempt)
                continue
            return {"error": f"FMP API request failed after {max_retries} attempts: {str(e)}", "endpoint": endpoint}
        
        except json.JSONDecodeError as e:
            if attempt < max_retries - 1:
                print(f"⚠️ JSON decode error, retrying... (attempt {attempt + 1})")
                time.sleep(2 ** attempt)
                continue
            return {"error": f"Invalid JSON response from FMP: {str(e)}", "endpoint": endpoint}
        
        except Exception as e:
            return {"error": f"Unexpected error fetching from FMP: {str(e)}", "endpoint": endpoint}
    
    return {"error": f"Max retries ({max_retries}) exceeded", "endpoint": endpoint}

def normalize_canadian_symbol(symbol: str) -> Tuple[str, str]:
    """
    Normalize Canadian stock symbols for different APIs.
    
    Args:
        symbol: Input symbol in various formats
        
    Returns:
        Tuple of (yahoo_symbol, fmp_symbol)
    """
    # Clean the symbol
    symbol = symbol.upper().strip()
    
    # Handle various input formats
    if symbol.endswith('.TO'):
        base_symbol = symbol[:-3]
        yahoo_symbol = symbol
        fmp_symbol = f"{base_symbol}.TRT"
    elif symbol.endswith('.TRT'):
        base_symbol = symbol[:-4]
        yahoo_symbol = f"{base_symbol}.TO"
        fmp_symbol = symbol
    else:
        # Assume it's a base symbol
        yahoo_symbol = f"{symbol}.TO"
        fmp_symbol = f"{symbol}.TRT"
    
    return yahoo_symbol, fmp_symbol

def calculate_financial_ratios(symbol: str) -> Dict:
    """
    Calculate comprehensive financial ratios for a Canadian stock with multiple data sources.
    
    Args:
        symbol: Stock symbol (will be normalized for different APIs)
        
    Returns:
        Dictionary with comprehensive financial ratio analysis and educational insights
    """
    try:
        yahoo_symbol, fmp_symbol = normalize_canadian_symbol(symbol)
        
        result = {
            "symbol": yahoo_symbol,
            "analysis_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S ET"),
            "data_sources": [],
            "financial_ratios": {},
            "valuation_metrics": {},
            "profitability_ratios": {},
            "liquidity_ratios": {},
            "leverage_ratios": {},
            "efficiency_ratios": {},
            "educational_insights": [],
            "warnings": [],
            "errors": []
        }
        
        # 1. Try FMP for comprehensive ratio data
        print(f"🔍 Fetching financial ratios from FMP for {fmp_symbol}...")
        
        # Get TTM (Trailing Twelve Months) ratios for most current data
        fmp_ratios_ttm = fetch_fmp_data_with_retry(f"ratios-ttm/{fmp_symbol}")
        
        if "data" in fmp_ratios_ttm and fmp_ratios_ttm["data"]:
            ratio_data = fmp_ratios_ttm["data"][0]
            result["data_sources"].append("FMP TTM Ratios")
            
            # Valuation Ratios
            result["valuation_metrics"] = {
                "pe_ratio": ratio_data.get("priceEarningsRatio"),
                "pb_ratio": ratio_data.get("priceToBookRatio"),
                "ps_ratio": ratio_data.get("priceToSalesRatio"),
                "peg_ratio": ratio_data.get("pegRatio"),
                "ev_to_ebitda": ratio_data.get("enterpriseValueOverEBITDA"),
                "ev_to_sales": ratio_data.get("priceToSalesRatio"),  # Note: FMP may use different naming
                "price_to_cash_flow": ratio_data.get("priceCashFlowRatio")
            }
            
            # Profitability Ratios
            result["profitability_ratios"] = {
                "roe": ratio_data.get("returnOnEquity"),
                "roa": ratio_data.get("returnOnAssets"),
                "roic": ratio_data.get("returnOnCapitalEmployed"),
                "gross_margin": ratio_data.get("grossProfitMargin"),
                "operating_margin": ratio_data.get("operatingProfitMargin"),
                "net_margin": ratio_data.get("netProfitMargin"),
                "ebitda_margin": ratio_data.get("ebitdaratio")
            }
            
            # Liquidity Ratios
            result["liquidity_ratios"] = {
                "current_ratio": ratio_data.get("currentRatio"),
                "quick_ratio": ratio_data.get("quickRatio"),
                "cash_ratio": ratio_data.get("cashRatio"),
                "operating_cash_flow_ratio": ratio_data.get("operatingCashFlowPerShare")
            }
            
            # Leverage Ratios
            result["leverage_ratios"] = {
                "debt_to_equity": ratio_data.get("debtEquityRatio"),
                "debt_to_assets": ratio_data.get("debtRatio"),
                "times_interest_earned": ratio_data.get("timesInterestEarnedRatio"),
                "debt_to_capital": ratio_data.get("capitalEmployed")  # May need adjustment
            }
            
            # Efficiency Ratios
            result["efficiency_ratios"] = {
                "asset_turnover": ratio_data.get("assetTurnover"),
                "inventory_turnover": ratio_data.get("inventoryTurnover"),
                "receivables_turnover": ratio_data.get("receivablesTurnover"),
                "payables_turnover": ratio_data.get("payablesTurnover")
            }
            
        else:
            result["errors"].append(f"FMP TTM ratios unavailable: {fmp_ratios_ttm.get('error', 'Unknown error')}")
        
        # 2. Get annual ratios for trend analysis
        fmp_ratios_annual = fetch_fmp_data_with_retry(f"ratios/{fmp_symbol}", {"limit": 5})
        
        if "data" in fmp_ratios_annual and fmp_ratios_annual["data"]:
            result["data_sources"].append("FMP Annual Ratios")
            annual_data = fmp_ratios_annual["data"]
            
            # Calculate trends if we have historical data
            if len(annual_data) >= 2:
                current_roe = annual_data[0].get("returnOnEquity", 0)
                prior_roe = annual_data[1].get("returnOnEquity", 0)
                
                if current_roe and prior_roe and prior_roe != 0:
                    roe_trend = ((current_roe - prior_roe) / prior_roe) * 100
                    result["financial_ratios"]["roe_trend_pct"] = round(roe_trend, 2)
        
        # 3. Fallback to Yahoo Finance for basic metrics
        if not result["data_sources"]:
            print(f"📈 Falling back to Yahoo Finance for {yahoo_symbol}...")
            try:
                ticker = yf.Ticker(yahoo_symbol)
                info = ticker.info
                
                if info:
                    result["data_sources"].append("Yahoo Finance")
                    
                    # Basic valuation metrics from Yahoo
                    result["valuation_metrics"] = {
                        "pe_ratio": info.get('trailingPE'),
                        "pb_ratio": info.get('priceToBook'),
                        "ps_ratio": info.get('priceToSalesTrailing12Months'),
                        "peg_ratio": info.get('pegRatio'),
                        "ev_to_ebitda": info.get('enterpriseToEbitda'),
                        "forward_pe": info.get('forwardPE')
                    }
                    
                    # Basic profitability metrics
                    result["profitability_ratios"] = {
                        "roe": info.get('returnOnEquity'),
                        "roa": info.get('returnOnAssets'),
                        "gross_margin": info.get('grossMargins'),
                        "operating_margin": info.get('operatingMargins'),
                        "net_margin": info.get('profitMargins')
                    }
                    
                    # Basic financial health metrics
                    result["liquidity_ratios"] = {
                        "current_ratio": info.get('currentRatio'),
                        "quick_ratio": info.get('quickRatio')
                    }
                    
                    result["leverage_ratios"] = {
                        "debt_to_equity": info.get('debtToEquity')
                    }
                    
            except Exception as e:
                result["errors"].append(f"Yahoo Finance error: {str(e)}")
        
        # 4. Generate educational insights and analysis
        _generate_ratio_insights(result)
        
        # 5. Add Canadian market context
        _add_canadian_market_context(result, yahoo_symbol)
        
        return result
        
    except Exception as e:
        return {
            "symbol": symbol,
            "error": f"Critical error in financial ratio calculation: {str(e)}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S ET")
        }

def _generate_ratio_insights(result: Dict) -> None:
    """Generate educational insights based on calculated ratios."""
    
    valuation = result.get("valuation_metrics", {})
    profitability = result.get("profitability_ratios", {})
    liquidity = result.get("liquidity_ratios", {})
    leverage = result.get("leverage_ratios", {})
    
    # PE Ratio Analysis
    pe_ratio = valuation.get("pe_ratio")
    if pe_ratio and pe_ratio > 0:
        if pe_ratio > 25:
            result["educational_insights"].append(
                f"📈 High P/E Ratio ({pe_ratio:.1f}): Stock may be overvalued or investors expect high growth. Compare to sector average."
            )
        elif pe_ratio < 10:
            result["educational_insights"].append(
                f"📉 Low P/E Ratio ({pe_ratio:.1f}): Stock may be undervalued or facing challenges. Research company fundamentals."
            )
        else:
            result["educational_insights"].append(
                f"➡️ Moderate P/E Ratio ({pe_ratio:.1f}): Reasonable valuation. Compare to industry peers for context."
            )
    
    # ROE Analysis
    roe = profitability.get("roe")
    if roe and roe > 0:
        roe_pct = roe * 100 if roe < 1 else roe  # Handle decimal vs percentage format
        if roe_pct > 20:
            result["educational_insights"].append(
                f"🏆 Excellent ROE ({roe_pct:.1f}%): Company efficiently generates profits from shareholders' equity."
            )
        elif roe_pct > 15:
            result["educational_insights"].append(
                f"✅ Good ROE ({roe_pct:.1f}%): Above-average return on equity indicates healthy profitability."
            )
        elif roe_pct < 10:
            result["educational_insights"].append(
                f"⚠️ Low ROE ({roe_pct:.1f}%): May indicate inefficient use of equity or industry challenges."
            )
    
    # Current Ratio Analysis
    current_ratio = liquidity.get("current_ratio")
    if current_ratio:
        if current_ratio > 2.5:
            result["educational_insights"].append(
                f"💰 High Current Ratio ({current_ratio:.1f}): Strong liquidity but may indicate inefficient cash use."
            )
        elif current_ratio < 1.0:
            result["warnings"].append(
                f"🚨 Low Current Ratio ({current_ratio:.1f}): Potential liquidity concerns - company may struggle to meet short-term obligations."
            )
        else:
            result["educational_insights"].append(
                f"✅ Healthy Current Ratio ({current_ratio:.1f}): Good balance of liquidity and efficiency."
            )
    
    # Debt to Equity Analysis
    debt_to_equity = leverage.get("debt_to_equity")
    if debt_to_equity:
        if debt_to_equity > 2.0:
            result["warnings"].append(
                f"⚠️ High Debt-to-Equity ({debt_to_equity:.1f}): Significant leverage may amplify risks during downturns."
            )
        elif debt_to_equity < 0.3:
            result["educational_insights"].append(
                f"🛡️ Conservative Debt Level ({debt_to_equity:.1f}): Low financial risk but may miss growth opportunities."
            )
    
    # Overall assessment
    if not result["educational_insights"] and not result["warnings"]:
        result["educational_insights"].append(
            "📊 Limited ratio data available. Consider checking data sources or trying again later."
        )

def _add_canadian_market_context(result: Dict, symbol: str) -> None:
    """Add Canadian market-specific context and insights."""
    
    # Check if it's a major TSX stock
    if symbol in TSX_MAJOR_STOCKS:
        stock_info = TSX_MAJOR_STOCKS[symbol]
        sector = stock_info["sector"]
        
        result["educational_insights"].extend([
            f"🍁 TSX Major Stock: {stock_info['name']} ({sector} sector)",
            f"💡 As a major TSX stock, this is likely included in Canadian index funds and ETFs",
            f"💡 {sector} sector performance often correlates with broader Canadian economic trends"
        ])
        
        # Sector-specific insights
        if sector == "Financial Services":
            result["educational_insights"].append(
                "🏦 Banking Sector: Watch Bank of Canada interest rate decisions - they significantly impact bank profitability"
            )
        elif sector == "Energy":
            result["educational_insights"].append(
                "⛽ Energy Sector: Performance closely tied to oil prices and USD/CAD exchange rate"
            )
        elif sector == "Technology":
            result["educational_insights"].append(
                "💻 Tech Sector: Consider currency exposure - many Canadian tech companies earn revenue in USD"
            )
    
    # Add general Canadian market insights
    result["educational_insights"].extend([
        "🇨🇦 Canadian Stock Considerations:",
        "• Currency risk if you're investing from other countries",
        "• Commodity exposure through TSX energy and materials sectors",
        "• Banking sector dominated by 'Big 6' Canadian banks",
        "• Consider withholding taxes for non-Canadian investors"
    ])

def perform_peer_comparison(symbol: str, sector: Optional[str] = None) -> Dict:
    """
    Compare a stock's financial ratios to sector peers.
    
    Args:
        symbol: Primary stock symbol to analyze
        sector: Sector for peer comparison (auto-detected if None)
        
    Returns:
        Dictionary with peer comparison analysis
    """
    try:
        yahoo_symbol, fmp_symbol = normalize_canadian_symbol(symbol)
        
        result = {
            "primary_stock": yahoo_symbol,
            "analysis_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S ET"),
            "sector": sector,
            "peer_comparison": {},
            "ranking": {},
            "educational_insights": [],
            "errors": []
        }
        
        # Get primary stock ratios
        primary_analysis = calculate_financial_ratios(symbol)
        
        if "error" in primary_analysis:
            return {"error": f"Could not analyze primary stock: {primary_analysis['error']}"}
        
        # Auto-detect sector if not provided
        if not sector and yahoo_symbol in TSX_MAJOR_STOCKS:
            sector = TSX_MAJOR_STOCKS[yahoo_symbol]["sector"]
            result["sector"] = sector
        
        # Find peers in the same sector
        peers = []
        if sector:
            for sym, info in TSX_MAJOR_STOCKS.items():
                if info["sector"] == sector and sym != yahoo_symbol:
                    peers.append(sym)
        
        if not peers:
            # Use a default set of major Canadian stocks for comparison
            peers = [sym for sym in TSX_MAJOR_STOCKS.keys() if sym != yahoo_symbol][:3]
            result["educational_insights"].append(
                "📊 Using major TSX stocks for comparison due to limited sector data"
            )
        
        # Analyze peers
        peer_data = {}
        for peer in peers[:3]:  # Limit to 3 peers to avoid API rate limits
            print(f"🔍 Analyzing peer: {peer}")
            peer_analysis = calculate_financial_ratios(peer)
            
            if "error" not in peer_analysis:
                peer_data[peer] = peer_analysis
                time.sleep(1)  # Rate limiting
        
        # Compare key metrics
        metrics_to_compare = [
            ("pe_ratio", "P/E Ratio"),
            ("pb_ratio", "P/B Ratio"),
            ("roe", "Return on Equity"),
            ("current_ratio", "Current Ratio"),
            ("debt_to_equity", "Debt-to-Equity")
        ]
        
        for metric_key, metric_name in metrics_to_compare:
            comparison = _compare_metric_across_peers(
                primary_analysis, peer_data, metric_key, metric_name
            )
            if comparison:
                result["peer_comparison"][metric_key] = comparison
        
        # Generate ranking insights
        _generate_peer_ranking_insights(result, primary_analysis, peer_data)
        
        return result
        
    except Exception as e:
        return {
            "error": f"Peer comparison failed: {str(e)}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S ET")
        }

def _compare_metric_across_peers(primary_analysis: Dict, peer_data: Dict, metric_key: str, metric_name: str) -> Dict:
    """Compare a specific metric across peers."""
    
    # Extract metric from different ratio categories
    primary_value = None
    for category in ["valuation_metrics", "profitability_ratios", "liquidity_ratios", "leverage_ratios"]:
        if category in primary_analysis and metric_key in primary_analysis[category]:
            primary_value = primary_analysis[category][metric_key]
            break
    
    if primary_value is None:
        return None
    
    peer_values = {}
    for peer_symbol, peer_analysis in peer_data.items():
        for category in ["valuation_metrics", "profitability_ratios", "liquidity_ratios", "leverage_ratios"]:
            if category in peer_analysis and metric_key in peer_analysis[category]:
                peer_value = peer_analysis[category][metric_key]
                if peer_value is not None:
                    peer_values[peer_symbol] = peer_value
                break
    
    if not peer_values:
        return None
    
    # Calculate statistics
    all_values = list(peer_values.values()) + [primary_value]
    peer_avg = np.mean(list(peer_values.values()))
    
    return {
        "metric_name": metric_name,
        "primary_value": primary_value,
        "peer_average": round(peer_avg, 3),
        "peer_values": peer_values,
        "vs_peers": "Above Average" if primary_value > peer_avg else "Below Average",
        "percentile": round((sum(1 for v in all_values if v < primary_value) / len(all_values)) * 100, 1)
    }

def _generate_peer_ranking_insights(result: Dict, primary_analysis: Dict, peer_data: Dict) -> None:
    """Generate insights based on peer comparison rankings."""
    
    comparison_data = result.get("peer_comparison", {})
    
    if not comparison_data:
        result["educational_insights"].append(
            "📊 Limited peer comparison data available. Consider manual comparison with sector competitors."
        )
        return
    
    above_average_count = sum(1 for comp in comparison_data.values() 
                             if comp and comp.get("vs_peers") == "Above Average")
    total_metrics = len(comparison_data)
    
    if above_average_count >= total_metrics * 0.7:
        result["educational_insights"].append(
            f"🏆 Strong Peer Performance: Outperforming peers in {above_average_count}/{total_metrics} key metrics"
        )
    elif above_average_count >= total_metrics * 0.4:
        result["educational_insights"].append(
            f"➡️ Mixed Peer Performance: Competitive in {above_average_count}/{total_metrics} key metrics"
        )
    else:
        result["educational_insights"].append(
            f"⚠️ Below Peer Average: Underperforming in {total_metrics - above_average_count}/{total_metrics} key metrics"
        )
    
    # Specific metric insights
    pe_comparison = comparison_data.get("pe_ratio")
    if pe_comparison and pe_comparison.get("vs_peers") == "Below Average":
        result["educational_insights"].append(
            "💡 Lower P/E than peers may indicate value opportunity or fundamental concerns"
        )
    
    roe_comparison = comparison_data.get("roe")
    if roe_comparison and roe_comparison.get("vs_peers") == "Above Average":
        result["educational_insights"].append(
            "✅ Higher ROE than peers suggests efficient profit generation"
        )

def analyze_financial_health_score(symbol: str) -> Dict:
    """
    Calculate a comprehensive financial health score for educational purposes.
    
    Args:
        symbol: Stock symbol to analyze
        
    Returns:
        Dictionary with financial health score and detailed breakdown
    """
    try:
        analysis = calculate_financial_ratios(symbol)
        
        if "error" in analysis:
            return {"error": f"Could not calculate health score: {analysis['error']}"}
        
        result = {
            "symbol": analysis["symbol"],
            "analysis_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S ET"),
            "health_score": 0,
            "score_breakdown": {},
            "strengths": [],
            "weaknesses": [],
            "educational_explanation": [],
            "investment_considerations": []
        }
        
        # Score components (each out of 20 points, total 100)
        scores = {}
        
        # 1. Profitability Score (20 points)
        profitability = analysis.get("profitability_ratios", {})
        roe = profitability.get("roe")
        net_margin = profitability.get("net_margin")
        
        prof_score = 0
        if roe:
            roe_pct = roe * 100 if roe < 1 else roe
            if roe_pct > 20: prof_score += 10
            elif roe_pct > 15: prof_score += 8
            elif roe_pct > 10: prof_score += 6
            elif roe_pct > 5: prof_score += 4
        
        if net_margin:
            margin_pct = net_margin * 100 if net_margin < 1 else net_margin
            if margin_pct > 15: prof_score += 10
            elif margin_pct > 10: prof_score += 8
            elif margin_pct > 5: prof_score += 6
            elif margin_pct > 0: prof_score += 4
        
        scores["profitability"] = prof_score
        
        # 2. Liquidity Score (20 points)
        liquidity = analysis.get("liquidity_ratios", {})
        current_ratio = liquidity.get("current_ratio")
        quick_ratio = liquidity.get("quick_ratio")
        
        liq_score = 0
        if current_ratio:
            if 1.5 <= current_ratio <= 3.0: liq_score += 10
            elif 1.0 <= current_ratio < 1.5: liq_score += 7
            elif current_ratio >= 3.0: liq_score += 6
            elif current_ratio >= 0.8: liq_score += 4
        
        if quick_ratio:
            if quick_ratio >= 1.0: liq_score += 10
            elif quick_ratio >= 0.7: liq_score += 7
            elif quick_ratio >= 0.5: liq_score += 4
        
        scores["liquidity"] = liq_score
        
        # 3. Leverage Score (20 points)
        leverage = analysis.get("leverage_ratios", {})
        debt_to_equity = leverage.get("debt_to_equity")
        
        lev_score = 0
        if debt_to_equity is not None:
            if debt_to_equity <= 0.3: lev_score += 20
            elif debt_to_equity <= 0.6: lev_score += 15
            elif debt_to_equity <= 1.0: lev_score += 10
            elif debt_to_equity <= 2.0: lev_score += 5
            # Above 2.0 gets 0 points
        
        scores["leverage"] = lev_score
        
        # 4. Valuation Score (20 points)
        valuation = analysis.get("valuation_metrics", {})
        pe_ratio = valuation.get("pe_ratio")
        pb_ratio = valuation.get("pb_ratio")
        
        val_score = 0
        if pe_ratio and pe_ratio > 0:
            if 10 <= pe_ratio <= 20: val_score += 10
            elif 8 <= pe_ratio < 10 or 20 < pe_ratio <= 25: val_score += 8
            elif 5 <= pe_ratio < 8 or 25 < pe_ratio <= 30: val_score += 6
            elif pe_ratio > 30: val_score += 2
        
        if pb_ratio and pb_ratio > 0:
            if 1.0 <= pb_ratio <= 3.0: val_score += 10
            elif 0.5 <= pb_ratio < 1.0 or 3.0 < pb_ratio <= 5.0: val_score += 8
            elif pb_ratio > 5.0: val_score += 4
        
        scores["valuation"] = val_score
        
        # 5. Efficiency Score (20 points) 
        efficiency = analysis.get("efficiency_ratios", {})
        asset_turnover = efficiency.get("asset_turnover")
        
        eff_score = 10  # Base score if no data
        if asset_turnover:
            if asset_turnover >= 1.0: eff_score = 20
            elif asset_turnover >= 0.75: eff_score = 15
            elif asset_turnover >= 0.5: eff_score = 10
            else: eff_score = 5
        
        scores["efficiency"] = eff_score
        
        # Calculate total score
        total_score = sum(scores.values())
        result["health_score"] = total_score
        result["score_breakdown"] = scores
        
        # Generate score interpretation
        _interpret_health_score(result, analysis, scores)
        
        return result
        
    except Exception as e:
        return {
            "error": f"Financial health score calculation failed: {str(e)}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S ET")
        }

def _interpret_health_score(result: Dict, analysis: Dict, scores: Dict) -> None:
    """Interpret the financial health score and provide educational insights."""
    
    total_score = result["health_score"]
    
    # Overall health assessment
    if total_score >= 80:
        health_grade = "Excellent (A)"
        result["educational_explanation"].append(
            "🏆 Excellent Financial Health: Strong across all key metrics. This company shows robust financial management."
        )
    elif total_score >= 70:
        health_grade = "Good (B)"
        result["educational_explanation"].append(
            "✅ Good Financial Health: Solid fundamentals with some areas for improvement."
        )
    elif total_score >= 60:
        health_grade = "Fair (C)"
        result["educational_explanation"].append(
            "⚠️ Fair Financial Health: Mixed results - some strengths but notable weaknesses to consider."
        )
    elif total_score >= 50:
        health_grade = "Poor (D)"
        result["educational_explanation"].append(
            "🚨 Poor Financial Health: Significant concerns across multiple metrics. High investment risk."
        )
    else:
        health_grade = "Very Poor (F)"
        result["educational_explanation"].append(
            "❌ Very Poor Financial Health: Critical financial issues. Extreme caution advised."
        )
    
    result["health_grade"] = health_grade
    
    # Identify strengths and weaknesses
    score_categories = {
        "profitability": "Profitability",
        "liquidity": "Liquidity", 
        "leverage": "Debt Management",
        "valuation": "Valuation",
        "efficiency": "Operational Efficiency"
    }
    
    for category, score in scores.items():
        category_name = score_categories.get(category, category.title())
        
        if score >= 16:  # 80% of 20 points
            result["strengths"].append(f"💪 {category_name}: Excellent performance")
        elif score >= 12:  # 60% of 20 points
            result["strengths"].append(f"✅ {category_name}: Good performance")
        elif score < 8:   # Less than 40% of 20 points
            result["weaknesses"].append(f"⚠️ {category_name}: Needs improvement")
    
    # Investment considerations based on score
    if total_score >= 70:
        result["investment_considerations"].extend([
            "💡 Conservative investors: Strong fundamentals make this suitable for defensive portfolios",
            "💡 Growth investors: Check if strong fundamentals support future growth potential",
            "💡 Value investors: High score may indicate fair valuation - compare to sector peers"
        ])
    elif total_score >= 50:
        result["investment_considerations"].extend([
            "💡 Risk assessment: Mixed fundamentals require deeper analysis of specific weaknesses",
            "💡 Diversification: Consider as part of diversified portfolio rather than concentration",
            "💡 Monitoring: Requires ongoing review of improving/deteriorating metrics"
        ])
    else:
        result["investment_considerations"].extend([
            "🚨 High risk: Poor fundamentals suggest significant investment risk",
            "🚨 Speculation only: Suitable only for highly risk-tolerant investors",
            "🚨 Turnaround potential: May be suitable if you believe in management's recovery plan"
        ])
    
    # Add Canadian-specific considerations
    result["investment_considerations"].extend([
        "🇨🇦 Currency consideration: Factor in CAD/USD exchange rate for international investors",
        "🇨🇦 Tax implications: Consider Canadian withholding taxes and capital gains treatment",
        "🇨🇦 TSX hours: Plan trading around 9:30 AM - 4:00 PM ET trading window"
    ])

def generate_comprehensive_report(symbol: str) -> Dict:
    """
    Generate a comprehensive financial analysis report combining all analysis functions.
    
    Args:
        symbol: Stock symbol to analyze
        
    Returns:
        Dictionary with comprehensive analysis report
    """
    try:
        yahoo_symbol, fmp_symbol = normalize_canadian_symbol(symbol)
        
        report = {
            "symbol": yahoo_symbol,
            "company_name": TSX_MAJOR_STOCKS.get(yahoo_symbol, {}).get("name", "Unknown Company"),
            "report_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S ET"),
            "executive_summary": {},
            "detailed_analysis": {},
            "peer_comparison": {},
            "health_score": {},
            "recommendations": [],
            "risk_factors": [],
            "educational_notes": [],
            "data_quality": {},
            "errors": []
        }
        
        print(f"📊 Generating comprehensive report for {yahoo_symbol}...")
        
        # 1. Financial Ratios Analysis
        print("🔍 Calculating financial ratios...")
        ratios_analysis = calculate_financial_ratios(symbol)
        
        if "error" not in ratios_analysis:
            report["detailed_analysis"]["financial_ratios"] = ratios_analysis
            report["data_quality"]["ratios_available"] = True
        else:
            report["errors"].append(f"Ratios analysis: {ratios_analysis['error']}")
            report["data_quality"]["ratios_available"] = False
        
        # 2. Financial Health Score
        print("🏥 Calculating financial health score...")
        health_analysis = analyze_financial_health_score(symbol)
        
        if "error" not in health_analysis:
            report["health_score"] = health_analysis
            report["data_quality"]["health_score_available"] = True
        else:
            report["errors"].append(f"Health score: {health_analysis['error']}")
            report["data_quality"]["health_score_available"] = False
        
        # 3. Peer Comparison (if we have sector info)
        if yahoo_symbol in TSX_MAJOR_STOCKS:
            print("👥 Performing peer comparison...")
            sector = TSX_MAJOR_STOCKS[yahoo_symbol]["sector"]
            peer_analysis = perform_peer_comparison(symbol, sector)
            
            if "error" not in peer_analysis:
                report["peer_comparison"] = peer_analysis
                report["data_quality"]["peer_comparison_available"] = True
            else:
                report["errors"].append(f"Peer comparison: {peer_analysis['error']}")
                report["data_quality"]["peer_comparison_available"] = False
        
        # 4. Generate Executive Summary
        _generate_executive_summary(report)
        
        # 5. Generate Recommendations
        _generate_investment_recommendations(report)
        
        # 6. Add Educational Content
        _add_comprehensive_educational_content(report)
        
        return report
        
    except Exception as e:
        return {
            "symbol": symbol,
            "error": f"Comprehensive report generation failed: {str(e)}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S ET")
        }

def _generate_executive_summary(report: Dict) -> None:
    """Generate executive summary based on all available analysis."""
    
    summary = {}
    
    # Health Score Summary
    health_data = report.get("health_score", {})
    if health_data and "health_score" in health_data:
        score = health_data["health_score"]
        grade = health_data.get("health_grade", "Unknown")
        summary["financial_health"] = f"{score}/100 ({grade})"
    
    # Key Ratios Summary
    ratios_data = report.get("detailed_analysis", {}).get("financial_ratios", {})
    if ratios_data:
        valuation = ratios_data.get("valuation_metrics", {})
        profitability = ratios_data.get("profitability_ratios", {})
        
        pe_ratio = valuation.get("pe_ratio")
        roe = profitability.get("roe")
        
        if pe_ratio:
            summary["valuation"] = f"P/E: {pe_ratio:.1f}"
        if roe:
            roe_pct = roe * 100 if roe < 1 else roe
            summary["profitability"] = f"ROE: {roe_pct:.1f}%"
    
    # Peer Ranking
    peer_data = report.get("peer_comparison", {})
    if peer_data and "peer_comparison" in peer_data:
        comparisons = peer_data["peer_comparison"]
        above_avg_count = sum(1 for comp in comparisons.values() 
                             if comp and comp.get("vs_peers") == "Above Average")
        total_metrics = len(comparisons)
        summary["peer_ranking"] = f"{above_avg_count}/{total_metrics} metrics above peer average"
    
    # Overall Assessment
    if health_data and "health_score" in health_data:
        score = health_data["health_score"]
        if score >= 70:
            summary["investment_thesis"] = "Strong fundamentals support investment consideration"
        elif score >= 50:
            summary["investment_thesis"] = "Mixed fundamentals require careful evaluation"
        else:
            summary["investment_thesis"] = "Weak fundamentals suggest high investment risk"
    
    report["executive_summary"] = summary

def get_ratio_explanations() -> Dict:
    """
    Provide educational explanations and calculation formulas for financial ratios.
    
    Returns:
        Dictionary with ratio explanations, formulas, and verification links
    """
    
    explanations = {
        "valuation_ratios": {
            "pe_ratio": {
                "name": "Price-to-Earnings Ratio",
                "formula": "Stock Price ÷ Earnings Per Share (EPS)",
                "explanation": "Shows how much investors are willing to pay for each dollar of earnings. Higher P/E suggests growth expectations or overvaluation.",
                "good_range": "15-25 for most industries, varies by sector",
                "verification_link": "https://www.investopedia.com/terms/p/price-earningsratio.asp"
            },
            "pb_ratio": {
                "name": "Price-to-Book Ratio", 
                "formula": "Stock Price ÷ Book Value Per Share",
                "explanation": "Compares market value to company's book value. Lower P/B may indicate undervaluation or fundamental problems.",
                "good_range": "1.0-3.0 for most companies",
                "verification_link": "https://www.investopedia.com/terms/p/price-to-bookratio.asp"
            },
            "ps_ratio": {
                "name": "Price-to-Sales Ratio",
                "formula": "Market Cap ÷ Total Revenue",
                "explanation": "Useful for companies with no profits yet. Shows how much investors pay for each dollar of sales.",
                "good_range": "1.0-2.0 for mature companies, higher for growth",
                "verification_link": "https://www.investopedia.com/terms/p/price-to-salesratio.asp"
            }
        },
        "profitability_ratios": {
            "roe": {
                "name": "Return on Equity",
                "formula": "Net Income ÷ Shareholders' Equity",
                "explanation": "Measures how efficiently a company uses shareholders' money to generate profits. Higher is generally better.",
                "good_range": "15-20% is excellent, >10% is good",
                "verification_link": "https://www.investopedia.com/terms/r/returnonequity.asp"
            },
            "roa": {
                "name": "Return on Assets",
                "formula": "Net Income ÷ Total Assets", 
                "explanation": "Shows how efficiently a company uses its assets to generate profit. Industry-dependent metric.",
                "good_range": "5-10% is good for most industries",
                "verification_link": "https://www.investopedia.com/terms/r/returnonassets.asp"
            },
            "gross_margin": {
                "name": "Gross Profit Margin",
                "formula": "(Revenue - Cost of Goods Sold) ÷ Revenue × 100",
                "explanation": "Shows percentage of revenue retained after direct costs. Higher margins indicate pricing power.",
                "good_range": "Varies widely by industry (20-80%)",
                "verification_link": "https://www.investopedia.com/terms/g/gross_profit_margin.asp"
            },
            "net_margin": {
                "name": "Net Profit Margin",
                "formula": "Net Income ÷ Revenue × 100",
                "explanation": "Shows what percentage of revenue becomes profit after all expenses. Key profitability measure.",
                "good_range": "5-10% is good, >15% is excellent",
                "verification_link": "https://www.investopedia.com/terms/n/net_margin.asp"
            }
        },
        "liquidity_ratios": {
            "current_ratio": {
                "name": "Current Ratio",
                "formula": "Current Assets ÷ Current Liabilities",
                "explanation": "Measures ability to pay short-term debts. Too high may indicate inefficient cash use.",
                "good_range": "1.5-3.0 is healthy for most companies",
                "verification_link": "https://www.investopedia.com/terms/c/currentratio.asp"
            },
            "quick_ratio": {
                "name": "Quick Ratio (Acid Test)",
                "formula": "(Current Assets - Inventory) ÷ Current Liabilities",
                "explanation": "More conservative liquidity measure excluding inventory. Shows immediate debt-paying ability.",
                "good_range": "1.0 or higher is good",
                "verification_link": "https://www.investopedia.com/terms/q/quickratio.asp"
            }
        },
        "leverage_ratios": {
            "debt_to_equity": {
                "name": "Debt-to-Equity Ratio",
                "formula": "Total Debt ÷ Shareholders' Equity",
                "explanation": "Shows how much debt a company uses relative to equity. Higher ratios indicate more financial risk.",
                "good_range": "<0.5 is conservative, >2.0 is risky",
                "verification_link": "https://www.investopedia.com/terms/d/debtequityratio.asp"
            }
        },
        "canadian_context": {
            "note": "For Canadian stocks, also consider currency impacts, commodity exposure, and sector concentration in TSX",
            "verification_sources": [
                "https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/tax-return/completing-a-tax-return/personal-income/line-12700-taxable-capital-gains/capital-gains-losses.html",
                "https://www.tsx.com/",
                "https://www.bankofcanada.ca/"
            ]
        }
    }
    
    return explanations

def _generate_investment_recommendations(report: Dict) -> None:
    """Generate investment recommendations based on comprehensive analysis."""
    
    recommendations = []
    risk_factors = []
    
    # Based on health score
    health_data = report.get("health_score", {})
    if health_data and "health_score" in health_data:
        score = health_data["health_score"]
        
        if score >= 80:
            recommendations.append("✅ POSITIVE: Strong financial health supports long-term investment")
            recommendations.append("💡 Consider for core portfolio holdings")
        elif score >= 70:
            recommendations.append("➡️ NEUTRAL: Solid fundamentals with room for improvement")
            recommendations.append("💡 Suitable for balanced portfolios")
        elif score >= 50:
            recommendations.append("⚠️ CAUTION: Mixed signals require deeper analysis")
            recommendations.append("💡 Consider smaller position sizes if investing")
        else:
            recommendations.append("🚨 NEGATIVE: Poor fundamentals suggest high risk")
            recommendations.append("💡 Only for speculative/turnaround plays")
    
    # Based on valuation metrics
    ratios_data = report.get("detailed_analysis", {}).get("financial_ratios", {})
    if ratios_data:
        valuation = ratios_data.get("valuation_metrics", {})
        pe_ratio = valuation.get("pe_ratio")
        
        if pe_ratio:
            if pe_ratio > 30:
                risk_factors.append("📈 High valuation risk: P/E ratio suggests expensive pricing")
            elif pe_ratio < 10:
                recommendations.append("💰 Potential value opportunity: Low P/E may indicate undervaluation")
    
    # Based on peer comparison
    peer_data = report.get("peer_comparison", {})
    if peer_data and "peer_comparison" in peer_data:
        comparisons = peer_data["peer_comparison"]
        above_avg_count = sum(1 for comp in comparisons.values() 
                             if comp and comp.get("vs_peers") == "Above Average")
        total_metrics = len(comparisons)
        
        if above_avg_count >= total_metrics * 0.7:
            recommendations.append("🏆 Sector leader: Outperforming most peers")
        elif above_avg_count < total_metrics * 0.3:
            risk_factors.append("📉 Sector laggard: Underperforming most peers")
    
    # Canadian market specific
    symbol = report.get("symbol", "")
    if symbol in TSX_MAJOR_STOCKS:
        sector = TSX_MAJOR_STOCKS[symbol]["sector"]
        
        if sector == "Financial Services":
            recommendations.append("🏦 Banking sector: Monitor interest rate environment")
            risk_factors.append("📊 Interest rate sensitivity may affect profitability")
        elif sector == "Energy":
            recommendations.append("⛽ Energy sector: Consider commodity price cycles")
            risk_factors.append("🛢️ Oil price volatility affects revenue")
        elif sector == "Technology":
            recommendations.append("💻 Tech sector: Evaluate growth sustainability")
            risk_factors.append("💱 Currency exposure to USD may affect results")
    
    report["recommendations"] = recommendations
    report["risk_factors"] = risk_factors

def _add_comprehensive_educational_content(report: Dict) -> None:
    """Add comprehensive educational content for learning investors."""
    
    educational_notes = [
        "📚 UNDERSTANDING FINANCIAL RATIOS:",
        "• P/E Ratio: Price-to-Earnings shows how much investors pay per dollar of earnings",
        "• ROE: Return on Equity measures how efficiently a company uses shareholder money",
        "• Current Ratio: Current Assets ÷ Current Liabilities (>1.0 is generally good)",
        "• Debt-to-Equity: Total Debt ÷ Shareholder Equity (lower is generally safer)",
        "",
        "📚 CANADIAN MARKET CONSIDERATIONS:",
        "• TSX trading hours: 9:30 AM - 4:00 PM Eastern Time",
        "• Currency impact: CAD/USD exchange rate affects international comparisons",
        "• Sector concentration: TSX heavily weighted toward financials, energy, materials",
        "• Dividend taxation: Canadian eligible dividends get preferential tax treatment",
        "",
        "📚 INVESTMENT PROCESS EDUCATION:",
        "• Never invest based on ratios alone - consider industry context",
        "• Compare metrics to industry averages, not absolute benchmarks",
        "• Consider economic cycles - some ratios are cyclical",
        "• Review multiple quarters/years to identify trends",
        "",
        "📚 RISK MANAGEMENT:",
        "• Diversify across sectors and company sizes",
        "• Consider position sizing based on risk assessment",
        "• Set stop-losses for risk management",
        "• Regular portfolio review and rebalancing",
        "",
        "⚖️ COMPLIANCE REMINDER:",
        "• This analysis is for educational purposes only",
        "• Not personalized investment advice",
        "• Consider your risk tolerance and investment goals",
        "• Consult with qualified financial advisors for personalized guidance"
    ]
    
    report["educational_notes"] = educational_notes

# Create the Financial Analysis Agent - ADK requires 'root_agent' naming
root_agent = Agent(
    name="financial_analysis_agent",
    model="gemini-2.0-flash",
    description="Comprehensive financial analysis specialist for Canadian stocks with accurate data integration and educational insights",
    instruction="""You are an expert financial analyst specializing in Canadian stocks and TSX-listed companies. Your core capabilities include:

ACCURATE FINANCIAL RATIO CALCULATION:
- Fetch comprehensive ratio data from Financial Modeling Prep API and Yahoo Finance
- Handle Canadian stock symbol formats correctly (.TO vs .TRT)
- Calculate profitability, liquidity, leverage, valuation, and efficiency ratios
- Provide robust error handling and data validation

EDUCATIONAL FINANCIAL ANALYSIS:
- Explain what each ratio means in practical terms for investors
- Provide context on good vs. poor ratio values for different industries
- Compare companies to sector peers and industry averages
- Calculate comprehensive financial health scores with detailed explanations

CANADIAN MARKET EXPERTISE:
- Understand TSX market structure and major Canadian companies
- Provide sector-specific insights (banking, energy, technology, materials)
- Consider Canadian economic factors (BoC rates, commodity prices, currency)
- Include compliance and tax considerations for Canadian investors

COMPREHENSIVE REPORTING:
- Generate detailed financial analysis reports with executive summaries
- Provide investment recommendations based on quantitative analysis
- Include risk factors and educational content for learning investors
- Maintain high data quality standards with transparent error reporting

INVESTMENT EDUCATION FOCUS:
- Always explain the 'why' behind financial metrics and recommendations
- Provide beginner-friendly explanations with practical examples
- Include warnings about investment risks and the importance of diversification
- Emphasize that analysis is educational, not personalized investment advice

Always prioritize data accuracy, provide multiple data source validation, and maintain an educational tone that helps users understand both the numbers and the reasoning behind financial analysis.""",
    tools=[
        calculate_financial_ratios,
        perform_peer_comparison, 
        analyze_financial_health_score,
        generate_comprehensive_report,
        normalize_canadian_symbol,
        get_ratio_explanations
    ]
)

if __name__ == "__main__":
    print("🍁 MapleTrade Financial Analysis Agent initialized!")
    print("🔧 Available tools:")
    print("   - calculate_financial_ratios(): Comprehensive ratio analysis with FMP + Yahoo Finance")
    print("   - perform_peer_comparison(): Compare stock to sector peers")
    print("   - analyze_financial_health_score(): Calculate financial health score (0-100)")
    print("   - generate_comprehensive_report(): Full analysis report with recommendations")
    print("   - normalize_canadian_symbol(): Convert between .TO and .TRT formats")
    print(f"\n🔑 FMP API Status: {'✅ Configured' if FMP_API_KEY != 'demo' else '⚠️ Using demo key'}")
    print("💡 Example usage:")
    print("   - calculate_financial_ratios('SHOP.TO')")
    print("   - generate_comprehensive_report('TD.TO')")
    print("   - perform_peer_comparison('RY.TO', 'Financial Services')")