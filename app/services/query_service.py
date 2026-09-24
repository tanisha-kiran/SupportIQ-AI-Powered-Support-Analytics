from app.services.sql_generator import SQLGenerator
from app.services.sql_validator import validate_sql
from app.services.query_engine import execute_query


class QueryService:

    def __init__(self):
        self.sql_generator = SQLGenerator()

    def answer(self, question: str) -> dict:
        """
        Convert a natural-language question into SQL,
        validate it, execute it against SQLite,
        and return the result.
        """

        # 1. Generate SQL using the LLM
        generated = self.sql_generator.generate(question)

        raw_sql = generated["sql"]
        description = generated.get(
            "description",
            "Generated SQL query."
        )

        # 2. Validate the generated SQL
        sql = validate_sql(raw_sql)

        # 3. Execute against SQLite
        rows = execute_query(sql)

        # 4. Return everything needed by the API/UI
        return {
            "question": question,
            "sql": sql,
            "description": description,
            "results": rows,
        }