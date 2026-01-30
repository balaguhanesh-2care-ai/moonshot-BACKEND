import json
import logging
import re
from typing import Any

from langgraph.graph import END, START, StateGraph
from langchain_groq import ChatGroq

from config import GROQ_API_KEY, GROQ_MODEL
from agent.state import AgentState
from agent.models import SearchQueries, FetchedDocs, EMRMappingResult, RequestSpec
from agent.tools import search_docs, fetch_docs_from_urls
from agent.prompts import SPLIT_QUERIES_SYSTEM, SPLIT_QUERIES_USER, PLAN_EMR_SYSTEM, PLAN_EMR_USER

log = logging.getLogger(__name__)


def _get_llm(api_key: str | None = None, model: str | None = None):
    key = (api_key or GROQ_API_KEY or "").strip()
    if not key:
        raise ValueError("GROQ_API_KEY is required for the mapping agent (set in config or .env)")
    return ChatGroq(
        model=(model or GROQ_MODEL or "llama-3.3-70b-versatile").strip(),
        api_key=key,
        temperature=0.2,
    )


def _parse_json_from_llm(text: str) -> dict[str, Any]:
    text = (text or "").strip()
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if m:
        text = m.group(1).strip()
    return json.loads(text)


def _fhir_summary(bundle: dict[str, Any], max_entries: int = 15) -> str:
    entries = bundle.get("entry") or []
    parts = []
    for i, e in enumerate(entries[:max_entries]):
        r = e.get("resource") or {}
        parts.append(f"  [{i}] {r.get('resourceType', '?')} id={r.get('id', '?')}")
    return "\n".join(parts) if parts else "(empty bundle)"


def split_queries(state: AgentState) -> dict[str, Any]:
    log.info("[agent] node: split_queries (doc URL -> search queries)")
    url = state.get("api_doc_url") or ""
    llm = _get_llm(state.get("groq_api_key"), state.get("groq_model"))
    user = SPLIT_QUERIES_USER.format(api_doc_url=url or "(none – use EMR API docs search)")
    msg = llm.invoke([
        {"role": "system", "content": SPLIT_QUERIES_SYSTEM},
        {"role": "user", "content": user},
    ])
    text = msg.content if hasattr(msg, "content") else str(msg)
    try:
        parsed = _parse_json_from_llm(text)
        queries = parsed.get("queries") or []
    except (json.JSONDecodeError, KeyError):
        queries = [f"{url} API documentation", "EMR REST API endpoints", "FHIR API push"]
    search_queries = SearchQueries(queries=queries)
    log.info("[agent] split_queries -> %d queries: %s", len(queries), queries[:3])
    return {"search_queries": search_queries.model_dump()}


def search_docs_node(state: AgentState) -> dict[str, Any]:
    log.info("[agent] node: search_docs (Tavily/fallback -> top URLs)")
    queries_data = state.get("search_queries") or {}
    queries = queries_data.get("queries") or []
    if not queries:
        queries = ["EMR API documentation", "REST API FHIR endpoints"]
    result = search_docs(queries)
    log.info("[agent] search_docs -> %d results", len(result.results))
    return {"doc_search_result": result.model_dump()}


def fetch_docs_node(state: AgentState) -> dict[str, Any]:
    log.info("[agent] node: fetch_docs (fetch content from URLs)")
    search_data = state.get("doc_search_result") or {}
    results = search_data.get("results") or []
    urls = [r.get("url", "") for r in results if r.get("url")]
    if not urls:
        log.info("[agent] fetch_docs: no URLs, using empty doc_content")
        return {"fetched_docs": FetchedDocs().model_dump(), "doc_content": "(no docs fetched)"}
    fetched = fetch_docs_from_urls(urls)
    parts = []
    for d in fetched.docs:
        parts.append(f"--- URL: {d.url} ---\n{d.content[:15000]}")
    doc_content = "\n\n".join(parts)[:100_000] if parts else "(no content)"
    log.info("[agent] fetch_docs -> %d docs, %d total chars", len(fetched.docs), len(doc_content))
    return {"fetched_docs": fetched.model_dump(), "doc_content": doc_content}


