import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Prompt Studio",
    layout="wide",
    page_icon="📋",
    initial_sidebar_state="collapsed",
)

PAGES_DIR = Path(__file__).parent / "utils" / "pages"

# ── Session defaults ───────────────────────────────────────────────────────────
if "current_studio_id" not in st.session_state:
    st.session_state.current_studio_id = None
if "_main_tab" not in st.session_state:
    st.session_state["_main_tab"] = "studio"   # default to Prompt Studio

# ── If we're inside a studio detail, skip the tab switcher entirely ────────────
if st.session_state.current_studio_id is not None:
    exec((PAGES_DIR / "Studio_Detail.py").read_text())
    st.stop()

# ── Top-level tab switcher ─────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.block-container { padding-top: 0rem !important; }
#MainMenu, footer { visibility: hidden; }

.main-tab-bar {
    background: #0d1f38;
    display: flex;
    align-items: center;
    gap: 0;
    padding: 0 24px;
    height: 52px;
    margin-bottom: 0;
}
.main-tab-bar .brand {
    color: white;
    font-weight: 700;
    font-size: 15px;
    letter-spacing: 0.01em;
    margin-right: 28px;
    white-space: nowrap;
}
.tab-btn-active {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 6px 18px;
    background: rgba(255,255,255,0.12);
    color: #ffffff;
    border-radius: 6px 6px 0 0;
    font-size: 13px; font-weight: 600;
    border-bottom: 2px solid #6366f1;
    cursor: default;
}
.tab-btn-inactive {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 6px 18px;
    background: transparent;
    color: #94a3b8;
    border-radius: 6px 6px 0 0;
    font-size: 13px; font-weight: 500;
    border-bottom: 2px solid transparent;
    cursor: pointer;
}
.tab-btn-inactive:hover { color: #e2e8f0; background: rgba(255,255,255,0.06); }
.tab-divider {
    border: none;
    border-top: 1px solid #e5e7eb;
    margin: 0 0 20px 0;
}
</style>
""", unsafe_allow_html=True)

# Render the dark brand bar
st.markdown('<div class="main-tab-bar"><span class="brand">📋 Prompt Studio</span></div>', unsafe_allow_html=True)

# Streamlit buttons acting as tabs (right below the navbar)
_tab = st.session_state["_main_tab"]
tc1, tc2, _gap = st.columns([1.4, 1.8, 8])
with tc1:
    if st.button(
        "📋 Prompt Studio",
        key="tab_studio_btn",
        type="primary" if _tab == "studio" else "secondary",
        use_container_width=True,
    ):
        st.session_state["_main_tab"] = "studio"
        st.rerun()
with tc2:
    if st.button(
        "🌐 API Deployments",
        key="tab_api_btn",
        type="primary" if _tab == "api" else "secondary",
        use_container_width=True,
    ):
        st.session_state["_main_tab"] = "api"
        st.rerun()

st.markdown("<hr class='tab-divider'>", unsafe_allow_html=True)

# ── Route to correct subpage ───────────────────────────────────────────────────
if _tab == "api":
    exec((PAGES_DIR / "API_Deployments.py").read_text())
else:
    exec((PAGES_DIR / "Prompt_Studio.py").read_text())
