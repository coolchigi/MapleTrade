"""
MapleTrade Compliance Agent
Canadian trading regulations, tax implications, and risk compliance
"""

from datetime import datetime, timedelta
from typing import List
import os
from dotenv import load_dotenv
from google.adk.agents import Agent

# Load environment variables
load_dotenv()

# Canadian trading and tax constants (2025 - CRA Official)
# Sources: 
# TFSA: https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/tax-free-savings-account/contributions.html
# RRSP: https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/rrsps-related-plans/contributing-a-rrsp-prpp/contributions-affect-your-rrsp-prpp-deduction-limit.html

TFSA_ANNUAL_LIMIT_2025 = 7000  # CRA confirmed: $7,000 for 2025
TFSA_CUMULATIVE_MAX_2025 = 102000  # For those born 1991 or earlier
RRSP_ANNUAL_LIMIT_2025 = 32490  # CRA: $32,490 for 2025
RRSP_CONTRIBUTION_RATE = 0.18  # 18% of previous year earned income (up to limit)

def check_tfsa_trading_rules(weekly_trades: int, avg_holding_days: int, uses_margin: bool) -> str:
    """
    Check if trading activity is suitable for TFSA account.
    
    Args:
        weekly_trades: Number of trades per week
        avg_holding_days: Average days positions are held
        uses_margin: Whether margin/leverage is used
        
    Returns:
        String with TFSA suitability analysis and warnings
    """
    warnings = []
    recommendations = []
    
    # Check for business income risk
    if weekly_trades >= 4:
        warnings.append("⚠️ Frequent trading (4+ per week) may be considered 'business income' by CRA")
        recommendations.append("💡 Consider using taxable account for frequent day trading")
    
    if avg_holding_days < 7:
        warnings.append("⚠️ Very short holding periods increase business income risk")
        recommendations.append("💡 Longer holding periods support capital gains treatment")
    
    if uses_margin:
        warnings.append("❌ Margin/leverage trading not allowed in TFSA accounts")
        recommendations.append("💡 Use margin account or taxable account for leveraged trading")
    
    # Educational piece..although it may make sense to use the agent
    educational_notes = [
        "📚 TFSA losses permanently reduce contribution room",
        "📚 CRA may tax all TFSA gains if deemed 'carrying on a business'",
        "📚 Over-contributions subject to 1% monthly penalty",
        f"📚 Current TFSA annual limit 2025: ${TFSA_ANNUAL_LIMIT_2025:,} (CRA confirmed)",
        f"📚 Maximum cumulative TFSA room: ${TFSA_CUMULATIVE_MAX_2025:,} (born 1991 or earlier)",
        "📚 Check your personal TFSA room: https://www.canada.ca/en/revenue-agency/services/e-services/e-services-individuals/account-individuals.html"
    ]
    
    # Build response
    result = f"🏛️ TFSA TRADING SUITABILITY ANALYSIS\n\n"
    
    if not warnings:
        result += "✅ SUITABLE: Your trading pattern appears appropriate for TFSA\n\n"
    else:
        result += "⚠️ REVIEW REQUIRED: Potential compliance issues identified\n\n"
        
    if warnings:
        result += "🚨 WARNINGS:\n"
        for warning in warnings:
            result += f"  {warning}\n"
        result += "\n"
    
    if recommendations:
        result += "💡 RECOMMENDATIONS:\n"
        for rec in recommendations:
            result += f"  {rec}\n"
        result += "\n"
    
    result += "📚 EDUCATIONAL NOTES:\n"
    for note in educational_notes:
        result += f"  {note}\n"
    
    return result

