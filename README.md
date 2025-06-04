# MapleTrade: A Multi-Agent Day Trading Assistant for Canadians

Welcome to **MapleTrade**—an intelligent, agent-driven platform designed to empower Canadian day traders. Built with Google’s Agent Development Kit (ADK), MapleTrade fills a unique gap in Canadian fintech by combining real-time data, explainable AI, and educational insights.

<details open>
  <summary><strong>📑 Table of Contents</strong></summary>
  <ol>
    <li><a href="#about">About</a></li>
    <li><a href="#motivation">Motivation</a></li>
    <li><a href="#project-concept">Project Concept</a></li>
    <li><a href="#agent-architecture">Agent Architecture</a></li>
    <li><a href="#google-cloud-integrations">Google Cloud Integrations</a></li>
    <li><a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#setup">Setup</a></li>
      </ul>
    </li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
  </ol>
</details>


## About
**MapleTrade** is a multi-agent trading assistant uniquely tailored for Canadian day traders. It leverages Google’s Agent Development Kit (ADK) and Google Cloud to provide real-time intelligence, actionable trade ideas, and educational support for trading on Canadian markets.


## Motivation
While there are many trading tools globally, Canadian traders face unique challenges: limited local tools, complex tax/compliance laws, and a lack of educational resources. MapleTrade addresses this gap by:

- Focusing on Canadian exchanges (TSX, TSXV)
- Integrating Canadian market news and sentiment
- Providing explainable AI-driven recommendations and education
- Orchestrating specialized agents for automation and insight


## Project Concept

MapleTrade is a **multi-agent trading assistant** that helps you:

1. **Monitor Canadian Stock Markets:** Real-time tracking of TSX/TSXV stocks.
2. **Analyze News & Sentiment:** Summarize financial news and social chatter around Canadian equities.
3. **Implement Trading Strategies:** Backtest and execute popular strategies (momentum, swing, mean-reversion).
4. **Make Trade Decisions:** Suggest or simulate trades with rationales and risk explanations.
5. **Educate & Alert:** Explain decisions, surface learning tips, and notify about compliance issues.


## Agent Architecture

MapleTrade leverages ADK to orchestrate several specialized agents:

| Agent                  | Responsibilities                                                                 |
|------------------------|---------------------------------------------------------------------------------|
| **Market Data Agent**      | Pulls real-time Canadian market data, detects price/volume anomalies           |
| **News & Sentiment Agent** | Scrapes news and social media, summarizes sentiment using NLP                  |
| **Strategy Agent**         | Runs trading strategies, backtests, and adapts based on performance            |
| **Trade Decision Agent**   | Decides buy/sell actions, interfaces with paper trading APIs                   |
| **Compliance Agent** (opt) | Checks trades for Canadian regulations (PDT, capital gains, TFSA/RRSP, etc.)   |
| **User Agent**             | Provides dashboard, explanations, alerts, and educational guidance            |

### Google Cloud Integrations

- **ADK:** Orchestrates agent workflows
- **BigQuery:** Stores & analyzes historical trade data
- **Vertex AI:** Trains models for sentiment and strategy optimization
- **Cloud Functions:** Triggers agents based on new data
- **Cloud Run:** Hosts user interface/dashboard


## Getting Started

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


## Contributing

Canadian fintech is better together! If you want to contribute or have ideas, open an issue or pull request.


## License

MIT License


## Roadmap

- [ ] Build Market Data Agent for TSX/TSXV
- [ ] Integrate News & Sentiment Agent (Reddit, StockTwits, News APIs)
- [ ] Implement Strategy & Trade Decision Agents (paper trading)
- [ ] Add Compliance logic for Canadian rules
- [ ] Develop User Dashboard and alerts
- [ ] Connect to Google Cloud for storage and model training

---

> _MapleTrade was started to help Canadian day traders learn, experiment, and thrive with the latest in AI and cloud technology._
