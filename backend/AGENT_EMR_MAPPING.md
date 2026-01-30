# EMR Mapping Agent (LangGraph Looping Agent)

Looping agent that discovers how to **push** and **get** FHIR for a given EMR from its API docs, then stores the mapping in Supabase so the adapter can reuse it.

## Flow (internal – log with server logger)

The agent **does not call the EMR API**. It only searches the web, reads docs, and produces a mapping from FHIR to the EMR structure, then stores it in the DB.

1. **split_queries** – From `api_doc_url`, LLM outputs 3–5 web search queries to find EMR API docs. Output: **SearchQueries** (Pydantic).
2. **search_docs** – Tavily (or duckduckgo fallback) runs those queries and returns top URLs/snippets. Output: **DocSearchResult** (Pydantic).
3. **fetch_docs** – Fetches content from those URLs. Output: **FetchedDocs** + concatenated **doc_content**.
4. **plan_emr** – LLM uses doc content + FHIR bundle summary to produce the **mapping**: how FHIR data maps to the EMR structure (POST/GET, URLs, params, body shape). Output: **request_plan** (push_fhir / get_fhir).
5. **persist_mapping** – Saves the mapping (Pydantic) to Supabase **emr_mappings** (push_fhir, get_fhir).

All steps log with `log.info("[agent] node: ...")` so you can follow the run in the server logs.

---

## How to trigger the agent

### 1. What you need

**Env (e.g. `.env` in project root or `backend/`):**

- **GROQ_API_KEY** – Required. Get one at [console.groq.com](https://console.groq.com).
- **GROQ_MODEL** – Optional. Default `llama-3.3-70b-versatile`.
- **TAVILY_API_KEY** – Optional. For doc search (Tavily). If unset, falls back to duckduckgo-search.
- **SUPABASE_URL**, **SUPABASE_SERVICE_ROLE_KEY** – Required if you want the agent to persist the mapping (so the adapter can reuse it).

**Supabase:**

- Run `backend/supabase_emr_mappings.sql` in the Supabase SQL editor once to create the `emr_mappings` table.

**Server:**

- Start the backend (e.g. `uvicorn main:app` from repo root with `main.py` that loads the backend, or run from `backend/` and hit the correct host/port).

### 2. Request

- **Method/URL:** `POST /api/agent/mapping`  
  (e.g. `http://localhost:8000/api/agent/mapping` or your deployed base URL + `/api/agent/mapping`.)

- **Headers:** `Content-Type: application/json`

- **Body (JSON):**

| Field             | Required | Description |
|-------------------|----------|-------------|
| **api_doc_url**   | No       | URL of the EMR’s API docs. Used to generate search queries (can be empty). |
| **emr_id**        | No       | Id for this EMR; mapping is stored under this (default `"default"`). |

**Sample bundle:** Fixed – the first row from **fhir_bundles** (column **bundle_json**), ordered by **created_at**. The table must have at least one row.

### 3. Example (cURL)

Sample bundle is always the first row from **fhir_bundles** (bundle_json). Body can be empty `{}` or include optional params.

```bash
curl -X POST "http://localhost:8000/api/agent/mapping" \
  -H "Content-Type: application/json" \
  -d '{"api_doc_url": "https://api.eka.care", "emr_id": "eka"}'
```

### 4. Example (PowerShell)

```powershell
$body = @{ api_doc_url = "https://api.eka.care"; emr_id = "eka" } | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/agent/mapping" -Method POST -ContentType "application/json" -Body $body
```

### 5. Response

- **Success:** Full agent state; includes **final_mapping** with **push_fhir** and **get_fhir** (list of request specs). Same mapping is stored in Supabase under **emr_id**.
- **Failure (e.g. no success within max_attempts):** State with **success: false**, **last_error**, **last_response_body**; no **final_mapping** and nothing new persisted.

---

## Params (reference)

- **api_doc_url** – EMR API documentation URL (fetched and used for reasoning).
- **Sample bundle** – Fixed: first row from **fhir_bundles** (bundle_json), ordered by created_at.
- **credentials** (optional) – `api_token`, `client_id`, `client_secret`, `base_url` for the EMR.
- **emr_id** – Identifier for this EMR; mapping is stored under this id (default `"default"`).
- **max_attempts** – Max trial attempts (default 10).

## Flow (max 10 attempts)

1. **analyze_docs** – Fetches `api_doc_url` and runs a web search for EMR REST API patterns.
2. **reason** – Chain-of-thought: from docs + FHIR summary, produces a request plan (POST/GET structure, URLs, headers, body_template, fhir_mapping).
3. **try_request** – Executes the plan (push_fhir requests); on 4xx/5xx captures status and body.
4. **route** – Success → persist_mapping → END; failure and attempts < max_attempts → critique; else END.
5. **critique** – LLM critiques the last error and request.
6. **alter_request** – LLM updates the request plan from the critique; then loop back to try_request.
7. **persist_mapping** – Saves `push_fhir` and `get_fhir` (list of request specs) to Supabase table `emr_mappings` under `emr_id`.

## Supabase

- Run `backend/supabase_emr_mappings.sql` in the Supabase SQL editor to create the table.
- Table: `emr_mappings` with columns `emr_id` (unique), `api_doc_url`, `push_fhir` (JSONB), `get_fhir` (JSONB).
- **get_emr_mapping(emr_id)** in `services/supabase_client.py` returns `push_fhir` and `get_fhir` so the adapter can use the stored mapping instead of re-running the agent.

## Env / server config

- **GROQ_API_KEY** – Required for the agent (LLM: reason, critique, alter). Set in `.env` or env; read in `config.py` and stored on the server (`app.state.groq_api_key`) in `main.py`.
- **GROQ_MODEL** – Model name (default `llama-3.3-70b-versatile`). Set in `.env` as `GROQ_MODEL`; read in `config.py` and stored on the server (`app.state.groq_model`) in `main.py`.
- **SUPABASE_URL**, **SUPABASE_SERVICE_ROLE_KEY** – For persisting and reading mappings.

## API

- **POST /api/agent/mapping** – Sample bundle = first row from fhir_bundles (bundle_json). Body: optional `api_doc_url`, `credentials`, `emr_id`, `max_attempts`. Returns full agent state including `final_mapping` (push_fhir / get_fhir) on success.
