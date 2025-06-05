#!/bin/bash
# MapleTrade Enhanced Project Setup Script
# This script sets up the project environment, including dependencies, directory structure, and configuration.

set -e  # Exit immediately if a command exits with a non-zero status
set -u  # Treat unset variables as an error

echo "🚀 Starting MapleTrade project setup..."

# Update requirements.txt with FMP integration
echo "📦 Updating requirements.txt..."
if [ -f "requirements.txt" ]; then
    echo "⚠️  requirements.txt already exists. Overwriting..."
fi
cat > requirements.txt << EOF
google-adk>=1.0.0
yfinance>=0.2.18
pandas>=1.5.0
python-dotenv>=1.0.0
requests>=2.31.0
fmp-python>=0.1.4
numpy>=1.24.0
python-dateutil>=2.8.0
EOF
echo "✅ requirements.txt updated."

# Create enhanced project structure
echo "📂 Creating project directory structure..."
PROJECT_DIR="mapletrade"
AGENTS=("data_collection_agent" "financial_analysis_agent" "technical_analysis_agent" "market_intelligence_agent" "coordinator_agent")

for AGENT in "${AGENTS[@]}"; do
    AGENT_DIR="$PROJECT_DIR/$AGENT"
    if [ ! -d "$AGENT_DIR" ]; then
        mkdir -p "$AGENT_DIR"
        touch "$AGENT_DIR/__init__.py"
        echo "  ➕ Created $AGENT_DIR with __init__.py"
    else
        echo "  ⚠️  $AGENT_DIR already exists. Skipping..."
    fi
done
echo "✅ Project structure created."

# Update .env file with FMP API key
echo "🔑 Configuring .env file..."
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists. Overwriting..."
fi
cat > .env << EOF
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=True

# Financial Data APIs
FMP_API_KEY=your-fmp-api-key-here
ENABLE_FMP_PREMIUM=False

# Educational Settings
ENABLE_EXPLANATIONS=True
TSX_UPDATE_INTERVAL_HOURS=1
DETAILED_LOGGING=True

# Canadian Market Settings
DEFAULT_CURRENCY=CAD
TSX_FOCUS=True
INCLUDE_US_COMPARISONS=True
EOF
echo "✅ .env file configured."

# Final message
echo "🎉 Setup complete!"
echo "📝 Next steps:"
echo "   1. Get your FMP API key from https://financialmodelingprep.com/"
echo "   2. Update the .env file with your API key."
echo "   3. Run your project and enjoy!"