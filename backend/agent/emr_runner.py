import json
import logging
from typing import Any

import httpx

log = logging.getLogger(__name__)


def _get_path(obj: Any, path: str) -> Any:
    parts = path.replace("]", "").split("[")
    for part in parts:
        segs = part.split(".")
        for seg in segs:
            if not seg:
                continue
            if isinstance(obj, dict):
                obj = obj.get(seg)
            elif isinstance(obj, list) and seg.isdigit():
                obj = obj[int(seg)] if int(seg) < len(obj) else None
            else:
                obj = None
            if obj is None:
                return None
    return obj


def _apply_fhir_mapping(body_template: Any, fhir_mapping: dict[str, str], fhir_bundle: dict[str, Any]) -> Any:
    if not fhir_mapping or body_template is None:
        return body_template
    if isinstance(body_template, dict):
        out = {}
        for k, v in body_template.items():
            if isinstance(v, str) and v.startswith("{{") and v.endswith("}}"):
                path = v[2:-2].strip()
                out[k] = _get_path(fhir_bundle, path)
            else:
                out[k] = _apply_fhir_mapping(v, fhir_mapping, fhir_bundle)
        return out
    if isinstance(body_template, list):
        return [_apply_fhir_mapping(x, fhir_mapping, fhir_bundle) for x in body_template]
    return body_template


def _build_headers(spec: dict[str, Any], credentials: dict[str, Any] | None) -> dict[str, str]:
    headers = dict(spec.get("headers") or {})
    if credentials:
        if credentials.get("api_token"):
            headers["Authorization"] = f"Bearer {credentials['api_token']}"
        if credentials.get("client_id"):
            headers["client-id"] = credentials["client_id"]
    return {k: str(v) for k, v in headers.items()}


def _build_url(spec: dict[str, Any], credentials: dict[str, Any] | None) -> str:
    url = spec.get("url") or ""
    base = (credentials or {}).get("base_url", "").rstrip("/")
    if base and url and not url.startswith("http"):
        url = f"{base}/{url.lstrip('/')}"
    return url


def execute_request_plan(
    request_plan: dict[str, Any],
    fhir_bundle: dict[str, Any],
    credentials: dict[str, Any] | None,
    *,
    execute_get: bool = False,
) -> tuple[bool, int | None, str, str | None]:
    key = "get_fhir" if execute_get else "push_fhir"
    specs = request_plan.get(key) or []
    if not specs:
        return False, None, "", "No request specs in plan"
    last_status = None
    last_body = ""
    last_error = None
    for spec in specs:
        url = _build_url(spec, credentials)
        headers = _build_headers(spec, credentials)
        headers.setdefault("Content-Type", "application/json")
        method = (spec.get("method") or "GET").upper()
        body_template = spec.get("body_template")
        fhir_mapping = spec.get("fhir_mapping") or {}
        body = _apply_fhir_mapping(body_template, fhir_mapping, fhir_bundle) if body_template is not None else None
        try:
            with httpx.Client(timeout=30.0) as client:
                if method == "GET":
                    r = client.get(url, headers=headers)
                elif method == "POST":
                    r = client.post(url, headers=headers, json=body)
                else:
                    r = client.request(method, url, headers=headers, json=body)
            last_status = r.status_code
            last_body = (r.text or "")[:2000]
            if r.status_code >= 400:
                last_error = f"HTTP {r.status_code}: {last_body[:500]}"
                return False, last_status, last_body, last_error
        except Exception as e:
            last_error = str(e)
            return False, None, "", last_error
    return True, last_status, last_body, None
