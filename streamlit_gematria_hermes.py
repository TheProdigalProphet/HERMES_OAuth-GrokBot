import json
import os
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import urljoin

import requests
import streamlit as st

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False

try:
    from gematria_full import GematriaFull
except Exception as exc:
    GematriaFull = None
    GEMATRIA_IMPORT_ERROR = str(exc)
else:
    GEMATRIA_IMPORT_ERROR = None

st.set_page_config(page_title="Hermes Gematria Oracle", layout="wide")

CSS = """
<style>
    .stApp { background-color: #0e0e0e; color: #ddd; }
    .stTextInput > div > div > input { background-color: #1a1a1a; color: white; }
    .stButton>button { background-color: #00796b; color: white; }
    .section-header { color: #00ffcc; font-weight: bold; margin-bottom: 8px; }
    .streamlit-expanderHeader { color: #00ffcc; }
    .stMarkdown p, .stMarkdown div { color: #ddd; }
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)
st.title("🌀 Hermes Gematria Oracle")

DEFAULT_HERMES_URLS = [
    url.strip()
    for url in os.environ.get("HERMES_BASE_URLS", "http://127.0.0.1:8000").split(",")
    if url.strip()
]
if not DEFAULT_HERMES_URLS:
    DEFAULT_HERMES_URLS = ["http://127.0.0.1:8000"]

ROOT_DIR = Path(__file__).resolve().parent
BACKGROUND_DIR = ROOT_DIR / "data" / "background"


def load_local_personas() -> List[Dict[str, Any]]:
    personas: List[Dict[str, Any]] = []
    if not BACKGROUND_DIR.exists():
        return personas
    for path in sorted(BACKGROUND_DIR.glob("*.json")):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
            personas.append(doc)
        except Exception:
            continue
    return personas


PERSONAS = load_local_personas()
PERSONA_TITLES = [persona.get("title", "Unnamed") for persona in PERSONAS]
PERSONA_TITLES.insert(0, "None")

EVIDENCE_CATEGORIES = [
    "DCP Interaction",
    "Church/Faith",
    "Relapse Prevention",
    "Housing",
    "Career",
    "Legal",
    "Contact with Leo",
    "Documentation",
]
EVIDENCE_STATUSES = ["open", "in progress", "completed", "pending review"]
EVIDENCE_RISK_LEVELS = ["low", "medium", "high"]


def build_url(base_url: str, path: str) -> str:
    return urljoin(base_url.rstrip("/"), path)


def call_hermes(base_url: str, path: str, method: str = "GET", payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    url = build_url(base_url, path)
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        else:
            response = requests.post(url, json=payload or {}, timeout=10)
        response.raise_for_status()
        try:
            return response.json()
        except ValueError:
            return {"error": "Hermes returned non-JSON response", "text": response.text}
    except requests.RequestException as exc:
        return {"error": str(exc)}


def format_json(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, indent=2, ensure_ascii=False)
    return str(value)


def safe_value(source: Dict[str, Any], key: str, default: str = "-") -> str:
    return source.get(key, default) if isinstance(source, dict) else default


def build_background_payload(query: str, result: Dict[str, Any], advanced: Dict[str, Any], persona: str | None = None) -> Dict[str, Any]:
    lines = [
        f"Query: {query}",
        f"Simple: {safe_value(result, 'Simple')}",
        f"English: {safe_value(result, 'English')}",
        f"Jewish: {safe_value(result, 'Jewish')}",
        f"Atbash: {safe_value(advanced, 'atbash')}",
        f"English Qabalah: {safe_value(advanced, 'english_qabalah')}",
        f"Reduction (mispar_katan): {safe_value(advanced, 'mispar_katan')}",
    ]
    title = f"Gematria Oracle analysis - {query[:50]}"
    if persona and persona != "None":
        lines.insert(0, f"Persona: {persona}")
        title = f"{persona} | {title}"
    return {
        "title": title,
        "category": "documentation",
        "content": "\n\n".join(lines),
    }


def safe_transliteration(gematria: GematriaFull, query: str, method_name: str) -> str:
    try:
        method = getattr(gematria, method_name, None)
        if callable(method):
            return method(query) or "-"
    except Exception:
        pass
    return "-"


def ensure_session_state() -> None:
    for key in [
        "auth_status",
        "health_status",
        "profile_state",
        "background_docs",
        "sync_result",
        "revoke_response",
        "persona_publish",
        "last_export",
        "elite_summary",
        "evidence_items",
        "evidence_metrics",
        "evidence_report",
        "chat_prompt",
        "chat_response",
    ]:
        if key not in st.session_state:
            st.session_state[key] = None


ensure_session_state()

with st.sidebar:
    st.header("Hermes backend")
    base_url = st.selectbox("Hermes endpoint", DEFAULT_HERMES_URLS, index=0)
    custom_url = st.text_input("Custom Hermes URL", value="")
    if custom_url.strip():
        base_url = custom_url.strip()

    st.markdown(
        "Hermes base URL must point to a running backend with `/auth`, `/profile`, `/background`, and `/health` endpoints."
    )
    st.divider()

    if st.button("Refresh auth status"):
        st.session_state.auth_status = call_hermes(base_url, "/auth/status")
    if st.button("Revoke auth"):
        st.session_state.revoke_response = call_hermes(base_url, "/auth/revoke", method="POST")
    if st.button("Refresh health"):
        st.session_state.health_status = call_hermes(base_url, "/health")
    if st.button("Load profile"):
        st.session_state.profile_state = call_hermes(base_url, "/profile")
    if st.button("Load background docs"):
        st.session_state.background_docs = call_hermes(base_url, "/background/documents")
    if st.button("Sync profile"):
        st.session_state.sync_result = call_hermes(base_url, "/background/sync-profile", method="POST")
    if st.button("Load evidence items"):
        st.session_state.evidence_items = call_hermes(base_url, "/evidence/items")
    if st.button("Load evidence metrics"):
        st.session_state.evidence_metrics = call_hermes(base_url, "/evidence/metrics")
    if st.button("Publish local persona docs"):
        outputs = []
        for persona in PERSONAS:
            payload = {
                "title": persona.get("title", "Unnamed"),
                "category": persona.get("category", "documentation"),
                "content": persona.get("content", ""),
            }
            outputs.append({
                "title": payload["title"],
                "result": call_hermes(base_url, "/background/document", method="POST", payload=payload),
            })
        st.session_state.persona_publish = outputs

    st.markdown("---")
    auth_link = build_url(base_url, "/auth/start")
    st.markdown(f"[Launch Hermes OAuth flow]({auth_link})")
    st.markdown("---")
    st.markdown("### Cached Hermes state")
    st.code(format_json(st.session_state.auth_status), language="json")
    st.code(format_json(st.session_state.health_status), language="json")
    st.code(format_json(st.session_state.profile_state), language="json")
    st.code(format_json(st.session_state.background_docs), language="json")
    st.code(format_json(st.session_state.evidence_items), language="json")
    st.code(format_json(st.session_state.evidence_metrics), language="json")
    st.code(format_json(st.session_state.sync_result), language="json")
    st.code(format_json(st.session_state.persona_publish), language="json")

if GEMATRIA_IMPORT_ERROR:
    st.error(f"Unable to import GematriaFull: {GEMATRIA_IMPORT_ERROR}")
    st.stop()

if GematriaFull is None:
    st.error("GematriaFull is unavailable. Install the package or adjust Python path.")
    st.stop()

selected_persona = st.selectbox("Persona for export", PERSONA_TITLES, index=0)

with st.form("gematria_form"):
    query = st.text_input("Enter name, word or phrase", value="", placeholder="Type here...")
    submit = st.form_submit_button("CALCULATE")

if submit and query:
    g = GematriaFull()
    result = g.calc(query)
    advanced = g.explore_advanced(query)
    hebrew_text = safe_transliteration(g, query, "hebrew_transliteration")
    greek_text = safe_transliteration(g, query, "greek_transliteration")

    st.subheader(f"Results for: {query}")
    col_left, col_mid, col_right = st.columns([2.2, 1.8, 2.5])

    with col_left:
        st.markdown('<div class="section-header">Gematria Values</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Ordinal", safe_value(result, "Simple"))
            st.metric("Reduction", safe_value(advanced, "mispar_katan"))
            st.metric("Reverse", safe_value(result, "Jewish"))
        with c2:
            st.metric("Standard", safe_value(result, "English"))
            st.metric("English Qabalah", safe_value(advanced, "english_qabalah"))
            st.metric("Atbash", safe_value(advanced, "atbash"))

    with col_mid:
        st.markdown('<div class="section-header">Hebrew Translation</div>', unsafe_allow_html=True)
        st.code(hebrew_text or "-", language="text")
        st.markdown('<div class="section-header">Greek Translation</div>', unsafe_allow_html=True)
        st.code(greek_text or "-", language="text")

    with col_right:
        st.markdown('<div class="section-header">Detailed Breakdown</div>', unsafe_allow_html=True)
        st.write("Hebrew Gematria")
        st.code(format_json(safe_value(advanced, "hebrew", {})), language="json")
        st.write("English Gematria")
        st.code(format_json(safe_value(advanced, "english", {})), language="json")
        st.write("Simple Gematria")
        st.code(format_json(safe_value(advanced, "simple", {})), language="json")

    st.divider()
    st.markdown('<div class="section-header">Quick result tables</div>', unsafe_allow_html=True)
    st.dataframe(
        [
            {"Phrase": query, "Jewish": safe_value(result, "Jewish")},
            {"Phrase": query, "English": safe_value(result, "English"), "Simple": safe_value(result, "Simple")},
        ],
        use_container_width=True,
    )

    st.markdown("## Hermes sync actions")
    export_col, elite_col = st.columns(2)
    with export_col:
        if st.button("Export analysis to Hermes background"):
            payload = build_background_payload(query, result, advanced, selected_persona)
            st.session_state.last_export = call_hermes(base_url, "/background/document", method="POST", payload=payload)
            st.json(st.session_state.last_export)

    with elite_col:
        if st.button("Generate Hermes elite summary"):
            st.session_state.elite_summary = call_hermes(base_url, "/background/elitesummary", method="POST", payload={})
            st.json(st.session_state.elite_summary)

    st.markdown("### Hermes response preview")
    st.write("Base URL:", base_url)
    st.write("Auth status:")
    st.json(call_hermes(base_url, "/auth/status"))
    st.write("Health:")
    st.json(call_hermes(base_url, "/health"))

    st.divider()
    st.markdown('<div class="section-header">Hermes Chat</div>', unsafe_allow_html=True)
    with st.expander("Send a Hermes Chat Prompt", expanded=True):
        st.markdown(
            "This local `/chat` endpoint proxies to a configured upstream provider. "
            "Set `CHAT_PROVIDER_URL` or `HERMES_CHAT_ENDPOINT` in the environment."
        )
        chat_prompt = st.text_area("Chat prompt", value=st.session_state.chat_prompt or "", height=120)
        use_background = st.checkbox("Use background docs", value=True)
        profile_aware = st.checkbox("Profile aware", value=True)

        if st.button("Send Hermes Chat Prompt", key="send_hermes_chat"):
            st.session_state.chat_prompt = chat_prompt
            payload = {
                "message": chat_prompt,
                "use_background": use_background,
                "profile_aware": profile_aware,
            }
            st.session_state.chat_response = call_hermes(base_url, "/chat", method="POST", payload=payload)

        if st.session_state.chat_response:
            st.markdown("#### Chat response")
            st.json(st.session_state.chat_response)

    st.divider()
    st.markdown('<div class="section-header">Evidence Tracking Dashboard</div>', unsafe_allow_html=True)
    with st.expander("Evidence Dashboard", expanded=True):
        evidence_col, metrics_col = st.columns([2.5, 1.5])

        with evidence_col:
            st.subheader("Evidence Log")
            if st.button("Reload Evidence Items", key="reload_evidence_items"):
                st.session_state.evidence_items = call_hermes(base_url, "/evidence/items")
            if st.session_state.evidence_items:
                st.dataframe(st.session_state.evidence_items, use_container_width=True)
            else:
                st.info("No evidence items loaded. Click 'Reload Evidence Items' or use the sidebar button.")

            st.subheader("Milestones & Timeline")
            if st.session_state.evidence_items:
                milestone_items = [item for item in st.session_state.evidence_items if item.get("category") in ["Legal", "Contact with Leo", "Relapse Prevention", "DCP Interaction"]]
                for item in milestone_items[:5]:
                    st.markdown(f"- **{item.get('title')}** — {item.get('status')} (due: {item.get('due_date') or 'n/a'})")
            else:
                st.markdown("No milestone items loaded yet. Add evidence items and classify them as legal, DCP, relapse prevention or contact-related.")

            st.subheader("Add Evidence Item")
            with st.form("add_evidence_item_form"):
                evidence_title = st.text_input("Title", value="")
                evidence_category = st.selectbox("Category", EVIDENCE_CATEGORIES)
                evidence_description = st.text_area("Description", value="", height=140)
                evidence_date = st.date_input("Event Date", key="evidence_date")
                evidence_due_date = st.date_input("Due Date", key="evidence_due_date")
                evidence_status = st.selectbox("Status", EVIDENCE_STATUSES)
                evidence_risk_level = st.selectbox("Risk Level", EVIDENCE_RISK_LEVELS)
                evidence_follow_up = st.text_input("Follow-up Action", value="")
                evidence_tags = st.text_input("Tags (comma-separated)", value="")
                evidence_faith_support = st.checkbox("Faith / Church support", value=False)
                evidence_contact_type = st.text_input("Contact Type", value="")

                save_evidence = st.form_submit_button("Save Evidence Item")
                if save_evidence:
                    payload = {
                        "title": evidence_title,
                        "category": evidence_category,
                        "description": evidence_description,
                        "date": evidence_date.isoformat() if evidence_date else None,
                        "due_date": evidence_due_date.isoformat() if evidence_due_date else None,
                        "status": evidence_status,
                        "risk_level": evidence_risk_level,
                        "follow_up": evidence_follow_up,
                        "tags": [tag.strip() for tag in evidence_tags.split(",") if tag.strip()],
                        "faith_support": evidence_faith_support,
                        "contact_type": evidence_contact_type,
                    }
                    st.session_state.last_export = call_hermes(base_url, "/evidence/item", method="POST", payload=payload)
                    st.success("Evidence item added.")
                    st.json(st.session_state.last_export)
                    st.session_state.evidence_items = call_hermes(base_url, "/evidence/items")

        with metrics_col:
            st.subheader("Dashboard Metrics")
            if st.button("Refresh Evidence Metrics", key="refresh_evidence_metrics"):
                st.session_state.evidence_metrics = call_hermes(base_url, "/evidence/metrics")
            st.write(format_json(st.session_state.evidence_metrics))

            st.subheader("Monthly Report Generator")
            report_month = st.number_input("Month", min_value=1, max_value=12, value=6, key="report_month")
            report_year = st.number_input("Year", min_value=2023, max_value=2030, value=2026, key="report_year")
            report_note = st.text_area("Report Note", value="", key="report_note")
            if st.button("Generate Monthly Evidence Report", key="generate_evidence_report"):
                payload = {"month": int(report_month), "year": int(report_year), "note": report_note}
                st.session_state.evidence_report = call_hermes(base_url, "/evidence/report", method="POST", payload=payload)
                st.json(st.session_state.evidence_report)

            if FPDF_AVAILABLE:
                if st.button("Export Evidence Report to PDF", key="export_evidence_pdf"):
                    if st.session_state.evidence_report:
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Arial", size=12)
                        pdf.multi_cell(0, 8, f"Evidence Report Summary:\n{st.session_state.evidence_report.get('report_summary', '')}\n\n")
                        pdf.multi_cell(0, 8, f"Metrics:\n{format_json(st.session_state.evidence_report.get('metrics', {}))}")
                        pdf_path = Path.cwd() / "evidence_report.pdf"
                        pdf.output(str(pdf_path))
                        st.success(f"PDF exported to {pdf_path}")
                    else:
                        st.warning("Generate a monthly evidence report first.")
            else:
                st.info("Install fpdf in requirements to enable PDF export.")

else:
    st.markdown("## No phrase submitted yet")
    st.markdown("Enter a query and click CALCULATE to compute gematria values and sync results to Hermes.")
    st.divider()
    st.markdown('<div class="section-header">Hermes Diagnostics</div>', unsafe_allow_html=True)
    st.write("Base URL:", base_url)
    st.write("Auth status:")
    st.json(call_hermes(base_url, "/auth/status"))
    st.write("Health:")
    st.json(call_hermes(base_url, "/health"))

st.markdown("---")
st.markdown(
    "This app is designed to keep the Streamlit gematria interface synchronized with a Hermes backend by exposing OAuth, health, profile, and background document actions."
)
