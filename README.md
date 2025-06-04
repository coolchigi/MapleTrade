# MapleTrade: A Multi-Agent Day Trading Assistant for Canadians

Welcome to **MapleTrade**—an intelligent, agent-driven platform designed to empower Canadian day traders. Built with Google’s Agent Development Kit (ADK), MapleTrade fills a unique gap in Canadian fintech by combining real-time data, explainable AI, and educational insights.

---

## 🇨🇦 Why MapleTrade?

Canadian day traders often lack dedicated tools tailored to our markets, regulations, and learning needs. MapleTrade aims to change that by:

- Focusing on Canadian exchanges (TSX, TSXV)
- Integrating Canadian market news and sentiment
- Educating users with transparent, explainable logic
- Coordinating specialized agents to automate and enhance trading

---

## 🧠 Project Concept

MapleTrade is a **multi-agent trading assistant** that helps you:

1. **Monitor Canadian Stock Markets**: Real-time tracking of TSX/TSXV stocks.
2. **Analyze News & Sentiment**: Summarize financial news and social chatter around Canadian equities.
3. **Implement Trading Strategies**: Backtest and execute popular strategies (momentum, swing, mean-reversion).
4. **Make Trade Decisions**: Suggest or simulate trades with rationale and risk explanations.
5. **Educate & Alert**: Explain decisions, surface learning tips, and notify about compliance issues.

---

## 🏗️ Agent Architecture

MapleTrade leverages ADK to orchestrate several specialized agents:

| Agent                | Responsibilities                                                                 |
|----------------------|---------------------------------------------------------------------------------|
| **Market Data Agent**      | Pulls real-time Canadian market data, detects price/volume anomalies           |
| **News & Sentiment Agent** | Scrapes news and social media, summarizes sentiment using NLP                  |
| **Strategy Agent**         | Runs trading strategies, backtests, and adapts based on performance           |
| **Trade Decision Agent**   | Decides buy/sell actions, interfaces with paper trading APIs                   |
| **Compliance Agent** (opt) | Checks trades for Canadian regulations (PDT, capital gains, TFSA/RRSP, etc.)   |
| **User Agent**             | Provides dashboard, explanations, alerts, and educational guidance            |

---

## ☁️ Google Cloud Integrations

- **ADK**: Orchestrates agent workflows
- **BigQuery**: Stores & analyzes historical trade data
- **Vertex AI**: Trains models for sentiment and strategy optimization
- **Cloud Functions**: Triggers agents based on new data
- **Cloud Run**: Hosts user interface/dashboard

---

## 🚀 Getting Started

> _MapleTrade is in early development. Stay tuned for install instructions, agent demos, and a dashboard preview!_

### Prerequisites

- Google Cloud account (for ADK and cloud integrations)
- API keys for market data/news (TBD)
- Python 3.9+ (project baseline)

### Setup

```bash
# Clone the repo
git clone https://github.com/coolchigi/MapleTrade.git
cd MapleTrade

# (Coming soon) Install dependencies and set up agents
```

---

## 📣 Roadmap

- [ ] Build Market Data Agent for TSX/TSXV
- [ ] Integrate News & Sentiment Agent (Reddit, StockTwits, News APIs)
- [ ] Implement Strategy & Trade Decision Agents (paper trading)
- [ ] Add Compliance logic for Canadian rules
- [ ] Develop User Dashboard and alerts
- [ ] Connect to Google Cloud for storage and model training

---

## 🤝 Contributing

Canadian fintech is better together! If you want to contribute or have ideas, open an issue or pull request.

---

## 📚 License

MIT License

---

### 👋 About

MapleTrade was started to help Canadian day traders learn, experiment, and thrive with the latest in AI and cloud technology.
