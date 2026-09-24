# DOTMappers AI Support Analytics

An AI-powered customer support analytics system that converts natural-language questions into safe SQL queries and detects operational anomalies from support ticket data.

## Architecture

```text
CSV
 ↓
Pandas Validation
 ↓
SQLite
 ├── Qwen 2.5 3B → Natural Language → SQL
 └── Deterministic Anomaly Detection
 ↓
SQL Validator
 ↓
FastAPI REST API
 ↓
Streamlit UI
```

## Features

* Natural-language querying using **Qwen 2.5 3B**
* LLM-generated SQLite queries with SQL safety validation
* Deterministic anomaly detection:

  * High/Critical unresolved tickets older than 24 hours
  * Abnormally long resolution times using the IQR method
* REST API with FastAPI
* Interactive Streamlit dashboard
* Automated tests with Pytest

## Dataset

The provided dataset contains:

* **500 tickets**
* **10 columns**
* **12 agents**
* 3 categories: General, Billing, Technical
* 4 priority levels: Low, Medium, High, Critical
* 3 statuses: Open, Escalated, Resolved

## Example Results

| Metric                  |    Result |
| ----------------------- | --------: |
| Total tickets           |       500 |
| Unresolved tickets      |       173 |
| Critical tickets        |        55 |
| Unresolved critical     |        31 |
| Billing tickets         |       159 |
| High-priority open      |        31 |
| Average resolution time | 19.16 hrs |
| Detected anomalies      |       101 |

Anomalies:

* **80** high/critical unresolved tickets older than 24 hours
* **21** unusually long resolution times

For this historical/static dataset, the latest ticket timestamp is used as the reference point for the 24-hour rule.

## API

Start the backend:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

API documentation:

`http://127.0.0.1:8001/docs`

Main endpoints:

```text
GET  /health
GET  /summary
POST /query
GET  /anomalies
```

## UI

Start Streamlit:

```powershell
.\.venv\Scripts\python.exe -m streamlit run ui/app.py
```

The UI provides KPI summaries, natural-language querying, generated SQL, and anomaly analysis.

## Setup

Install dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Configure Ollama in `.env`:

```text
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b
```

Ingest the dataset:

```powershell
.\.venv\Scripts\python.exe -m app.ingestion.run_ingestion
```

Run tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Design

The LLM is responsible for **natural-language understanding and SQL generation**. Database access remains constrained by a dedicated SQL validator that permits only read-only queries again
