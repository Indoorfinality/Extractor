from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple, Any

from openai import OpenAI

from ..config import OPENAI_API_KEY


def _safe_usage(usage_obj: Any) -> Dict[str, int]:
    if not usage_obj:
        return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    return {
        "prompt_tokens": int(getattr(usage_obj, "input_tokens", 0) or 0),
        "completion_tokens": int(getattr(usage_obj, "output_tokens", 0) or 0),
        "total_tokens": int(getattr(usage_obj, "total_tokens", 0) or 0),
    }


def extract_fields_from_pdf(
    pdf_path: str | Path,
    field_prompts: List[Tuple[str, str]],
    *,
    model: str = "gpt-5",
    max_output_tokens: int = 8000,
) -> tuple[Dict[str, Any], Dict[str, int], str | None]:
    pdf_path = Path(pdf_path)

    if not pdf_path.is_file() or pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Invalid or missing PDF: {pdf_path}")

    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set")

    field_lines: list[str] = []
    for field_name, prompt_text in field_prompts:
        prompt_text = (prompt_text or "").strip()
        if prompt_text:
            field_lines.append(f"- {field_name}: {prompt_text}")

    fields_instruction = "\n".join(field_lines) if field_lines else "(No fields defined)"

    system_prompt = f"""
You are an expert at extracting structured data from invoices, purchase orders, receipts, quotations and similar documents.

Strict rules:
- Extract ONLY information clearly visible in the document
- Never guess or infer values
- Return "" (empty string) for missing fields
- Dates: normalize to YYYY-MM-DD
- Monetary amounts: keep currency symbol if present
- Line items: return array of objects (extract EVERY row)
- Addresses: single line, comma separated
- Output ONLY valid JSON (no markdown, no explanation)

Fields to extract:
{fields_instruction}
""".strip()

    client = OpenAI(api_key=OPENAI_API_KEY)

    openai_file_id: str | None = None
    try:
        with open(pdf_path, "rb") as f:
            file_response = client.files.create(
                file=f,
                purpose="user_data",
            )
        openai_file_id = file_response.id

        response = client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "Extract all fields from this document and return ONLY valid JSON.",
                        },
                        {"type": "input_file", "file_id": openai_file_id},
                    ],
                },
            ],
            max_output_tokens=max_output_tokens,
        )

        raw_output = (response.output_text or "").strip()

        extracted_fields: Dict[str, Any]
        try:
            extracted_fields = json.loads(raw_output)
        except json.JSONDecodeError:
            extracted_fields = {
                "error": "Model returned invalid JSON",
                "raw": raw_output,
            }

        usage = _safe_usage(getattr(response, "usage", None))

        expected_keys = [name for name, _ in field_prompts]
        if isinstance(extracted_fields, dict) and expected_keys:
            normalized: Dict[str, Any] = {}
            for k in expected_keys:
                v = extracted_fields.get(k, "")
                normalized[k] = v if v is not None else ""
            return normalized, usage, raw_output

        return extracted_fields, usage, raw_output

    finally:
        if openai_file_id:
            try:
                client.files.delete(openai_file_id)
            except Exception:
                pass