# Multi-Agent Research Assistant

An AI-powered research workspace built with Streamlit and LangChain. The app coordinates specialized stages to find current information, extract source content, write a report, and review the result.

## Live demo

**[Open the Multi-Agent Research Assistant](https://multi-agentresearch-assistant-jdxcyqzr9fqkg9wfk4owqz.streamlit.app/)**

## Features

- Search agent for recent web sources using Tavily
- Scrape agent for extracting readable source content
- Writer chain for creating a structured research report
- Critic chain for scoring the report and identifying improvements
- Streamlit dashboard with pipeline status, metrics, tabs, and Markdown download
- Local `.env` and Streamlit Cloud secrets support

## Pipeline

1. **Search** — finds relevant sources and summarizes key points.
2. **Scrape** — selects a relevant URL and extracts deeper content.
3. **Write** — combines the research into a professional report.
4. **Critique** — reviews the report and highlights strengths and gaps.

## Run locally

### Requirements

- Python 3.10 or newer
- A Google Gemini API key
- A Tavily API key

### Installation

```powershell
git clone https://github.com/affan1311/Multi-Agent_Research-Assistant.git
cd Multi-Agent_Research-Assistant
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a local `.env` file in the project root:

```dotenv
GOOGLE_API_KEY="your-google-gemini-api-key"
TAVILY_API_KEY="your-tavily-api-key"
```

Start the Streamlit app:

```powershell
streamlit run app.py
```

The application will be available at `http://localhost:8501`.

## Streamlit Cloud deployment

1. Fork or deploy this repository from GitHub.
2. Set the main file to `app.py`.
3. Open **Manage app → Settings → Secrets**.
4. Add:

```toml
GOOGLE_API_KEY = "your-google-gemini-api-key"
TAVILY_API_KEY = "your-tavily-api-key"
```

5. Save the secrets and reboot the app.

Never commit `.env` or real API keys. A safe template is available at [`.streamlit/secrets.toml.example`](.streamlit/secrets.toml.example).

## Project structure

```text
.
├── app.py
├── main.py
├── requirements.txt
├── src
│   ├── agents
│   │   └── agents.py
│   ├── pipeline
│   │   └── pipeline.py
│   ├── tools
│   │   └── tools.py
│   └── config.py
└── .streamlit
    └── secrets.toml.example
```

## Technology

- Python
- Streamlit
- LangChain
- Google Gemini
- Tavily Search
- BeautifulSoup, Readability, and Trafilatura

## License

This project is provided for learning and experimentation.
