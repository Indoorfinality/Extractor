import requests
import streamlit as st

API_BASE = "http://127.0.0.1:8001/api"  # change if backend port/host different


def handle_response(r):
    if r.status_code >= 400:
        try:
            msg = r.json().get("detail", r.text or "Unknown error")
        except:
            msg = r.text or "Unknown error"
        st.error(f"API error {r.status_code}: {msg}")
        return None
    try:
        return r.json()
    except:
        return r.text


def get_studios():
    r = requests.get(f"{API_BASE}/studios/")
    return handle_response(r) or []


def create_studio(name: str, description: str = ""):
    r = requests.post(f"{API_BASE}/studios/", json={"name": name, "description": description})
    return handle_response(r)


def update_studio(studio_id: int, *, name: str | None = None, description: str | None = None):
    payload = {}
    if name is not None:
        payload["name"] = name
    if description is not None:
        payload["description"] = description
    if not payload:
        return None
    r = requests.put(f"{API_BASE}/studios/{studio_id}", json=payload)
    return handle_response(r)


def delete_studio(studio_id: int):
    r = requests.delete(f"{API_BASE}/studios/{studio_id}")
    if r.status_code == 204:
        return True
    return handle_response(r)


def get_prompts(studio_id: int):
    r = requests.get(f"{API_BASE}/prompts/{studio_id}")
    return handle_response(r) or []


def create_prompt(studio_id: int, field_name: str, prompt_text: str):
    payload = {
        "studio_id": studio_id,
        "field_name": field_name,
        "prompt_text": prompt_text
    }
    r = requests.post(f"{API_BASE}/prompts/", json=payload)
    return handle_response(r)


def update_prompt(prompt_id: int, *, field_name: str | None = None, prompt_text: str | None = None):
    payload = {}
    if field_name is not None:
        payload["field_name"] = field_name
    if prompt_text is not None:
        payload["prompt_text"] = prompt_text
    if not payload:
        return None
    r = requests.put(f"{API_BASE}/prompts/{prompt_id}", json=payload)
    return handle_response(r)


def upload_document(studio_id: int, file):
    files = {"file": (file.name, file.getvalue(), "application/pdf")}
    r = requests.post(
        f"{API_BASE}/documents/upload",
        params={"studio_id": studio_id},
        files=files,
    )
    return handle_response(r)


def get_documents(studio_id: int):
    r = requests.get(f"{API_BASE}/documents/{studio_id}")
    return handle_response(r) or []


def delete_prompt(prompt_id: int):
    r = requests.delete(f"{API_BASE}/prompts/{prompt_id}")
    if r.status_code == 204:
        return True
    return handle_response(r)


def run_extraction(studio_id: int, document_id: int):
    r = requests.post(
        f"{API_BASE}/extraction/run",
        json={"studio_id": studio_id, "document_id": document_id},
    )
    return handle_response(r)


def get_latest_extraction(studio_id: int, document_id: int | None = None):
    params = {"studio_id": studio_id}
    if document_id is not None:
        params["document_id"] = document_id
    r = requests.get(f"{API_BASE}/extraction/latest", params=params)
    return handle_response(r)


def get_extraction_result(studio_id: int, document_id: int):
    r = requests.get(
        f"{API_BASE}/extraction/result",
        params={"studio_id": studio_id, "document_id": document_id},
    )
    if r.status_code == 404:
        return None
    return handle_response(r)


def get_document_file_url(doc_id: int) -> str:
    return f"{API_BASE}/documents/file/{doc_id}"



def create_deployment(studio_id: int, name: str):
    r = requests.post(
        f"{API_BASE}/deployments/",
        params={"studio_id": studio_id},
        json={"name": name},
    )
    return handle_response(r)


def get_deployments(studio_id: int):
    """Get all deployments (active + inactive) for a specific studio."""
    r = requests.get(f"{API_BASE}/deployments/{studio_id}")
    return handle_response(r) or []


def get_all_deployments():
    """Get deployments across ALL studios (for the global API Deployments page)."""
    r = requests.get(f"{API_BASE}/deployments/")
    return handle_response(r) or []


def toggle_deployment(deployment_id: int, is_active: bool):
    r = requests.patch(
        f"{API_BASE}/deployments/{deployment_id}/toggle",
        json={"is_active": is_active},
    )
    return handle_response(r)


def delete_deployment(deployment_id: int):
    r = requests.delete(f"{API_BASE}/deployments/{deployment_id}")
    return r.status_code == 204