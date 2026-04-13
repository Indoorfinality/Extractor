import streamlit as st
from utils.api_client import get_studios, create_studio, delete_studio, update_studio

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

/* Remove default top padding */
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

/* Studio list rows */
.studio-row {
    display: flex;
    align-items: center;
    padding: 14px 12px;
    border-bottom: 1px solid #f0f2f5;
    border-radius: 6px;
    transition: background 0.15s;
    gap: 12px;
}
.studio-row:hover { background: #f9fafb; }
.studio-name { font-weight: 600; font-size: 0.88rem; color: #111827; margin: 0 0 2px 0; }
.studio-desc { font-size: 0.76rem; color: #9ca3af; margin: 0; }
.studio-name-header {
    background: #1e1b4b;
    border-radius: 6px;
    padding: 7px 12px;
    margin-bottom: 4px;
    display: inline-block;
}
.studio-name-header span {
    font-size: 1rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: 0.01em;
}
.owner-pill {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: #f3f4f6;
    border-radius: 20px;
    padding: 4px 13px;
    font-size: 0.73rem;
    color: #6b7280;
    white-space: nowrap;
}
.owner-dot {
    width: 17px; height: 17px;
    background: #6366f1;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 9px;
    font-weight: 700;
}

/* Make secondary (icon) buttons look like icon-only buttons */
button[kind="secondary"] {
    padding: 0.25rem 0.55rem !important;
    min-height: 32px !important;
    background: transparent !important;
    border: 1px solid #e5e7eb !important;
    color: #6b7280 !important;
    font-size: 13px !important;
    border-radius: 6px !important;
    box-shadow: none !important;
    line-height: 1 !important;
}
button[kind="secondary"]:hover {
    background: #f3f4f6 !important;
    color: #111827 !important;
    border-color: #d1d5db !important;
}

/* Primary button → dark navy */
button[kind="primary"] {
    background: #0d1f38 !important;
    border-color: #0d1f38 !important;
    color: white !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}
button[kind="primary"]:hover {
    background: #162d4f !important;
    border-color: #162d4f !important;
}

/* Inline edit container */
.edit-box {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 14px 16px;
    margin: 4px 0 8px 0;
}

/* Search input styling */
div[data-testid="stTextInput"] input {
    border-radius: 6px !important;
    font-size: 13px !important;
    border-color: #e5e7eb !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="ps-navbar">📋&nbsp; Prompt Studio</div>', unsafe_allow_html=True)

col_search, col_gap, col_new = st.columns([4, 0.1, 1])

with col_search:
    search_q = st.text_input(
        "search",
        placeholder="🔍  Search by name...",
        label_visibility="collapsed",
        key="ps_search",
    )

with col_new:
    if st.button("＋ New Project", key="btn_new_project", type="primary", use_container_width=True):
        st.session_state["show_new_form"] = not st.session_state.get("show_new_form", False)

if st.session_state.get("show_new_form"):
    with st.container(border=True):
        st.markdown("**New Project**")
        np_name = st.text_input("Project name", key="np_name", placeholder="e.g. Invoice Extractor")
        np_desc = st.text_input("Description (optional)", key="np_desc", placeholder="Short description")
        c1, c2, _ = st.columns([1, 1, 3])
        with c1:
            if st.button("Create", key="np_create", type="primary", use_container_width=True):
                name_v = (st.session_state.get("np_name") or "").strip()
                if not name_v:
                    st.warning("Enter a project name.")
                else:
                    result = create_studio(name_v, st.session_state.get("np_desc") or "")
                    if result:
                        st.session_state["show_new_form"] = False
                        for k in ("np_name", "np_desc"):
                            st.session_state.pop(k, None)
                        st.session_state.pop("_studios_list_fp", None)
                        st.rerun()
        with c2:
            if st.button("Cancel", key="np_cancel", use_container_width=True):
                st.session_state["show_new_form"] = False
                st.rerun()

st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

studios = get_studios()

fp = tuple((s["id"], s["name"], s.get("description") or "") for s in studios)
if st.session_state.get("_studios_list_fp") != fp:
    st.session_state["_studios_list_fp"] = fp
    for s in studios:
        st.session_state[f"sn_{s['id']}"] = s["name"]
        st.session_state[f"sd_{s['id']}"] = s.get("description") or ""


query = (search_q or "").strip().lower()
visible = [s for s in studios if query in s["name"].lower() or query in (s.get("description") or "").lower()] if query else studios

if not visible:
    st.info("No projects found." if query else "No projects yet. Click **＋ New Project** to create one.")
else:
    # Column header
    h1, h2, h3 = st.columns([5, 2, 1])
    with h1:
        st.markdown("<span style='font-size:0.72rem;color:#9ca3af;font-weight:600;letter-spacing:0.05em;text-transform:uppercase;'>Project</span>", unsafe_allow_html=True)
    with h2:
        st.markdown("<span style='font-size:0.72rem;color:#9ca3af;font-weight:600;letter-spacing:0.05em;text-transform:uppercase;'>Owner</span>", unsafe_allow_html=True)
    with h3:
        st.markdown("<span style='font-size:0.72rem;color:#9ca3af;font-weight:600;letter-spacing:0.05em;text-transform:uppercase;'>Actions</span>", unsafe_allow_html=True)

    st.markdown("<div style='border-bottom:1px solid #e5e7eb;margin-bottom:2px'></div>", unsafe_allow_html=True)

    for s in visible:
        sid = s["id"]
        is_editing = st.session_state.get(f"editing_{sid}", False)

        col_name, col_owner, col_acts = st.columns([5, 2, 1])

        with col_name:
            # Clickable studio name
            st.markdown(
                f"<div class='studio-name-header'><span>{s['name']}</span></div>"
                f"<p style='margin:2px 0 0 0;font-size:0.76rem;color:#9ca3af'>{s.get('description') or ''}</p>",
                unsafe_allow_html=True,
            )
            if st.button("Open →", key=f"nav_{sid}", help=f"Open {s['name']}"):
                st.session_state.current_studio_id = sid
                st.rerun()

        with col_owner:
            st.markdown(
                '<span class="owner-pill">'
                '<span class="owner-dot">M</span>'
                'Owned By: <strong>Me</strong>'
                '</span>',
                unsafe_allow_html=True,
            )

        with col_acts:
            a1, a2, a3 = st.columns(3)
            with a1:
                if st.button("✏️", key=f"edit_{sid}", help="Edit"):
                    entering = not is_editing
                    st.session_state[f"editing_{sid}"] = entering
                    if entering:
                        # Pre-seed with current values so inputs are never blank
                        st.session_state[f"sn_{sid}"] = s["name"]
                        st.session_state[f"sd_{sid}"] = s.get("description") or ""
                    st.rerun()
            with a2:
                st.button("🔗", key=f"share_{sid}", help="Share (coming soon)", disabled=True)
            with a3:
                if st.button("🗑️", key=f"del_{sid}", help="Delete this project"):
                    st.session_state[f"confirm_del_{sid}"] = True
                    st.rerun()

        # ── Confirm delete ──────────────────────────────────────────────────
        if st.session_state.get(f"confirm_del_{sid}"):
            with st.container(border=True):
                st.warning(f"Delete **{s['name']}**? This cannot be undone.")
                y, n = st.columns(2)
                with y:
                    if st.button("Yes, delete", key=f"confirm_yes_{sid}", type="primary", use_container_width=True):
                        delete_studio(sid)
                        for k in (f"sn_{sid}", f"sd_{sid}", "_studios_list_fp", f"confirm_del_{sid}"):
                            st.session_state.pop(k, None)
                        st.rerun()
                with n:
                    if st.button("Cancel", key=f"confirm_no_{sid}", use_container_width=True):
                        st.session_state.pop(f"confirm_del_{sid}", None)
                        st.rerun()

        # ── Inline edit form ────────────────────────────────────────────────
        if is_editing:
            with st.container(border=True):
                st.markdown(f"<div style='font-size:0.8rem;font-weight:600;color:#374151;margin-bottom:8px'>Edit: {s['name']}</div>", unsafe_allow_html=True)
                e1, e2 = st.columns(2)
                with e1:
                    st.text_input("Project name", key=f"sn_{sid}", label_visibility="collapsed", placeholder="Project name")
                with e2:
                    st.text_input("Description", key=f"sd_{sid}", label_visibility="collapsed", placeholder="Description")
                sv, cl = st.columns([1, 4])
                with sv:
                    if st.button("Save", key=f"save_{sid}", type="primary", use_container_width=True):
                        name_v = (st.session_state.get(f"sn_{sid}") or "").strip()
                        if not name_v:
                            st.warning("Name cannot be empty.")
                        else:
                            desc_v = st.session_state.get(f"sd_{sid}") or ""
                            if update_studio(sid, name=name_v, description=desc_v):
                                st.session_state[f"editing_{sid}"] = False
                                st.session_state.pop("_studios_list_fp", None)
                                st.rerun()
                with cl:
                    if st.button("Cancel", key=f"cancel_edit_{sid}", use_container_width=True):
                        st.session_state[f"editing_{sid}"] = False
                        st.rerun()

        st.markdown("<div style='border-bottom:1px solid #f3f4f6'></div>", unsafe_allow_html=True)
