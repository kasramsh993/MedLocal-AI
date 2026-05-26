import streamlit as st


def apply_theme() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --ml-bg: #f3f1ec;
    --ml-surface: #fbfaf7;
    --ml-surface-soft: #f7f5f0;
    --ml-panel: #ffffff;
    --ml-ink: #172033;
    --ml-muted: #667085;
    --ml-border: #dde3ea;
    --ml-border-strong: #c8d1dc;
    --ml-blue: #102a43;
    --ml-blue-2: #183b56;
    --ml-blue-3: #2f5d7c;
    --ml-accent: #0f5f7a;
    --ml-emerald: #11845b;
    --ml-warning: #9a6a14;
    --ml-shadow: 0 16px 45px rgba(16, 42, 67, 0.10);
    --ml-shadow-soft: 0 8px 24px rgba(16, 42, 67, 0.08);
    --ml-radius: 18px;
}

html, body, [class*="css"] {
    font-family: 'Inter', 'Roboto', 'Segoe UI', sans-serif;
    color: var(--ml-ink);
}

.stApp {
    background:
        radial-gradient(circle at 18% 0%, rgba(47, 93, 124, 0.08), transparent 28%),
        linear-gradient(180deg, #f8f7f3 0%, var(--ml-bg) 100%);
}

.block-container {
    max-width: 1480px;
    padding-top: 0.35rem;
    padding-bottom: 1rem;
}

#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] {
    visibility: hidden;
    height: 0;
}

header[data-testid="stHeader"] {
    background: transparent;
    height: 0.5rem;
}

[data-testid="stSidebar"] {
    background: #eef1f3;
    border-right: 1px solid var(--ml-border);
}

[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p {
    color: var(--ml-ink) !important;
}

h1, h2, h3, h4 {
    color: var(--ml-ink) !important;
    letter-spacing: 0;
}

.ml-app-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    padding: 0.15rem 0 0.55rem;
}

.ml-brand {
    display: flex;
    align-items: center;
    gap: 0.9rem;
}

.ml-logo {
    width: 36px;
    height: 36px;
    border-radius: 12px;
    background: linear-gradient(145deg, var(--ml-blue), var(--ml-blue-3));
    color: #fff;
    display: grid;
    place-items: center;
    box-shadow: var(--ml-shadow-soft);
    font-weight: 800;
    font-size: 0.9rem;
}

.ml-title {
    font-size: 1.12rem;
    line-height: 1.15;
    font-weight: 800;
    color: var(--ml-blue);
}

.ml-subtitle {
    margin-top: 0.18rem;
    color: var(--ml-muted);
    font-size: 0.78rem;
}

.ml-status-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.38rem 0.6rem;
    border-radius: 999px;
    background: #eaf7f1;
    color: var(--ml-emerald);
    border: 1px solid #c7eadb;
    font-size: 0.76rem;
    font-weight: 700;
}

.ml-layout-card,
.ml-panel,
.ml-card {
    background: rgba(251, 250, 247, 0.94);
    border: 1px solid var(--ml-border);
    border-radius: var(--ml-radius);
    box-shadow: var(--ml-shadow-soft);
}

.ml-panel {
    padding: 0.82rem;
    min-height: 0;
}

.ml-panel-header,
.ml-workflow-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
    margin-bottom: 0.55rem;
}

.ml-section-kicker {
    color: var(--ml-accent);
    font-size: 0.72rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.ml-section-title {
    font-size: 1.05rem;
    font-weight: 800;
    color: var(--ml-blue);
    margin-top: 0.1rem;
}

.ml-section-note {
    color: var(--ml-muted);
    font-size: 0.82rem;
    margin-top: 0.18rem;
}

.ml-card {
    padding: 0.72rem;
    margin-bottom: 0.55rem;
}

.ml-metric-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.75rem;
}

.ml-mini-label {
    color: var(--ml-muted);
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.ml-mini-value {
    color: var(--ml-blue);
    font-size: 1rem;
    font-weight: 800;
    margin-top: 0.15rem;
}

.ml-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.45rem 0.65rem;
    border-radius: 999px;
    background: #edf4f7;
    color: var(--ml-blue-3);
    border: 1px solid #d7e6ed;
    font-weight: 800;
    font-size: 0.78rem;
}

.ml-time-saved {
    color: var(--ml-muted);
    font-size: 0.82rem;
    text-align: center;
    margin-top: 0.55rem;
}

.stTextInput > div > div > input,
.stDateInput > div > div > input,
.stTextArea textarea,
.stSelectbox > div > div,
.stRadio > div {
    background: var(--ml-panel) !important;
    color: var(--ml-ink) !important;
    border: 1px solid var(--ml-border) !important;
    border-radius: 14px !important;
    box-shadow: 0 1px 0 rgba(16, 42, 67, 0.03);
}

.stRadio [role="radiogroup"] {
    gap: 0.35rem !important;
}

.stRadio [role="radio"] + div,
.stRadio label {
    line-height: 1.1 !important;
}

.stTextArea textarea {
    line-height: 1.55 !important;
    font-size: 0.95rem !important;
    padding: 0.75rem !important;
}

label, .stSelectbox label, .stTextInput label, .stTextArea label, .stRadio label {
    color: var(--ml-blue) !important;
    font-size: 0.82rem !important;
    font-weight: 750 !important;
}

