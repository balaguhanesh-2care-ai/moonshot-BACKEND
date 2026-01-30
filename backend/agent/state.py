from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    api_doc_url: str
    fhir_bundle: dict[str, Any]
    credentials: dict[str, Any] | None
    emr_id: str
    groq_api_key: str | None
    groq_model: str | None
    max_attempts: int
    attempts: int

    search_queries: dict[str, Any]
    doc_search_result: dict[str, Any]
    fetched_docs: dict[str, Any]
    doc_content: str

    request_plan: dict[str, Any]
    last_request: dict[str, Any] | None
    last_response_status: int | None
    last_response_body: str | None
    last_error: str | None
    success: bool

    critique_result: dict[str, Any]
    confidence: float
    critique_feedback: str

    final_mapping: dict[str, Any] | None
    reasoning: str
    alter_notes: str
