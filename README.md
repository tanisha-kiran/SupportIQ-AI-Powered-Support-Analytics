\# DOTMappers AI Support Analytics



An AI-powered customer support analytics system that allows users to query support ticket data using natural language and automatically detect operational anomalies.



\## Overview



This project ingests a customer support ticket CSV into SQLite and exposes analytics through a REST API and a lightweight Streamlit interface.



The system combines an LLM for natural-language understanding with deterministic database execution and rule-based anomaly detection.



\## Architecture



```text

Customer Support CSV

&#x20;       |

&#x20;       v

Pandas Ingestion

&#x20;       |

&#x20;       v

SQLite Database

&#x20;       |

&#x20;       +----------------------+

&#x20;       |                      |

&#x20;       v                      v

&#x20;Qwen 2.5:3B            Deterministic

&#x20;NL -> SQL              Anomaly Engine

&#x20;       |                      |

&#x20;       v                      |

&#x20;  SQL Validator               |

&#x20;       |                      |

&#x20;       v                      |

&#x20;     SQLite <----------------+

&#x20;       |

&#x20;       v

&#x20;    FastAPI

&#x20;       |

&#x20;       v

&#x20;  Streamlit UI

&#x20;  Key Features

Natural-language querying



Users can ask questions such as:



How many tickets are there?

How many unresolved tickets are there?

How many critical tickets are unresolved?

How many billing tickets are there?

How many high priority tickets are open?

What is the average resolution time?

Which agent has the lowest average customer rating?



Qwen 2.5:3B converts the natural-language request into SQLite-compatible SQL.



The generated query is validated before execution.



SQLite remains the source of truth for numerical results.



SQL safety



The SQL validator:



allows only SELECT and WITH queries

rejects destructive SQL operations

prevents multiple SQL statements

restricts queries to the tickets table

Anomaly detection



The system detects:



High or critical priority tickets that remain unresolved for more than 24 hours.

Abnormally long resolution times using the IQR method.



Because the supplied dataset is historical, the 24-hour rule uses the latest timestamp in the dataset as the reference point rather than the machine's current time.



REST API



FastAPI exposes:



GET  /health

GET  /summary

POST /query

GET  /anomalies



Interactive API documentation is available through FastAPI's Swagger interface.



Dataset



The supplied dataset contains:



500 customer support tickets

10 columns

12 agents

3 categories

4 priority levels

3 ticket statuses



Important data semantics:



Resolved    -> resolved

Open        -> unresolved

Escalated   -> unresolved



A missing resolution\_time\_hrs indicates that no resolution time was recorded.



A missing customer\_rating indicates that no customer rating was recorded.



Example Results



Using the supplied dataset:



Query	Result

Total tickets	500

Unresolved tickets	173

Critical tickets	55

Critical unresolved tickets	31

Billing tickets	159

High-priority open tickets	31

Average resolution time	\~19.16 hours



The anomaly detector currently identifies:



80 old high-priority unresolved tickets

21 abnormally long resolution tickets

101 total anomalies

Project Structure

dotmappers-ai-assessment/

|

├── app/

│   ├── api/

│   │   └── routes.py

│   │

│   ├── core/

│   │   ├── config.py

│   │   └── database.py

│   │

│   ├── ingestion/

│   │   ├── csv\_loader.py

│   │   └── run\_ingestion.py

│   │

│   ├── services/

│   │   ├── anomaly\_detector.py

│   │   ├── llm.py

│   │   ├── query\_engine.py

│   │   ├── query\_service.py

│   │   ├── sql\_generator.py

│   │   └── sql\_validator.py

│   │

│   └── main.py

│

├── data/

│   └── tickets.csv

│

├── tests/

│   ├── test\_llm.py

│   └── test\_services.py

│

├── ui/

│   └── app.py

│

├── .env

├── .gitignore

├── README.md

└── requirements.txt

Setup

1\. Clone the repository

git clone <repository-url>

cd dotmappers-ai-assessment

2\. Create a virtual environment



Windows:



python -m venv .venv

.\\.venv\\Scripts\\Activate.ps1

3\. Install dependencies

python -m pip install -r requirements.txt

4\. Configure environment variables



Create a .env file:



OLLAMA\_BASE\_URL=http://localhost:11434

OLLAMA\_MODEL=qwen2.5:3b



The .env file is intentionally excluded from version control.



5\. Install the local LLM



The application expects the following Ollama model:



qwen2.5:3b



Make sure Ollama is running locally before using natural-language queries.



6\. Ingest the dataset

python -m app.ingestion.run\_ingestion



This creates the SQLite database from:



data/tickets.csv

7\. Start the API

python -m uvicorn app.main:app --host 127.0.0.1 --port 8001

8\. Start the UI



In a second terminal:



python -m streamlit run ui/app.py

Testing



Run the complete test suite:



python -m pytest -v



The test suite covers:



database summary calculations

anomaly detection

anomaly classification

SQL validation

rejection of destructive SQL

rejection of multiple SQL statements

natural-language SQL generation

distinction between open and unresolved tickets

distinction between escalated and open tickets

Design Decisions

Why SQLite?



SQLite provides a lightweight relational source of truth while remaining easy to run locally during an assessment.



Why use an LLM for SQL generation?



The assessment requires natural-language understanding. The LLM translates user questions into structured database queries while SQLite performs the actual computation.



Why deterministic anomaly detection?



Anomaly rules are explicitly defined by the assessment requirements. Deterministic rules provide reproducible and explainable results instead of relying on an LLM to decide whether a ticket is anomalous.



Why validate generated SQL?



LLM-generated code should not be executed blindly. The validator provides a safety boundary between the model and the database.



Limitations



This implementation is designed for the supplied assessment dataset and a local development environment.



Potential production extensions include:



read-only database credentials

a full SQL parser instead of regex-based validation

query timeouts

authentication and authorization

structured logging

model monitoring

persistent audit logs

containerized deployment

larger-scale analytical storage

Technologies

Python

Pandas

SQLite

SQLAlchemy

Qwen 2.5:3B

Ollama

FastAPI

Streamlit

Pytest