.stButton > button,
.stDownloadButton > button {
    border-radius: 14px !important;
    border: 1px solid transparent !important;
    min-height: 44px !important;
    font-weight: 800 !important;
    transition: transform 120ms ease, box-shadow 120ms ease, background 120ms ease;
}

.stButton > button[kind="primary"],
.stButton > button {
    background: linear-gradient(135deg, var(--ml-blue), var(--ml-blue-3)) !important;
    color: #fff !important;
    box-shadow: 0 14px 28px rgba(16, 42, 67, 0.18) !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    transform: translateY(-1px);
}

.stDownloadButton > button {
    background: var(--ml-panel) !important;
    color: var(--ml-blue) !important;
    border-color: var(--ml-border-strong) !important;
    box-shadow: none !important;
}

.ml-progress-box {
    padding: 1rem;
    border-radius: 16px;
    background: #eef5f7;
    border: 1px solid #d7e6ed;
    margin: 0.8rem 0;
}

.ml-progress-stage {
    color: var(--ml-blue);
    font-size: 0.9rem;
    font-weight: 800;
    margin-bottom: 0.4rem;
}

.ml-letter-shell {
    background: #dfe5eb;
    border-radius: 18px;
    padding: 0.7rem;
    border: 1px solid var(--ml-border-strong);
    box-shadow: var(--ml-shadow);
}

.ml-letter-paper {
    background: #fffdf8;
    color: #1c2533;
    border-radius: 8px;
    padding: 28px 34px;
    min-height: 0;
    box-shadow: 0 12px 35px rgba(16, 42, 67, 0.16);
    font-size: 0.9rem;
    line-height: 1.68;
}

.ml-letter-head {
    display: flex;
    justify-content: space-between;
    gap: 1.5rem;
    padding-bottom: 10px;
    border-bottom: 2px solid var(--ml-blue);
    margin-bottom: 14px;
}

.ml-practice-name {
    color: var(--ml-blue);
    font-size: 1.05rem;
    font-weight: 850;
}

.ml-practice-meta,
.ml-letter-meta {
    color: #5f6b7a;
    font-size: 0.74rem;
    line-height: 1.55;
}

.ml-letter-title {
    color: var(--ml-blue);
    font-size: 1.28rem;
    font-weight: 850;
    margin: 0.8rem 0 0.6rem;
}

.ml-patient-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.55rem 1.5rem;
    padding: 0.9rem;
    border: 1px solid #e4e8ed;
    background: #f8f7f3;
    border-radius: 10px;
    margin-bottom: 1.1rem;
}

.ml-letter-paper h1,
.ml-letter-paper h2,
.ml-letter-paper h3 {
    color: var(--ml-blue) !important;
    font-family: 'Inter', 'Roboto', sans-serif;
    letter-spacing: 0;
}

.ml-letter-paper h2 {
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    border-bottom: 1px solid #dfe5eb;
    padding-bottom: 4px;
    margin-top: 1.35rem;
}

.ml-signature {
    margin-top: 1.5rem;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
}

.ml-signature-line {
    border-top: 1px solid #aeb8c4;
    padding-top: 0.5rem;
    color: #5f6b7a;
    font-size: 0.78rem;
}

.ml-code-row {
    display: grid;
    grid-template-columns: 72px 1fr auto;
    gap: 0.65rem;
    align-items: center;
    padding: 0.45rem 0;
    border-bottom: 1px solid var(--ml-border);
}

.ml-code-row:last-child {
    border-bottom: none;
}

.ml-code {
    font-weight: 850;
    color: var(--ml-blue);
}

.ml-code-label {
    color: var(--ml-ink);
    font-size: 0.86rem;
}

.ml-confidence {
    color: var(--ml-emerald);
    background: #eaf7f1;
    border: 1px solid #c7eadb;
    border-radius: 999px;
    padding: 0.22rem 0.45rem;
    font-size: 0.72rem;
    font-weight: 800;
}

.ml-health-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.7rem;
}

.ml-health-value {
    font-size: 1rem;
    font-weight: 850;
    color: var(--ml-blue);
}

.ml-empty-output {
    margin-top: 0.65rem;
    padding: 1rem;
    border: 1px dashed var(--ml-border-strong);
    border-radius: 14px;
    background: #f8f7f3;
    color: var(--ml-muted);
    min-height: 96px;
}

.ml-transcript-card {
    min-height: 86px;
    padding: 0.75rem;
    border-radius: 14px;
    background: #ffffff;
    border: 1px solid var(--ml-border);
    color: var(--ml-ink);
    line-height: 1.5;
    font-size: 0.92rem;
    margin-bottom: 0.55rem;
    white-space: pre-wrap;
}

.ml-billing-row {
    padding: 0.62rem 0;
    border-bottom: 1px solid var(--ml-border);
    color: var(--ml-ink);
}

.ml-billing-row:last-child {
    border-bottom: none;
}

@media (max-width: 900px) {
    .ml-app-header,
    .ml-letter-head,
    .ml-signature {
        grid-template-columns: 1fr;
        flex-direction: column;
    }
    .ml-patient-grid,
    .ml-metric-grid,
    .ml-health-grid {
        grid-template-columns: 1fr;
    }
    .ml-letter-paper {
        padding: 28px 24px;
    }
}
</style>
        """,
        unsafe_allow_html=True,
    )
