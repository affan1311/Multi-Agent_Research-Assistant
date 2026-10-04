from __future__ import annotations

import time
from typing import Any

import streamlit as st

from src.agents.agents import (
    build_scrape_agent,
    build_search_agent,
    critic_chain,
    writer_chain,
)


st.set_page_config(
    page_title="Researcher | Multi-Agent Research",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --ink: #eaf2ff;
    --muted: #8ea3bf;
    --line: rgba(148, 163, 184, .16);
    --panel: rgba(15, 29, 51, .76);
    --cyan: #5eead4;
    --blue: #60a5fa;
    --violet: #a78bfa;
}

html, body, [class*="css"] { font-family: "Manrope", sans-serif; }
.stApp {
    color: var(--ink);
    background:
        radial-gradient(circle at 8% 0%, rgba(96,165,250,.18), transparent 28rem),
        radial-gradient(circle at 92% 15%, rgba(167,139,250,.15), transparent 25rem),
        #07111f;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { max-width: 1380px; padding: 2rem 3.5rem 4rem; }

[data-testid="stSidebar"] {
    background: rgba(6, 16, 31, .94);
    border-right: 1px solid var(--line);
}
[data-testid="stSidebar"] > div:first-child { padding-top: 2rem; }

.brand { font-family: "DM Mono", monospace; letter-spacing: .16em; text-transform: uppercase;
    font-size: .72rem; color: var(--cyan); }
.hero { padding: 2.5rem 0 1.6rem; }
.hero h1 { font-size: clamp(2.4rem, 5vw, 4.8rem); line-height: 1; letter-spacing: -.06em;
    margin: .5rem 0 1rem; font-weight: 800; }
.hero h1 span { color: var(--cyan); }
.hero p { color: var(--muted); max-width: 700px; font-size: 1.03rem; line-height: 1.7; }
.eyebrow, .section-label { font-family: "DM Mono", monospace; text-transform: uppercase;
    letter-spacing: .14em; font-size: .68rem; color: var(--blue); }
.panel { border: 1px solid var(--line); border-radius: 20px; padding: 1.35rem;
    background: var(--panel); box-shadow: 0 18px 50px rgba(0,0,0,.18); }
.section-title { font-size: 1.15rem; font-weight: 700; margin: .35rem 0 1rem; }
.step { border: 1px solid var(--line); border-radius: 14px; padding: .85rem 1rem;
    margin: .65rem 0; background: rgba(255,255,255,.025); }
.step.active { border-color: rgba(96,165,250,.65); background: rgba(96,165,250,.09); }
.step.done { border-color: rgba(94,234,212,.42); background: rgba(94,234,212,.06); }
.step-row { display: flex; align-items: center; gap: .7rem; }
.step-number { color: var(--cyan); font-family: "DM Mono", monospace; font-size: .75rem; }
.step-name { font-weight: 700; flex: 1; }
.step-state { color: var(--muted); font-family: "DM Mono", monospace; font-size: .65rem; }
.step.done .step-state { color: var(--cyan); }
.metric { padding: 1rem; border: 1px solid var(--line); border-radius: 14px;
    background: rgba(255,255,255,.025); }
.metric-value { font-size: 1.7rem; font-weight: 800; }
.metric-label { color: var(--muted); font-size: .75rem; }
.stTextArea textarea, .stTextInput input {
    background: rgba(255,255,255,.045) !important; border: 1px solid var(--line) !important;
    border-radius: 12px !important; color: var(--ink) !important;
}
.stButton > button, .stDownloadButton > button {
    border: 0 !important; border-radius: 11px !important; font-weight: 700 !important;
    background: linear-gradient(135deg, #2563eb, #7c3aed) !important; color: white !important;
}
.stButton > button:hover, .stDownloadButton > button:hover { filter: brightness(1.15); }
.stTabs [data-baseweb="tab-list"] { gap: .4rem; }
.stTabs [data-baseweb="tab"] { color: var(--muted); }
.stTabs [aria-selected="true"] { color: var(--cyan); }
.hint { color: var(--muted); font-size: .78rem; line-height: 1.5; }
</style>
""",
    unsafe_allow_html=True,
)


def latest_content(response: dict[str, Any]) -> str:
    """Return the text content from the final LangChain message."""
    message = response["messages"][-1]
    content = getattr(message, "content", message)
    if isinstance(content, list):
        return "\n".join(
            block.get("text", str(block)) if isinstance(block, dict) else str(block)
            for block in content
        )
    return str(content)


def render_step(number: str, name: str, description: str, state: str) -> None:
    state_text = {"done": "DONE", "active": "RUNNING", "waiting": "WAITING"}[state]
    st.markdown(
        f"""
        <div class="step {state}">
            <div class="step-row">
                <span class="step-number">{number}</span>
                <span class="step-name">{name}</span>
                <span class="step-state">{state_text}</span>
            </div>
            <div class="hint" style="margin: .4rem 0 0 1.7rem;">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def reset_results() -> None:
    st.session_state.results = {}
    st.session_state.error = ""
    st.session_state.topic_run = ""


if "results" not in st.session_state:
    reset_results()

with st.sidebar:
    st.markdown('<div class="brand">◈ Researcher</div>', unsafe_allow_html=True)
    st.markdown("### Control room")
    st.caption("A focused workspace for search, synthesis, and review.")
    st.divider()
    st.markdown("**Pipeline**")
    st.markdown("`01` Search  ·  `02` Scrape  ·  `03` Write  ·  `04` Critique")
    st.divider()
    st.markdown("**Tips**")
    st.markdown(
        '<p class="hint">Use a specific topic and include a timeframe, audience, or region '
        "when those details matter.</p>",
        unsafe_allow_html=True,
    )
    if st.button("Clear workspace", use_container_width=True):
        reset_results()
        st.rerun()


st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Multi-agent research workspace</div>
        <h1>Turn a question into a <span>clear brief.</span></h1>
        <p>Four coordinated stages gather current sources, extract deeper context,
        write a polished report, and challenge its claims before you read it.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

input_col, pipeline_col = st.columns([1.35, 1], gap="large")

with input_col:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Start a new investigation</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">What should we research?</div>', unsafe_allow_html=True)
    examples = [
        "The impact of artificial intelligence on the job market",
        "How renewable energy is changing global infrastructure",
        "The latest advances in AI agents for software development",
    ]
    selected_example = st.selectbox("Example prompts", ["Write your own"] + examples)
    default_topic = "" if selected_example == "Write your own" else selected_example
    topic = st.text_area(
        "Research topic",
        value=default_topic,
        height=105,
        placeholder="e.g. How will AI affect entry-level software jobs by 2030?",
        label_visibility="collapsed",
    )
    run = st.button("Run research pipeline  →", type="primary", use_container_width=True)
    st.markdown(
        '<p class="hint">The run may take a few minutes because each stage uses a live model '
        "and web search.</p>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

with pipeline_col:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Execution map</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Agent activity</div>', unsafe_allow_html=True)
    current = st.session_state.results
    render_step("01", "Search agent", "Finds recent and relevant sources.", "done" if "search" in current else "waiting")
    render_step("02", "Scrape agent", "Extracts readable source content.", "done" if "scrape" in current else "waiting")
    render_step("03", "Writer chain", "Synthesizes the research into a report.", "done" if "writer" in current else "waiting")
    render_step("04", "Critic chain", "Scores the report and identifies gaps.", "done" if "critic" in current else "waiting")
    st.markdown("</div>", unsafe_allow_html=True)


if run:
    clean_topic = topic.strip()
    if not clean_topic:
        st.warning("Enter a research topic before starting.")
    else:
        st.session_state.results = {}
        st.session_state.error = ""
        st.session_state.topic_run = clean_topic
        results: dict[str, str] = {}
        try:
            with st.status("Running the research pipeline…", expanded=True) as status:
                st.write("🔎 Searching for current sources…")
                search_agent = build_search_agent()
                search_response = search_agent.invoke(
                    {
                        "messages": [
                            (
                                "user",
                                f"Find recent, reliable and detailed information about the topic: "
                                f"{clean_topic}. Summarize key points and include relevant sources.",
                            )
                        ]
                    }
                )
                results["search"] = latest_content(search_response)
                st.session_state.results = dict(results)

                st.write("📄 Extracting deeper content from the best source…")
                scrape_agent = build_scrape_agent()
                scrape_response = scrape_agent.invoke(
                    {
                        "messages": [
                            (
                                "user",
                                f"Based on these search results about '{clean_topic}', pick the "
                                "most relevant URL and scrape it for deeper content.\n\n"
                                f"Search results:\n{results['search'][:2000]}",
                            )
                        ]
                    }
                )
                results["scrape"] = latest_content(scrape_response)
                st.session_state.results = dict(results)

                st.write("✍️ Writing the research brief…")
                results["writer"] = str(
                    writer_chain.invoke(
                        {
                            "topic": clean_topic,
                            "research": (
                                f"Search results:\n{results['search']}\n\n"
                                f"Scraped content:\n{results['scrape']}"
                            ),
                        }
                    )
                )
                st.session_state.results = dict(results)

                st.write("🧭 Reviewing the report for quality…")
                results["critic"] = str(critic_chain.invoke({"report": results["writer"]}))
                st.session_state.results = dict(results)
                status.update(label="Research pipeline complete", state="complete", expanded=False)
        except Exception as exc:
            st.session_state.results = dict(results)
            st.session_state.error = str(exc)
            st.error(
                "The pipeline stopped before completing all stages. "
                "Any completed stage is still available below."
            )


results = st.session_state.results
if results:
    st.divider()
    st.markdown('<div class="section-label">Output workspace</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="section-title">{st.session_state.get("topic_run", "Research results")}</div>',
        unsafe_allow_html=True,
    )
    metrics = st.columns(3)
    metrics[0].metric("Stages complete", f"{len(results)}/4")
    metrics[1].metric("Report words", len(results.get("writer", "").split()))
    metrics[2].metric("Run status", "Complete" if "critic" in results else "Partial")

    tabs = st.tabs(["Final report", "Critique", "Sources & notes"])
    with tabs[0]:
        if "writer" in results:
            st.markdown(results["writer"])
            st.download_button(
                "Download report as Markdown",
                data=results["writer"],
                file_name=f"research_report_{int(time.time())}.md",
                mime="text/markdown",
            )
        else:
            st.info("The writer stage did not complete.")
    with tabs[1]:
        st.markdown(results.get("critic", "Critique is not available yet."))
    with tabs[2]:
        if "search" in results:
            with st.expander("Search agent output", expanded=True):
                st.markdown(results["search"])
        if "scrape" in results:
            with st.expander("Scraped source output", expanded=False):
                st.markdown(results["scrape"])

st.markdown(
    '<p class="hint" style="text-align:center;margin-top:3rem;">Researcher · '
    "Powered by LangChain, Gemini, Tavily, and Streamlit</p>",
    unsafe_allow_html=True,
)
