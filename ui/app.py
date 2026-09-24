import requests
import streamlit as st


API_URL = "http://127.0.0.1:8001"


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="DOTMappers Support Analytics",
    page_icon="📊",
    layout="wide",
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .main {
        padding-top: 1rem;
    }

    .block-container {
        max-width: 1400px;
        padding-top: 2rem;
    }

    .hero {
        padding: 1.5rem 0 1rem 0;
    }

    .hero h1 {
        font-size: 2.3rem;
        margin-bottom: 0.25rem;
    }

    .hero p {
        font-size: 1.05rem;
        opacity: 0.7;
    }

    .section-title {
        font-size: 1.35rem;
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }

    .answer-box {
        padding: 1rem 1.2rem;
        border-radius: 10px;
        border: 1px solid rgba(128, 128, 128, 0.25);
        margin-bottom: 1rem;
    }

    .status-pill {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# API HELPERS
# =========================================================

def get_summary():
    response = requests.get(
        f"{API_URL}/summary",
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def get_anomalies():
    response = requests.get(
        f"{API_URL}/anomalies",
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def ask_question(question: str):
    response = requests.post(
        f"{API_URL}/query",
        json={"question": question},
        timeout=120,
    )
    response.raise_for_status()
    return response.json()


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>DOTMappers Support Analytics</h1>
        <p>
            Ask questions about customer support data using
            natural language.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# CONNECTION STATUS
# =========================================================

try:
    health = requests.get(
        f"{API_URL}/health",
        timeout=5,
    )

    if health.ok:
        st.success("● API connected")
    else:
        st.error("API unavailable")

except requests.RequestException:
    st.error(
        "Cannot connect to FastAPI. "
        "Start the backend before using the dashboard."
    )
    st.stop()


# =========================================================
# LOAD SUMMARY
# =========================================================

try:
    summary = get_summary()

except requests.RequestException as exc:
    st.error(f"Failed to load dashboard data: {exc}")
    st.stop()


# =========================================================
# KPI CARDS
# =========================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Tickets",
        summary.get("total_tickets", 0),
    )

with col2:
    st.metric(
        "Unresolved",
        summary.get("unresolved_tickets", 0),
    )

with col3:
    st.metric(
        "Critical Tickets",
        summary.get("critical_tickets", 0),
    )

with col4:
    st.metric(
        "Critical Unresolved",
        summary.get(
            "unresolved_critical_tickets",
            0,
        ),
    )


st.divider()


# =========================================================
# NATURAL LANGUAGE QUERY
# =========================================================

st.markdown(
    '<div class="section-title">Ask your support data</div>',
    unsafe_allow_html=True,
)

st.caption(
    "The system converts your question into SQL, "
    "validates the query, and executes it against SQLite."
)

question = st.text_input(
    "Natural-language question",
    placeholder="Example: How many critical tickets are unresolved?",
    label_visibility="collapsed",
)


if st.button(
    "Run Analysis",
    type="primary",
    width="stretch",
):

    if not question.strip():

        st.warning(
            "Please enter a question first."
        )

    else:

        with st.spinner(
            "Generating and executing query..."
        ):

            try:

                result = ask_question(
                    question.strip()
                )

                rows = result.get(
                    "results",
                    [],
                )

                st.markdown(
                    '<div class="section-title">Result</div>',
                    unsafe_allow_html=True,
                )

                if rows:

                    # If there is exactly one value,
                    # present it prominently.
                    if (
                        len(rows) == 1
                        and len(rows[0]) == 1
                    ):

                        value = list(
                            rows[0].values()
                        )[0]

                        st.metric(
                            "Answer",
                            (
                                round(value, 2)
                                if isinstance(
                                    value,
                                    float,
                                )
                                else value
                            ),
                        )

                    else:

                        st.dataframe(
                            rows,
                            width="stretch",
                        )

                else:

                    st.info(
                        "The query returned no results."
                    )


                # -------------------------------------------------
                # SQL TRANSPARENCY
                # -------------------------------------------------

                with st.expander(
                    "View generated SQL"
                ):

                    st.code(
                        result.get(
                            "sql",
                            "",
                        ),
                        language="sql",
                    )

                    st.caption(
                        result.get(
                            "description",
                            "Generated database query.",
                        )
                    )


            except requests.HTTPError as exc:

                try:
                    detail = exc.response.json().get(
                        "detail",
                        exc.response.text,
                    )
                except Exception:
                    detail = exc.response.text

                st.error(
                    f"Query failed: {detail}"
                )

            except requests.RequestException as exc:

                st.error(
                    f"Could not reach the API: {exc}"
                )


# =========================================================
# EXAMPLE QUESTIONS
# =========================================================

st.markdown(
    '<div class="section-title">Example questions</div>',
    unsafe_allow_html=True,
)

examples = [
    "How many tickets are there?",
    "How many unresolved tickets are there?",
    "How many critical tickets are unresolved?",
    "How many billing tickets are there?",
    "How many high priority tickets are open?",
    "What is the average resolution time?",
    "Which agent has the lowest average customer rating?",
]

for i in range(0, len(examples), 2):

    cols = st.columns(2)

    for j, col in enumerate(cols):

        index = i + j

        if index < len(examples):

            with col:

                if st.button(
                    examples[index],
                    key=f"example_{index}",
                    width="stretch",
                ):

                    try:

                        result = ask_question(
                            examples[index]
                        )

                        rows = result.get(
                            "results",
                            [],
                        )

                        st.session_state[
                            "example_result"
                        ] = result

                    except requests.RequestException as exc:

                        st.error(
                            f"Query failed: {exc}"
                        )


# =========================================================
# SHOW EXAMPLE RESULT
# =========================================================

if "example_result" in st.session_state:

    result = st.session_state[
        "example_result"
    ]

    st.markdown(
        '<div class="section-title">Example result</div>',
        unsafe_allow_html=True,
    )

    rows = result.get(
        "results",
        [],
    )

    if (
        len(rows) == 1
        and len(rows[0]) == 1
    ):

        value = list(
            rows[0].values()
        )[0]

        st.metric(
            "Answer",
            (
                round(value, 2)
                if isinstance(
                    value,
                    float,
                )
                else value
            ),
        )

    elif rows:

        st.dataframe(
            rows,
            width="stretch",
        )

    with st.expander(
        "View generated SQL"
    ):

        st.code(
            result.get(
                "sql",
                "",
            ),
            language="sql",
        )


st.divider()


# =========================================================
# ANOMALY DETECTION
# =========================================================

st.markdown(
    '<div class="section-title">Anomaly detection</div>',
    unsafe_allow_html=True,
)

st.caption(
    "Deterministic rules identify operational issues "
    "that require attention."
)


try:

    anomaly_data = get_anomalies()

    anomaly_count = anomaly_data.get(
        "count",
        0,
    )

    anomalies = anomaly_data.get(
        "anomalies",
        [],
    )

    if anomaly_count == 0:

        st.success(
            "No anomalies detected."
        )

    else:

        high_count = sum(
            1
            for item in anomalies
            if item.get("severity") == "high"
        )

        critical_count = sum(
            1
            for item in anomalies
            if item.get("severity") == "critical"
        )

        medium_count = sum(
            1
            for item in anomalies
            if item.get("severity") == "medium"
        )

        a, b, c = st.columns(3)

        with a:
            st.metric(
                "Total anomalies",
                anomaly_count,
            )

        with b:
            st.metric(
                "High / Critical",
                high_count + critical_count,
            )

        with c:
            st.metric(
                "Long resolution",
                medium_count,
            )

        st.dataframe(
            anomalies,
            width="stretch",
        )


except requests.RequestException as exc:

    st.error(
        f"Failed to load anomalies: {exc}"
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "DOTMappers AI Assessment • "
    "Qwen 2.5:3B • FastAPI • SQLite"
)