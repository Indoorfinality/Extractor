import streamlit as st
from utils.api_client import get_all_deployments, toggle_deployment, delete_deployment

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.block-container { padding-top: 0rem !important; padding-bottom: 1rem !important; }

/* Top nav bar */
.ps-navbar {
    background: #0d1f38;
    color: white;
    padding: 0 28px;
    height: 52px;
    display: flex;
    align-items: center;
    font-weight: 700;
    font-size: 15px;
    letter-spacing: 0.01em;
    margin-bottom: 24px;
}

/* Table header */
.dep-table-header {
    display: grid;
    grid-template-columns: 1.8fr 1.6fr 2fr 2.4fr 1fr 1.2fr;
    gap: 8px;
    padding: 8px 16px;
    background: #f3f4f6;
    border-radius: 8px 8px 0 0;
    border: 1px solid #e5e7eb;
    border-bottom: none;
}
.dep-table-header span {
    font-size: 0.7rem;
    font-weight: 700;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}

/* Row card */
.dep-row {
    display: grid;
    grid-template-columns: 1.8fr 1.6fr 2fr 2.4fr 1fr 1.2fr;
    gap: 8px;
    align-items: center;
    padding: 12px 16px;
    border: 1px solid #e5e7eb;
    border-top: none;
    transition: background 0.12s;
}
.dep-row:hover { background: #f9fafb; }
.dep-row:last-child { border-radius: 0 0 8px 8px; }

.dep-api-name { font-weight: 800; font-size: 1.02rem; color: #ffffff; }
.dep-studio-name { font-size: 0.96rem; color: #ffffff; font-weight: 800; }
.dep-endpoint { font-family: monospace; font-size: 0.9rem; color: #ffffff; font-weight: 700; }
.dep-apikey { font-family: monospace; font-size: 0.9rem; color: #ffffff; font-weight: 700; }
.badge-active   { display:inline-flex; align-items:center; gap:5px; background:#dcfce7; color:#16a34a; border:1px solid #bbf7d0; border-radius:20px; padding:3px 10px; font-size:0.7rem; font-weight:600; }
.badge-inactive { display:inline-flex; align-items:center; gap:5px; background:#fee2e2; color:#dc2626; border:1px solid #fecaca; border-radius:20px; padding:3px 10px; font-size:0.7rem; font-weight:600; }
div[data-testid="stCodeBlock"] pre,
div[data-testid="stCodeBlock"] code {
    color: #ffffff !important;
    font-size: 0.9rem !important;
    font-weight: 700 !important;
}

/* Buttons */
button[kind="primary"] {
    background: #0d1f38 !important; border-color: #0d1f38 !important;
    color: white !important; border-radius: 6px !important;
    font-weight: 600 !important; font-size: 12px !important;
}
button[kind="primary"]:hover { background: #162d4f !important; border-color: #162d4f !important; }
button[kind="secondary"] {
    padding: 0.22rem 0.5rem !important; min-height: 30px !important;
    background: transparent !important; border: 1px solid #e5e7eb !important;
    color: #6b7280 !important; font-size: 12px !important;
    border-radius: 6px !important; box-shadow: none !important;
}
button[kind="secondary"]:hover { background: #f3f4f6 !important; color: #111827 !important; }
#MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="ps-navbar">🌐&nbsp; API Deployments</div>', unsafe_allow_html=True)

# ── Reload button ──────────────────────────────────────────────────────────────
_, col_reload = st.columns([8, 1])
with col_reload:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

# ── Fetch all deployments ──────────────────────────────────────────────────────
all_deps = get_all_deployments()

if not all_deps:
    st.info("No API deployments found. Open a Prompt Studio and click **Deploy as API** to create one.")
    st.stop()

# ── Stats bar ─────────────────────────────────────────────────────────────────
total   = len(all_deps)
active  = sum(1 for d in all_deps if d["is_active"])
inactive = total - active

s1, s2, s3 = st.columns(3)
s1.metric("Total Deployments", total)
s2.metric("Active",   active,   delta=None)
s3.metric("Inactive", inactive, delta=None)

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ── Table header ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="dep-table-header">
  <span>API Name</span>
  <span>Prompt Studio</span>
  <span>Endpoint URL</span>
  <span>API Key</span>
  <span>Status</span>
  <span>Actions</span>
</div>
""", unsafe_allow_html=True)

# ── Rows ──────────────────────────────────────────────────────────────────────
for dep in all_deps:
    dep_id      = dep["id"]
    badge       = "<span class='badge-active'>● Active</span>" if dep["is_active"] else "<span class='badge-inactive'>○ Inactive</span>"
    full_endpoint_url = (
        dep["endpoint_url"]
        if str(dep["endpoint_url"]).startswith("http")
        else f"http://127.0.0.1:8001{dep['endpoint_url']}"
    )
    full_api_key = dep["api_key"]

    # Render the static info part via markdown, actions via Streamlit columns
    c_name, c_studio, c_url, c_key, c_status, c_actions = st.columns([1.8, 1.6, 2, 2.4, 1, 1.2])

    with c_name:
        st.markdown(f"<div class='dep-api-name'><strong>{dep['name']}</strong></div>", unsafe_allow_html=True)
    with c_studio:
        st.markdown(f"<div class='dep-studio-name'><strong>{dep.get('studio_name','—')}</strong></div>", unsafe_allow_html=True)
    with c_url:
        st.markdown("**Endpoint URL**")
        st.code(full_endpoint_url, language="text")
    with c_key:
        st.markdown("**API Key**")
        st.code(full_api_key, language="text")
    with c_status:
        st.markdown(f"<div style='padding-top:4px'>{badge}</div>", unsafe_allow_html=True)
    with c_actions:
        tog_label = "Disable" if dep["is_active"] else "Enable"
        a1, a2 = st.columns(2)
        with a1:
            if st.button(tog_label, key=f"adep_tog_{dep_id}", use_container_width=True):
                toggle_deployment(dep_id, not dep["is_active"])
                st.rerun()
        with a2:
            if st.button("🗑️", key=f"adep_del_{dep_id}", help="Delete", use_container_width=True):
                st.session_state[f"adep_confirm_{dep_id}"] = True
                st.rerun()

    # Confirm delete (inline below the row)
    if st.session_state.get(f"adep_confirm_{dep_id}"):
        with st.container(border=True):
            st.warning(f"Delete API **{dep['name']}** permanently?")
            by, bn = st.columns(2)
            with by:
                if st.button("Yes, delete", key=f"adep_cdy_{dep_id}", type="primary", use_container_width=True):
                    delete_deployment(dep_id)
                    st.session_state.pop(f"adep_confirm_{dep_id}", None)
                    st.rerun()
            with bn:
                if st.button("Cancel", key=f"adep_cdn_{dep_id}", use_container_width=True):
                    st.session_state.pop(f"adep_confirm_{dep_id}", None)
                    st.rerun()

    st.markdown("<div style='border-bottom:1px solid #f3f4f6'></div>", unsafe_allow_html=True)
