import json
import re

from app.services.llm import OllamaClient


SCHEMA = """
Table: tickets

Columns:

ticket_id TEXT
created_at TEXT
category TEXT
priority TEXT
status TEXT
response_time_hrs REAL
resolution_time_hrs REAL
agent_id TEXT
customer_rating REAL
issue_summary TEXT
"""


SYSTEM_PROMPT = f"""
You are a SQL generation engine for a customer support analytics system.

Your ONLY task is to convert a user's natural-language question
into ONE safe SQLite SELECT query.

DATABASE SCHEMA:

{SCHEMA}

EXACT DATA VALUES:

category:
- General
- Billing
- Technical

priority:
- Low
- Medium
- High
- Critical

status:
- Open
- Escalated
- Resolved

IMPORTANT SEMANTICS:

- "unresolved" means status != 'Resolved'
- "resolved" means status = 'Resolved'
- "open" means status = 'Open'
- "escalated" means status = 'Escalated'
- Open and Escalated tickets are unresolved
- "unresolved" does NOT mean "open"
- If the user explicitly says "open", use status = 'Open'
- If the user explicitly says "escalated", use status = 'Escalated'
- If the user explicitly says "unresolved", use status != 'Resolved'
- NULL resolution_time_hrs means no recorded resolution time
- NULL customer_rating means no recorded rating

- "unresolved" means status != 'Resolved'
- "resolved" means status = 'Resolved'
- Open and Escalated tickets are unresolved
- NULL resolution_time_hrs means no recorded resolution time
- NULL customer_rating means no recorded rating

STRICT RULES:

1. Only use filters explicitly requested or logically required
   by the user's question.

2. NEVER add an arbitrary category, priority, status,
   agent, or other filter that the user did not mention.

3. Do NOT assume a category from the wording of the question.

4. Do NOT invent data.

5. Do NOT invent columns.

6. Generate SQLite-compatible SQL.

7. Only generate SELECT or WITH queries.

8. Never generate:
   INSERT
   UPDATE
   DELETE
   DROP
   ALTER
   CREATE
   ATTACH
   DETACH
   PRAGMA

9. If the user asks for an average rating, ignore NULL ratings.

10. If the user asks for average resolution time,
    ignore NULL resolution times.

11. If the user asks about "unresolved" tickets,
    use status != 'Resolved'.

12. If the question does not specify a filter,
    do not create one.

13. Return ONLY valid JSON.

14. Do not use markdown code fences.

JSON FORMAT:

{{
    "sql": "SELECT ...",
    "description": "Short description of what the query calculates."
}}

EXAMPLES:
Question:
How many high priority tickets are open?

Correct:
{{
    "sql": "SELECT COUNT(*) AS count FROM tickets WHERE priority = 'High' AND status = 'Open'",
    "description": "Counts high-priority tickets that are currently open."
}}

Question:
How many high priority tickets are unresolved?

Correct:
{{
    "sql": "SELECT COUNT(*) AS count FROM tickets WHERE priority = 'High' AND status != 'Resolved'",
    "description": "Counts high-priority tickets that are not resolved."
}}

Question:
How many critical tickets are unresolved?

Correct:
{{
    "sql": "SELECT COUNT(*) AS count FROM tickets WHERE priority = 'Critical' AND status != 'Resolved'",
    "description": "Counts unresolved critical tickets."
}}

Question:
How many technical tickets are unresolved?

Correct:
{{
    "sql": "SELECT COUNT(*) AS count FROM tickets WHERE category = 'Technical' AND status != 'Resolved'",
    "description": "Counts unresolved technical tickets."
}}

Question:
How many tickets are there?

Correct:
{{
    "sql": "SELECT COUNT(*) AS count FROM tickets",
    "description": "Counts all tickets."
}}

Question:
Which agent has the lowest average customer rating?

Correct:
{{
    "sql": "SELECT agent_id, AVG(customer_rating) AS average_rating FROM tickets WHERE customer_rating IS NOT NULL GROUP BY agent_id ORDER BY average_rating ASC LIMIT 1",
    "description": "Finds the agent with the lowest average recorded customer rating."
}}

Question:
What is the average resolution time?

Correct:
{{
    "sql": "SELECT AVG(resolution_time_hrs) AS average_resolution_time_hrs FROM tickets WHERE resolution_time_hrs IS NOT NULL",
    "description": "Calculates the average recorded resolution time."
}}
"""


def extract_json(text: str) -> dict:
    """
    Extract JSON from the LLM response.
    Handles accidental markdown fences or extra text.
    """

    text = text.strip()

    # Remove markdown code fences
    text = re.sub(r"```json", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```", "", text)

    text = text.strip()

    # Find the JSON object if the model added extra text
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)

    if not match:
        raise ValueError(
            f"Could not find JSON in LLM response:\n{text}"
        )

    json_text = match.group(0)

    try:
        return json.loads(json_text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON returned by LLM:\n{text}"
        ) from exc


class SQLGenerator:

    def __init__(self):
        self.client = OllamaClient()

    def generate(self, question: str) -> dict:

        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        prompt = f"""
{SYSTEM_PROMPT}

USER QUESTION:
{question}

Return ONLY the JSON object.
"""

        response = self.client.generate(
            prompt,
            temperature=0.0,
        )

        result = extract_json(response)

        if "sql" not in result:
            raise ValueError("LLM response does not contain 'sql'.")

        if "description" not in result:
            result["description"] = "Generated SQL query."

        return result