def calculate_capital_gains_tax(profit_amount: float, province: str = "ON") -> str:
    """
    Calculate estimated tax on capital gains for Canadian traders.
    
    Args:
        profit_amount: Capital gain amount in CAD
        province: Canadian province code (ON, BC, AB, QC)
        
    Returns:
        String with tax calculation and explanation
    """
    if profit_amount <= 0:
        return f"📊 CAPITAL LOSS ANALYSIS\n\nLoss Amount: ${abs(profit_amount):,.2f}\n\n✅ Capital losses can offset future capital gains\n📚 Losses can be carried back 3 years or forward indefinitely\n💡 Keep detailed records for tax filing"
    
    # Simplified provincial tax rates (combined federal + provincial)
    tax_rates = {
        "ON": 0.45,  # Ontario combined rate estimate
        "BC": 0.47,  # BC combined rate estimate  
        "AB": 0.42,  # Alberta combined rate estimate
        "QC": 0.49   # Quebec combined rate estimate
    }
    
    combined_rate = tax_rates.get(province.upper(), 0.45)
    
    # Capital gains calculation (50% inclusion rate)
    taxable_amount = profit_amount * 0.5
    estimated_tax = taxable_amount * combined_rate
    after_tax_profit = profit_amount - estimated_tax
    
    result = f"💰 CAPITAL GAINS TAX CALCULATION ({province.upper()})\n\n"
    result += f"Gross Capital Gain: ${profit_amount:,.2f}\n"
    result += f"Taxable Amount (50%): ${taxable_amount:,.2f}\n"
    result += f"Estimated Tax: ${estimated_tax:,.2f}\n"
    result += f"After-Tax Profit: ${after_tax_profit:,.2f}\n\n"
    
    result += "📚 EXPLANATION:\n"
    result += "  • Only 50% of capital gains are taxable in Canada\n"
    result += "  • Tax rate depends on your total income bracket\n"
    result += "  • This is an estimate - consult tax professional for accuracy\n\n"
    
    result += "💡 TAX PLANNING TIPS:\n"
    result += "  • Consider tax-loss harvesting to offset gains\n"
    result += "  • Timing of sales can affect which tax year applies\n"
    result += "  • Keep detailed records of all transactions\n"
    
    return result

def assess_margin_trading_compliance(account_equity: float, position_size: float) -> str:
    """
    Assess compliance requirements for margin trading in Canada.
    
    Args:
        account_equity: Current account equity in CAD
        position_size: Planned position size in CAD
        
    Returns:
        String with margin trading compliance analysis
    """
    MIN_EQUITY = 2000  # IIROC minimum
    MAINTENANCE_MARGIN = 0.25  # 25% maintenance requirement
    
    result = f"📊 MARGIN TRADING COMPLIANCE CHECK\n\n"
    result += f"Account Equity: ${account_equity:,.2f}\n"
    result += f"Position Size: ${position_size:,.2f}\n\n"
    
    # Check minimum equity requirement
    if account_equity < MIN_EQUITY:
        result += f"❌ COMPLIANCE ISSUE: Minimum equity required: ${MIN_EQUITY:,}\n"
        result += f"   Current shortfall: ${MIN_EQUITY - account_equity:,.2f}\n\n"
        return result
    
    # Calculate buying power and requirements
    max_position = account_equity * 2  # 2:1 leverage for regular margin
    required_margin = position_size * 0.5  # 50% initial margin
    maintenance_requirement = position_size * MAINTENANCE_MARGIN
    
    result += "✅ MARGIN REQUIREMENTS:\n"
    result += f"  • Maximum position size: ${max_position:,.2f} (2:1 leverage)\n"
    result += f"  • Required initial margin: ${required_margin:,.2f}\n"
    result += f"  • Maintenance requirement: ${maintenance_requirement:,.2f}\n\n"
    
    if position_size > max_position:
        result += f"⚠️ WARNING: Position exceeds maximum allowed\n"
        result += f"   Reduce position by: ${position_size - max_position:,.2f}\n\n"
    
    # Risk warnings
    result += "⚠️ MARGIN TRADING RISKS:\n"
    result += "  • Interest charges on borrowed funds\n"
    result += "  • Margin calls if equity falls below maintenance\n"
    result += "  • Forced liquidation during market volatility\n"
    result += "  • Amplified losses in declining markets\n\n"
    
    result += "💡 RISK MANAGEMENT:\n"
    result += "  • Set stop-loss orders to limit downside\n"
    result += "  • Monitor account equity daily\n"
    result += "  • Keep cash reserves for margin calls\n"
    result += "  • Understand margin interest costs\n"
    
    return result

