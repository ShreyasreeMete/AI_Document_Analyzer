"""AI Document Analyzer - Streamlit front end."""
import json

import pandas as pd
import streamlit as st

from src.analyzer import DocumentAnalyzer
from src.chunking import chunk_document
from src.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    GROQ_API_KEY,
    GROQ_MODEL,
    EMBEDDING_MODEL,
    SUPPORTED_TYPES,
)
from src.llm import GroqLLM
from src.loaders import load_document
from src.vector_store import Embedder, VectorStore

st.set_page_config(page_title="AI Document Analyzer", page_icon="📄", layout="wide")


@st.cache_resource(show_spinner="Loading embedding model (first run downloads ~90 MB)...")
def get_embedder() -> Embedder:
    return Embedder(EMBEDDING_MODEL)


def ss(key, default=None):
    return st.session_state.get(key, default)


def run(label: str, fn):
    """Run an LLM call with a spinner and friendly error handling."""
    try:
        with st.spinner(label):
            return fn()
    except Exception as e:  # noqa: BLE001
        st.error(f"Something went wrong: {e}")
        return None


# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.title("📄 AI Document Analyzer")
    api_key = GROQ_API_KEY
    model = GROQ_MODEL
    st.divider()
    uploaded = st.file_uploader("📤 Upload document", type=SUPPORTED_TYPES)
    process = st.button("Process document", type="primary", use_container_width=True,
                        disabled=uploaded is None)
    st.caption("Pipeline: extract → chunk → embed → ChromaDB → RAG → Groq")

if process and uploaded:
    if not api_key:
        st.sidebar.error("Enter your Groq API key first.")
    else:
        try:
            with st.spinner("Extracting, chunking and embedding..."):
                if ss("store"):
                    st.session_state.store.reset()
                doc = load_document(uploaded.name, uploaded.getvalue())
                chunks = chunk_document(doc, CHUNK_SIZE, CHUNK_OVERLAP)
                store = VectorStore(get_embedder())
                store.add(chunks)
            for k in ("results", "chat", "quiz_state"):
                st.session_state.pop(k, None)
            st.session_state.update(doc=doc, store=store, n_chunks=len(chunks))
        except Exception as e:  # noqa: BLE001
            st.sidebar.error(str(e))

# ------------------------------------------------------------------ main
if not ss("store"):
    st.header("Upload a document to get started")
    st.write("Supports **PDF, DOCX, TXT and CSV**. Then summarize it, ask questions, "
             "extract keywords and structured data, generate a quiz or a full report.")
    st.info("Example: upload a resume and ask *“What are the candidate's strongest technical skills?”*")
    st.stop()

doc, store = st.session_state.doc, st.session_state.store
st.subheader(f"📎 {doc.name}")
c1, c2, c3 = st.columns(3)
c1.metric("Characters", f"{len(doc.full_text):,}")
c2.metric("Chunks indexed", st.session_state.n_chunks)
c3.metric("File type", doc.file_type.upper())

if not api_key:
    st.warning("Enter your Groq API key in the sidebar to use the AI features.")
    st.stop()

analyzer = DocumentAnalyzer(store, GroqLLM(api_key, model), doc.name)
results = st.session_state.setdefault("results", {})

tabs = st.tabs(["📝 Summarize", "🔍 Ask Questions", "🔑 Keywords", "📌 Key Points",
                "📊 Structured Data", "🧠 Quiz", "📋 Report"])

# --- Summarize
with tabs[0]:
    style = st.selectbox("Style", ["concise paragraph", "bullet points", "executive summary",
                                   "explain simply (ELI5)"])
    if st.button("Summarize", key="b_sum"):
        out = run("Summarizing...", lambda: analyzer.summarize(style))
        if out:
            results["summary"] = out
    if "summary" in results:
        st.markdown(results["summary"])

# --- Ask questions
with tabs[1]:
    chat = st.session_state.setdefault("chat", [])
    for m in chat:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            if m.get("sources"):
                with st.expander("Sources"):
                    for s in m["sources"]:
                        st.caption(f"{s['location']} · similarity {s['score']:.2f}")
                        st.text(s["text"][:400] + ("..." if len(s["text"]) > 400 else ""))
    question = st.chat_input("Ask something about the document")
    if question:
        history = [{"role": m["role"], "content": m["content"]} for m in chat]
        chat.append({"role": "user", "content": question})
        res = run("Searching and thinking...", lambda: analyzer.ask(question, history))
        if res:
            answer, hits = res
            chat.append({"role": "assistant", "content": answer, "sources": hits})
        st.rerun()

# --- Keywords
with tabs[2]:
    if st.button("Extract keywords", key="b_kw"):
        out = run("Extracting keywords...", analyzer.keywords)
        if out:
            results["keywords"] = out
    if "keywords" in results:
        st.markdown(" ".join(f"`{k}`" for k in results["keywords"]))

# --- Important points
with tabs[3]:
    if st.button("Extract important points", key="b_pts"):
        out = run("Extracting points...", analyzer.important_points)
        if out:
            results["points"] = out
    if "points" in results:
        st.markdown(results["points"])

# --- Structured data
with tabs[4]:
    if st.button("Extract structured data", key="b_struct"):
        out = run("Extracting structured data...", analyzer.structured_data)
        if out:
            results["structured"] = out
    if "structured" in results:
        st.json(results["structured"])
        st.download_button("Download JSON", json.dumps(results["structured"], indent=2),
                           "structured_data.json", "application/json")
    if doc.dataframe is not None:
        st.markdown("**CSV preview**")
        st.dataframe(doc.dataframe.head(100), use_container_width=True)

# --- Quiz
with tabs[5]:
    n_q = st.slider("Number of questions", 3, 10, 5)
    if st.button("Generate quiz", key="b_quiz"):
        out = run("Writing quiz...", lambda: analyzer.quiz(n_q))
        if out:
            results["quiz"] = out
        elif out is not None:
            st.error("No valid questions were produced. Try again.")
    for i, q in enumerate(results.get("quiz", [])):
        st.markdown(f"**Q{i + 1}. {q['question']}**")
        choice = st.radio("Your answer", q["options"], index=None, key=f"q_{i}",
                          label_visibility="collapsed")
        if choice is not None:
            if q["options"].index(choice) == q["answer_index"]:
                st.success("Correct! " + q.get("explanation", ""))
            else:
                st.error(f"Not quite. Answer: {q['options'][q['answer_index']]}. "
                         + q.get("explanation", ""))

# --- Report
with tabs[6]:
    st.caption("Runs summary, keywords, key points and structured extraction, then writes the report.")
    if st.button("Generate report", key="b_report"):
        def build():
            results["summary"] = results.get("summary") or analyzer.summarize()
            results["keywords"] = results.get("keywords") or analyzer.keywords()
            results["points"] = results.get("points") or analyzer.important_points()
            results["structured"] = results.get("structured") or analyzer.structured_data()
            return analyzer.report(results["summary"], results["keywords"],
                                   results["points"], results["structured"])
        out = run("Building report (4-5 LLM calls)...", build)
        if out:
            results["report"] = out
    if "report" in results:
        st.markdown(results["report"])
        st.download_button("Download report (.md)", results["report"],
                           f"{doc.name.rsplit('.', 1)[0]}_report.md", "text/markdown")
