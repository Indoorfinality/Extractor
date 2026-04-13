import html
import json
import streamlit as st
from utils.api_client import (
    get_prompts,
    create_prompt,
    update_prompt,
    delete_prompt,
    upload_document,
    get_documents,
    get_studios,
    run_extraction,
    get_extraction_result,
    get_document_file_url,
    get_deployments,
    create_deployment,
    delete_deployment,
    toggle_deployment,
)

API_BASE = "http://127.0.0.1:8001/api"

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif !important; }
.block-container { padding-top: 0 !important; padding-bottom: 1rem !important; max-width: 100% !important; }
#MainMenu, footer { visibility: hidden; }

/* Navbar */
.ps-navbar {
    background: #1e1b4b;
    color: white;
    padding: 0 20px;
    height: 50px;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 0;
}
.ps-bc-dim  { color: #a5b4fc; font-weight: 400; }
.ps-bc-sep  { color: #6366f1; margin: 0 6px; }
.ps-bc-cur  { color: #ffffff; font-weight: 600; }

/* Tab pills */
.tab-pill-active {
    display: inline-block;
    padding: 5px 16px;
    background: #4f46e5;
    color: white;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
    border: 1px solid #4f46e5;
    cursor: pointer;
}
.tab-pill-inactive {
    display: inline-block;
    padding: 5px 16px;
    background: white;
    color: #6b7280;
    border-radius: 6px;
    font-size: 13px;
    border: 1px solid #e5e7eb;
    cursor: pointer;
}

/* Field cards */
.field-card-header {
    background: #1e1b4b;
    border-radius: 6px;
    padding: 8px 12px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.field-name {
    font-size: 1.05rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0;
    letter-spacing: 0.01em;
}
.field-prompt {
    font-size: 0.8rem;
    color: #6366f1;
    font-style: italic;
    line-height: 1.55;
    margin: 0 0 10px 0;
}
.field-value {
    background: #f0fdf4;
    border-left: 3px solid #22c55e;
    border-radius: 4px;
    padding: 7px 12px;
    font-size: 0.85rem;
    font-weight: 600;
    color: #15803d;
    margin-bottom: 8px;
}
.field-value-empty {
    background: #f9fafb;
    border-left: 3px solid #e5e7eb;
    border-radius: 4px;
    padding: 7px 12px;
    font-size: 0.8rem;
    color: #d1d5db;
    font-style: italic;
    margin-bottom: 8px;
}
.enabled-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: #ede9fe;
    color: #4f46e5;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.68rem;
    font-weight: 600;
}
.token-info { font-size: 0.68rem; color: #9ca3af; }

/* Deploy as API section */
.deploy-api-section {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
    border-radius: 12px;
    padding: 24px 28px;
    margin-top: 28px;
    border: 1px solid #312e81;
}
.deploy-api-section h4 {
    color: #e0e7ff;
    font-size: 1rem;
    font-weight: 700;
    margin: 0 0 16px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}
.dep-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
}
.dep-name { color: #c7d2fe; font-weight: 600; font-size: 0.85rem; }
.dep-key  { color: #818cf8; font-size: 0.75rem; font-family: monospace; }
.dep-url  { color: #6ee7b7; font-size: 0.75rem; font-family: monospace; }
.dep-active   { background:#16a34a22; color:#4ade80; border:1px solid #166534; border-radius:20px; padding:2px 9px; font-size:0.68rem; font-weight:600; }
.dep-inactive { background:#dc262622; color:#f87171; border:1px solid #991b1b; border-radius:20px; padding:2px 9px; font-size:0.68rem; font-weight:600; }
.existing-warn {
    background: #451a0322;
    border: 1px solid #92400e;
    border-radius: 8px;
    padding: 10px 14px;
    color: #fbbf24;
    font-size: 0.8rem;
    margin-bottom: 12px;
}

/* Raw / JSON output block */
.raw-output {
    background: #1e293b;
    color: #e2e8f0;
    border-radius: 8px;
    padding: 16px;
    font-family: 'JetBrains Mono', 'Fira Code', monospace !important;
    font-size: 0.73rem;
    line-height: 1.65;
    max-height: 660px;
    overflow-y: auto;
    white-space: pre-wrap;
    word-break: break-all;
}

/* PDF iframe */
.pdf-wrap {
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    overflow: hidden;
    background: #f8fafc;
}

/* Add prompt panel */
.add-prompt-panel {
    background: #f5f3ff;
    border: 1.5px solid #c4b5fd;
    border-radius: 8px;
    padding: 16px;
    margin-top: 10px;
}

/* Global button overrides */
button[kind="primary"] {
    background: #4f46e5 !important;
    border-color: #4f46e5 !important;
    color: white !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}
button[kind="primary"]:hover { background: #4338ca !important; border-color: #4338ca !important; }
button[kind="secondary"] {
    border-radius: 6px !important;
    font-size: 12px !important;
    border-color: #e5e7eb !important;
    color: #374151 !important;
}
button[kind="secondary"]:hover {
    background: #f3f4f6 !important;
    border-color: #d1d5db !important;
}
/* Make icon buttons (single emoji) smaller */
div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
    padding: 0.2rem 0.45rem !important;
    min-height: 30px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Guards ────────────────────────────────────────────────────────────────────
studio_id = st.session_state.get("current_studio_id")
if studio_id is None:
    st.warning("No studio selected.")
    st.stop()

studios = get_studios()
current = next((s for s in studios if s["id"] == studio_id), None)
if not current:
    st.error("Studio not found.")
    st.stop()

# ── Navbar ────────────────────────────────────────────────────────────────────
st.markdown(
    f'<div class="ps-navbar">'
    f'📋&nbsp;<span class="ps-bc-dim">Prompt Studio</span>'
    f'<span class="ps-bc-sep">/</span>'
    f'<span class="ps-bc-cur">{html.escape(current["name"])}</span>'
    f'</div>',
    unsafe_allow_html=True,
)

# ── Deploy modal ───────────────────────────────────────────────────────────────
@st.dialog("Deploy as API")
def deploy_api_dialog():
    deployments = get_deployments(studio_id)

    if deployments:
        st.markdown(
            "<div style='font-size:0.8rem;color:#6b7280;font-weight:600;margin-bottom:6px;'"
            ">EXISTING APIS FOR THIS STUDIO</div>",
            unsafe_allow_html=True,
        )
        for dep in deployments:
            status_badge = (
                "<span class='dep-active'>● Active</span>"
                if dep["is_active"]
                else "<span class='dep-inactive'>○ Inactive</span>"
            )
            with st.container(border=True):
                dc1, dc2, dc3 = st.columns([3, 2, 1])
                with dc1:
                    st.markdown(
                        f"<div class='dep-name'>{dep['name']}</div>"
                        f"<div class='dep-url'>{dep['endpoint_url']}</div>"
                        f"<div class='dep-key'>🔑 {dep['api_key'][:28]}...</div>",
                        unsafe_allow_html=True,
                    )
                with dc2:
                    st.markdown(f"<div style='padding-top:6px'>{status_badge}</div>", unsafe_allow_html=True)
                    tog_label = "Disable" if dep["is_active"] else "Enable"
                    if st.button(tog_label, key=f"tog_dep_{dep['id']}"):
                        toggle_deployment(dep["id"], not dep["is_active"])
                        st.rerun()
                with dc3:
                    st.markdown("<div style='padding-top:4px'></div>", unsafe_allow_html=True)
                    if st.button("🗑️ Delete", key=f"del_dep_{dep['id']}"):
                        st.session_state[f"confirm_del_dep_{dep['id']}"] = True
                        st.rerun()

                if st.session_state.get(f"confirm_del_dep_{dep['id']}"):
                    st.warning(f"Delete API **{dep['name']}**? This is irreversible.")
                    cy, cn = st.columns(2)
                    with cy:
                        if st.button("Yes, delete", key=f"cdy_dep_{dep['id']}", type="primary", use_container_width=True):
                            delete_deployment(dep["id"])
                            st.session_state.pop(f"confirm_del_dep_{dep['id']}", None)
                            st.rerun()
                    with cn:
                        if st.button("Cancel", key=f"cdn_dep_{dep['id']}", use_container_width=True):
                            st.session_state.pop(f"confirm_del_dep_{dep['id']}", None)
                            st.rerun()

    if deployments:
        st.markdown(
            "<div class='existing-warn'>⚠️ This studio already has "
            f"{len(deployments)} deployed API(s). You can deploy another with a different name.</div>",
            unsafe_allow_html=True,
        )

    default_name = f"{current['name'].lower().replace(' ', '-')}-api"
    api_name = st.text_input(
        "Endpoint name (used in URL)",
        value=st.session_state.get(f"_dep_name_{studio_id}", default_name),
        key=f"dep_name_input_{studio_id}",
        placeholder="e.g. invoice-extractor-api",
        help="Only lowercase letters, numbers, and hyphens. This becomes part of the URL.",
    )

    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("🚀 Deploy Now", key=f"deploy_now_{studio_id}", type="primary", use_container_width=True):
            clean_name = (api_name or "").strip().lower().replace(" ", "-")
            if not clean_name:
                st.warning("Please enter a name for the API endpoint.")
            else:
                with st.spinner("Deploying…"):
                    res = create_deployment(studio_id, clean_name)
                if res:
                    st.success(f"✅ API **{clean_name}** deployed successfully!")
                    st.code(
                        f"POST http://127.0.0.1:8001{res['endpoint_url']}\n"
                        f"X-API-Key: {res['api_key']}",
                        language="bash",
                    )
    with c2:
        if st.button("Close", key=f"close_dep_dialog_{studio_id}", use_container_width=True):
            st.session_state["_show_deploy_dialog"] = False
            st.rerun()


# ── Toolbar — Back | (spacer) | Deploy | Run ─────────────────────────────────
tb_back, _, tb_deploy, tb_run = st.columns([1, 4.8, 1.7, 1])
with tb_back:
    if st.button("← Back", key="back_btn"):
        st.session_state.current_studio_id = None
        st.rerun()
with tb_deploy:
    if st.button("🚀 Deploy as API", key="open_deploy_modal_btn", use_container_width=True):
        st.session_state["_show_deploy_dialog"] = True
        st.rerun()
with tb_run:
    if st.button("▶ Run", key="run_btn", type="primary", use_container_width=True):
        st.session_state["_trigger_run"] = True

if st.session_state.get("_show_deploy_dialog", False):
    deploy_api_dialog()

# ── Load data ─────────────────────────────────────────────────────────────────
prompts = get_prompts(studio_id)
docs    = get_documents(studio_id)

sel_doc_id = st.session_state.get(f"sel_doc_{studio_id}")

# ── Keep extraction result in sync with selected document ─────────────────────
# Result payload is displayed at studio scope, so we must refresh it whenever
# selected document changes to avoid showing stale data from another document.
doc_sync_key = f"_last_loaded_doc_{studio_id}"
last_loaded_doc = st.session_state.get(doc_sync_key)
if sel_doc_id:
    if last_loaded_doc != sel_doc_id:
        persisted = get_extraction_result(studio_id, sel_doc_id)
        st.session_state[f"last_ex_{studio_id}"] = persisted or {}
        st.session_state[doc_sync_key] = sel_doc_id
elif last_loaded_doc is not None:
    st.session_state[f"last_ex_{studio_id}"] = {}
    st.session_state.pop(doc_sync_key, None)

# ── Handle extraction run ─────────────────────────────────────────────────────
if st.session_state.pop("_trigger_run", False):
    if not sel_doc_id:
        st.warning("⚠️ Select a document first using **Manage Documents** on the right.")
    elif not prompts:
        st.warning("⚠️ Add at least one field before running.")
    else:
        with st.spinner("🔍 Extracting fields from PDF…"):
            result = run_extraction(studio_id, sel_doc_id)
        if result:
            st.session_state[f"last_ex_{studio_id}"] = result
            st.success("✅ Extraction complete!")
            st.rerun()
        else:
            st.error("Extraction failed. Check backend logs.")

# ── Grab last extraction ──────────────────────────────────────────────────────
last_ex   = st.session_state.get(f"last_ex_{studio_id}", {})
extracted = last_ex.get("extracted_fields", {}) if last_ex else {}
usage     = last_ex.get("usage", {}) if last_ex else {}
n_fields  = max(len(prompts), 1)

prompt_tok = usage.get("prompt_tokens", 0) if usage else 0
comp_tok   = usage.get("completion_tokens", 0) if usage else 0
total_tok  = usage.get("total_tokens", 0) if usage else 0

per_tok    = round(total_tok / n_fields) if total_tok else 0
total_cost = (prompt_tok * 5.0 + comp_tok * 15.0) / 1_000_000
per_cost   = total_cost / n_fields

# Sync editable state when prompt list changes
pfp = tuple((p["id"], p["field_name"], p["prompt_text"]) for p in prompts)
if st.session_state.get("_prompts_fp") != pfp:
    st.session_state["_prompts_fp"] = pfp
    for p in prompts:
        st.session_state[f"ef_{p['id']}"] = p["field_name"]
        st.session_state[f"et_{p['id']}"] = p["prompt_text"]

# ══════════════════════════════════════════════════════════════════════════════
# TWO-COLUMN LAYOUT
# ══════════════════════════════════════════════════════════════════════════════
left, right = st.columns([1.35, 1.65])

# ─────────────────────────────────────────── LEFT ────────────────────────────
with left:

    # ── Left tab switcher ─────────────────────────────────────────────────────
    _ltab = st.session_state.get("_ltab", "parser")
    lc1, lc2 = st.columns(2)
    with lc1:
        if st.button("Document Parser", key="ltab_parser",
                     type="primary" if _ltab == "parser" else "secondary",
                     use_container_width=True):
            st.session_state["_ltab"] = "parser"
            st.rerun()
    with lc2:
        if st.button("Combined Output", key="ltab_combined",
                     type="primary" if _ltab == "combined" else "secondary",
                     use_container_width=True):
            st.session_state["_ltab"] = "combined"
            st.rerun()

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # DOCUMENT PARSER tab
    # ══════════════════════════════════════════════════════════════════════════
    if _ltab == "parser":

        if not prompts:
            st.info("No fields yet — add a prompt below.")

        for p in prompts:
            pid        = p["id"]
            is_editing = st.session_state.get(f"editing_p_{pid}", False)
            field_val  = extracted.get(p["field_name"])

            with st.container(border=True):

                # ── Card header: dark band (name) + icon buttons side-by-side ──
                hdr_col, btn_col = st.columns([5, 1])
                with hdr_col:
                    st.markdown(
                        f"<div class='field-card-header'>"
                        f"<span class='field-name'>{html.escape(p['field_name'])}</span>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                with btn_col:
                    ic1, ic2 = st.columns(2)
                    with ic1:
                        if st.button("✏️", key=f"edit_p_{pid}", help="Edit"):
                            entering = not is_editing
                            st.session_state[f"editing_p_{pid}"] = entering
                            if entering:
                                # Pre-seed with current values so inputs are never blank
                                st.session_state[f"ef_{pid}"] = p["field_name"]
                                st.session_state[f"et_{pid}"] = p["prompt_text"]
                            st.rerun()
                    with ic2:
                        if st.button("🗑️", key=f"del_p_{pid}", help="Delete"):
                            st.session_state[f"confirm_del_p_{pid}"] = True
                            st.rerun()

                # ── Confirm delete ────────────────────────────────────────────
                if st.session_state.get(f"confirm_del_p_{pid}"):
                    st.warning(f"Delete **{p['field_name']}**? This cannot be undone.")
                    cd1, cd2 = st.columns(2)
                    with cd1:
                        if st.button("Yes, delete", key=f"cdy_{pid}",
                                     type="primary", use_container_width=True):
                            delete_prompt(pid)
                            for k in (f"confirm_del_p_{pid}", "_prompts_fp"):
                                st.session_state.pop(k, None)
                            st.rerun()
                    with cd2:
                        if st.button("Cancel", key=f"cdn_{pid}", use_container_width=True):
                            st.session_state.pop(f"confirm_del_p_{pid}", None)
                            st.rerun()

                # ── Inline edit form ──────────────────────────────────────────
                if is_editing:
                    st.text_input(
                        "Field name", key=f"ef_{pid}",
                        label_visibility="collapsed", placeholder="Field name",
                    )
                    st.text_area(
                        "Prompt", key=f"et_{pid}", height=90,
                        label_visibility="collapsed", placeholder="Prompt instruction",
                    )
                    sv1, sv2 = st.columns(2)
                    with sv1:
                        if st.button("Save", key=f"sv_{pid}",
                                     type="primary", use_container_width=True):
                            new_fn = (st.session_state.get(f"ef_{pid}") or "").strip()
                            new_pt = st.session_state.get(f"et_{pid}") or ""
                            if new_fn:
                                update_prompt(pid, field_name=new_fn, prompt_text=new_pt)
                                st.session_state[f"editing_p_{pid}"] = False
                                st.session_state.pop("_prompts_fp", None)
                                st.rerun()
                            else:
                                st.warning("Field name cannot be empty.")
                    with sv2:
                        if st.button("Cancel", key=f"cl_{pid}", use_container_width=True):
                            st.session_state[f"editing_p_{pid}"] = False
                            st.rerun()

                else:
                    # ── Prompt text (read mode) ───────────────────────────────
                    st.markdown(
                        f"<p class='field-prompt'>{html.escape(p['prompt_text'])}</p>",
                        unsafe_allow_html=True,
                    )

                # ── Extracted value ───────────────────────────────────────────
                if field_val is not None and str(field_val).strip():
                    st.markdown(
                        f"<div class='field-value'>{html.escape(str(field_val))}</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        "<div class='field-value-empty'>Not yet extracted</div>",
                        unsafe_allow_html=True,
                    )

                # ── Token info (subtle, no enabled badge) ─────────────────────
                if per_tok:
                    st.markdown(
                        f"<span class='token-info'>Tokens: ~{per_tok} (~${per_cost:.4f})</span>",
                        unsafe_allow_html=True,
                    )

        # ── Add Prompt button + inline form ───────────────────────────────────
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        _show_add = st.session_state.get("_show_add_prompt", False)

        if st.button(
            "＋ Add Prompt" if not _show_add else "✕ Cancel",
            key="toggle_add_prompt",
            type="primary" if not _show_add else "secondary",
            use_container_width=True,
        ):
            st.session_state["_show_add_prompt"] = not _show_add
            # Clear any partial input when closing
            if _show_add:
                st.session_state.pop(f"np_field_{studio_id}", None)
                st.session_state.pop(f"np_text_{studio_id}", None)
            st.rerun()

        if st.session_state.get("_show_add_prompt", False):
            st.markdown("<div class='add-prompt-panel'>", unsafe_allow_html=True)
            kf = f"np_field_{studio_id}"
            kt = f"np_text_{studio_id}"

            st.text_input(
                "Field name",
                key=kf,
                placeholder="e.g. Customer_Name",
                label_visibility="visible",
            )
            st.text_area(
                "Prompt instruction",
                key=kt,
                height=90,
                placeholder="Describe what to extract…",
                label_visibility="visible",
            )

            ap1, ap2 = st.columns(2)
            with ap1:
                if st.button("✔ Save Prompt", key="save_new_prompt",
                             type="primary", use_container_width=True):
                    fn = (st.session_state.get(kf) or "").strip()
                    pt = (st.session_state.get(kt) or "").strip()
                    if not fn:
                        st.warning("Field name cannot be empty.")
                    elif not pt:
                        st.warning("Prompt instruction cannot be empty.")
                    else:
                        res = create_prompt(studio_id, fn, pt)
                        if res:
                            st.session_state.pop(kf, None)
                            st.session_state.pop(kt, None)
                            st.session_state.pop("_prompts_fp", None)
                            st.session_state["_show_add_prompt"] = False
                            st.rerun()
            with ap2:
                if st.button("Cancel", key="cancel_new_prompt", use_container_width=True):
                    st.session_state["_show_add_prompt"] = False
                    st.session_state.pop(kf, None)
                    st.session_state.pop(kt, None)
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # COMBINED OUTPUT tab
    # ══════════════════════════════════════════════════════════════════════════
    else:
        if not last_ex:
            st.info("Run extraction first to see combined output.")
        else:
            raw_text = last_ex.get("raw_output") or json.dumps(
                last_ex.get("extracted_fields", {}), indent=2, ensure_ascii=False
            )
            st.markdown(
                f'<div class="raw-output">{html.escape(raw_text)}</div>',
                unsafe_allow_html=True,
            )

            # Usage metrics
            if usage:
                st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Prompt tokens",     usage.get("prompt_tokens", 0))
                m2.metric("Completion tokens",  usage.get("completion_tokens", 0))
                m3.metric("Total tokens",        usage.get("total_tokens", 0))
                m4.metric("Est. Cost",           f"${total_cost:.4f}")

            # Output file path
            out_path = last_ex.get("output_path")
            if out_path:
                st.caption(f"Saved to: `{out_path}`")


# ─────────────────────────────────────────── RIGHT ───────────────────────────
with right:

    # ── Right tab + Manage Documents button ───────────────────────────────────
    rc1, rc2 = st.columns([1, 1.4])
    with rc1:
        # Only PDF View tab now (Raw View removed)
        st.markdown(
            "<div style='padding:5px 0;font-weight:600;color:#4f46e5;font-size:13px;'>"
            "📄 PDF View</div>",
            unsafe_allow_html=True,
        )
    with rc2:
        if st.button("📂 Manage Documents", key="toggle_docs", use_container_width=True):
            st.session_state["_show_docs"] = not st.session_state.get("_show_docs", False)
            st.rerun()

    # ── Manage Documents panel ────────────────────────────────────────────────
    if st.session_state.get("_show_docs", False):
        with st.container(border=True):
            st.markdown("**Upload a PDF**")
            uploaded = st.file_uploader("PDF file", type=["pdf"], key="doc_uploader",
                                        label_visibility="collapsed")
            if uploaded:
                with st.spinner("Uploading…"):
                    res = upload_document(studio_id, uploaded)
                    if res:
                        st.success(f"✅ {uploaded.name}")
                        docs = get_documents(studio_id)

            if docs:
                st.markdown("**Select document for extraction & preview:**")
                for d in docs:
                    is_sel = sel_doc_id == d["id"]
                    prefix = "✅ " if is_sel else "📄 "
                    if st.button(f"{prefix}{d['filename']}", key=f"sdoc_{d['id']}",
                                 use_container_width=True,
                                 type="primary" if is_sel else "secondary"):
                        st.session_state[f"sel_doc_{studio_id}"] = d["id"]
                        st.rerun()
            else:
                st.info("No PDFs uploaded yet.")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Re-read sel_doc_id in case it changed via Manage Documents
    sel_doc_id = st.session_state.get(f"sel_doc_{studio_id}")

    # ══════════════════════════════════════════════════════════════════════════
    # PDF VIEW
    # ══════════════════════════════════════════════════════════════════════════
    if sel_doc_id:
        pdf_url = f"{API_BASE}/documents/file/{sel_doc_id}"
        st.markdown(
            f'<div class="pdf-wrap">'
            f'<iframe src="{pdf_url}#toolbar=1&view=FitH" '
            f'width="100%" height="720px" '
            f'style="border:none;display:block;" '
            f'type="application/pdf">'
            f'<p style="padding:16px">Your browser cannot display PDFs inline. '
            f'<a href="{pdf_url}" target="_blank">Open PDF ↗</a></p>'
            f'</iframe>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.caption(f"[Open in new tab ↗]({pdf_url})")
    else:
        st.markdown(
            '<div style="height:720px;display:flex;align-items:center;justify-content:center;'
            'border:2px dashed #c4b5fd;border-radius:8px;color:#6366f1;font-size:0.9rem">'
            '📂&nbsp; Click <strong>Manage Documents</strong> to select a PDF'
            '</div>',
            unsafe_allow_html=True,
        )