def plan_emr(state: AgentState) -> dict[str, Any]:
    log.info("[agent] node: plan_emr (docs + FHIR -> mapping)")
    doc_content = state.get("doc_content") or ""
    fhir_bundle = state.get("fhir_bundle") or {}
    llm = _get_llm(state.get("groq_api_key"), state.get("groq_model"))
    user = PLAN_EMR_USER.format(
        doc_content=doc_content[:80000],
        fhir_summary=_fhir_summary(fhir_bundle),
    )
    msg = llm.invoke([
        {"role": "system", "content": PLAN_EMR_SYSTEM},
        {"role": "user", "content": user},
    ])
    text = msg.content if hasattr(msg, "content") else str(msg)
    try:
        plan = _parse_json_from_llm(text)
    except json.JSONDecodeError:
        plan = {"push_fhir": [], "get_fhir": []}
    log.info("[agent] plan_emr -> push_fhir=%d get_fhir=%d",
             len(plan.get("push_fhir") or []), len(plan.get("get_fhir") or []))
    return {"request_plan": plan, "reasoning": text[:500]}


def persist_mapping(state: AgentState) -> dict[str, Any]:
    log.info("[agent] node: persist_mapping (save to Supabase)")
    request_plan = state.get("request_plan") or {}
    emr_id = state.get("emr_id") or "default"
    api_doc_url = state.get("api_doc_url")
    push_specs = request_plan.get("push_fhir") or []
    get_specs = request_plan.get("get_fhir") or []
    mapping = EMRMappingResult(
        push_fhir=[RequestSpec.model_validate(s) for s in push_specs],
        get_fhir=[RequestSpec.model_validate(s) for s in get_specs],
    )
    push_fhir_dict = [s.model_dump() for s in mapping.push_fhir]
    get_fhir_dict = [s.model_dump() for s in mapping.get_fhir]
    try:
        from services.supabase_client import upsert_emr_mapping
        upsert_emr_mapping(emr_id, push_fhir_dict, get_fhir_dict, api_doc_url=api_doc_url)
        log.info("[agent] persist_mapping -> saved emr_id=%s", emr_id)
    except Exception as e:
        log.warning("[agent] persist_mapping failed: %s", e)
    return {"final_mapping": mapping.model_dump(), "success": True}


def create_emr_mapping_agent():
    workflow = StateGraph(AgentState)

    workflow.add_node("split_queries", split_queries)
    workflow.add_node("search_docs", search_docs_node)
    workflow.add_node("fetch_docs", fetch_docs_node)
    workflow.add_node("plan_emr", plan_emr)
    workflow.add_node("persist_mapping", persist_mapping)

    workflow.add_edge(START, "split_queries")
    workflow.add_edge("split_queries", "search_docs")
    workflow.add_edge("search_docs", "fetch_docs")
    workflow.add_edge("fetch_docs", "plan_emr")
    workflow.add_edge("plan_emr", "persist_mapping")
    workflow.add_edge("persist_mapping", END)

    return workflow.compile()


def run_emr_mapping_agent(
    api_doc_url: str,
    fhir_bundle: dict[str, Any],
    *,
    emr_id: str = "default",
    groq_api_key: str | None = None,
    groq_model: str | None = None,
) -> dict[str, Any]:
    log.info("[agent] run_emr_mapping_agent emr_id=%s", emr_id)
    graph = create_emr_mapping_agent()
    initial: AgentState = {
        "api_doc_url": api_doc_url,
        "fhir_bundle": fhir_bundle,
        "emr_id": emr_id,
        "groq_api_key": groq_api_key,
        "groq_model": groq_model,
    }
    config = {"recursion_limit": 20}
    result = graph.invoke(initial, config=config)
    log.info("[agent] run_emr_mapping_agent done success=%s", result.get("success"))
    return result


def run_mapping_agent(
    input_data: dict[str, Any] | str,
    *,
    groq_api_key: str | None = None,
    groq_model: str | None = None,
) -> dict[str, Any]:
    if isinstance(input_data, str):
        raise ValueError("EMR mapping agent expects dict with api_doc_url and fhir_bundle")
    data = input_data if isinstance(input_data, dict) else {}
    url = data.get("api_doc_url") or ""
    bundle = data.get("fhir_bundle") or data.get("fhir_bundle_json")
    if not bundle or not isinstance(bundle, dict):
        raise ValueError("fhir_bundle (or first row from Supabase) is required")
    return run_emr_mapping_agent(
        api_doc_url=url,
        fhir_bundle=bundle,
        emr_id=data.get("emr_id", "default"),
        groq_api_key=groq_api_key,
        groq_model=groq_model,
    )