def get_canadian_trading_regulations() -> str:
    """
    Get overview of current Canadian trading regulations and important dates.
    
    Returns:
        String with comprehensive regulatory information
    """
    current_year = datetime.now().year
    
    result = f"🏛️ CANADIAN TRADING REGULATIONS {current_year}\n\n"
    
    # Account type rules
    result += "📋 ACCOUNT TYPE REGULATIONS:\n\n"
    
    result += "🔹 TFSA (Tax-Free Savings Account):\n"
    result += f"  • Annual limit 2025: ${TFSA_ANNUAL_LIMIT_2025:,} (CRA confirmed)\n"
    result += f"  • Maximum cumulative: ${TFSA_CUMULATIVE_MAX_2025:,} (born 1991 or earlier)\n"
    result += "  • No margin/leverage allowed\n"
    result += "  • Frequent trading may trigger business income tax\n"
    result += "  • Source: https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/tax-free-savings-account/contributions.html\n\n"
    
    result += "🔹 RRSP (Registered Retirement Savings Plan):\n"
    result += f"  • Annual limit 2025: ${RRSP_ANNUAL_LIMIT_2025:,} (18% of 2024 earned income)\n"
    result += "  • Contribution rate: 18% of previous year earned income\n"
    result += "  • Qualified investments only\n"
    result += "  • No margin/leverage allowed\n"
    result += "  • Source: https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/rrsps-related-plans/contributing-a-rrsp-prpp/contributions-affect-your-rrsp-prpp-deduction-limit.html\n\n"
    
    result += "🔹 Margin Accounts:\n"
    result += "  • Minimum equity: $2,000 (IIROC requirement)\n"
    result += "  • Maximum leverage: 2:1 for most stocks\n"
    result += "  • Maintenance margin: 25% minimum\n"
    result += "  • Interest charges on borrowed funds\n\n"
    
    # Trading rules
    result += "⚖️ TRADING REGULATIONS:\n"
    result += "  • Settlement period: T+2 (trade date + 2 business days)\n"
    result += "  • Pattern day trader rules apply\n"
    result += "  • IIROC oversight of all Canadian brokers\n"
    result += "  • Currency conversion fees on US stocks\n\n"
    
    # Tax implications
    result += "💰 TAX TREATMENT:\n"
    result += "  • Capital gains: 50% inclusion rate\n"
    result += "  • Business income: 100% taxable if day trading\n"
    result += "  • Provincial tax rates vary significantly\n"
    result += "  • Detailed record-keeping required\n\n"
    
    # Important dates
    result += f"📅 IMPORTANT DATES {current_year}:\n"
    result += "  • Tax filing deadline: April 30\n"
    result += "  • RRSP contribution deadline: 60 days after year-end\n"
    result += "  • T5 slips available: End of February\n"
    result += "  • Quarterly installments: March 15, June 15, Sept 15, Dec 15\n\n"
    
    result += "📚 COMPLIANCE RESOURCES:\n"
    result += "  • CRA Guide T4037: Capital Gains\n"
    result += "  • CRA TFSA Guide: https://www.canada.ca/en/revenue-agency/services/forms-publications/publications/rc4466/tax-free-savings-account-tfsa-guide-individuals.html\n"
    result += "  • CRA RRSP Guide: https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/rrsps-related-plans.html\n"
    result += "  • IIROC Rules and Guidance: https://www.iiroc.ca/\n"
    result += "  • Provincial securities commissions\n"
    result += "  • Professional tax advice recommended\n"
    
    return result

# Create the Compliance Agent with simpler tools
root_agent = Agent(
    name="compliance_agent",
    model="gemini-2.0-flash",
    description="Canadian trading compliance, tax implications, and regulatory guidance specialist",
    instruction="""You are a Canadian trading compliance specialist. Help traders understand:

• TFSA/RRSP trading rules and business income risks
• Capital gains tax calculations and planning
• Margin trading compliance and requirements  
• Current Canadian trading regulations and deadlines

Always provide specific Canadian context, explain WHY rules exist, and warn about compliance risks. Use clear examples and suggest professional consultation for complex situations.""",
    tools=[check_tfsa_trading_rules, calculate_capital_gains_tax, assess_margin_trading_compliance, get_canadian_trading_regulations]
)

if __name__ == "__main__":
    print("⚖️ MapleTrade Compliance Agent initialized!")
    print("🔧 Available tools:")
    print("   - check_tfsa_trading_rules(): Analyze TFSA trading suitability")
    print("   - calculate_capital_gains_tax(): Estimate tax on capital gains")
    print("   - assess_margin_trading_compliance(): Check margin requirements")
    print("   - get_canadian_trading_regulations(): Current regulations overview")
    print(f"\n✅ Root agent available: {root_agent.name}")