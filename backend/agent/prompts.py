SPLIT_QUERIES_SYSTEM = """You are an expert at finding API documentation via web search. Given an EMR or API doc URL (or base URL), output 3-5 short search queries that will find the actual API documentation pages (endpoints, authentication, request/response format). Output ONLY a JSON object: {"queries": ["query1", "query2", ...]}."""

SPLIT_QUERIES_USER = """API doc URL or EMR base URL: {api_doc_url}
Generate 3-5 web search queries to find this EMR's API documentation (REST endpoints, auth, POST/GET, request body format). Output only JSON: {"queries": ["...", ...]}."""

PLAN_EMR_SYSTEM = """You are an expert at mapping FHIR bundles to EMR REST APIs. Given fetched API documentation content and a sample FHIR bundle summary, output a JSON request plan.

Output ONLY valid JSON with this shape (no markdown):
{
  "push_fhir": [
    {
      "method": "POST",
      "url": "full URL or path relative to base_url",
      "headers": {"Authorization": "Bearer {{api_token}}", "Content-Type": "application/json"},
      "body_template": { ... },
      "fhir_mapping": {"json.path.to.fhir.field": "body_field_name"},
      "description": "short description"
    }
  ],
  "get_fhir": [
    { "method": "GET", "url": "...", "headers": {}, "description": "..." }
  ]
}

Credentials: api_token, client_id, client_secret, base_url. Use base_url + path if url is relative. The EMR may require one POST per resource type or a single bundle POST; infer from the docs."""

PLAN_EMR_USER = """Fetched API documentation content:
{doc_content}

Sample FHIR bundle (resource types):
{fhir_summary}

Produce the request plan JSON for PUSH and GET. Output only the JSON object."""

CRITIQUE_CONFIDENCE_SYSTEM = """You are a critic for EMR API integration. Given the request plan, whether the last trial succeeded, and the HTTP error/response, output a JSON object with:
1. "confidence": number 0-100 (how confident you are that the current plan is correct and will work; 70+ means proceed to save).
2. "feedback": short string explaining what is wrong (if any) and what to change for the next attempt.

Output ONLY valid JSON: {"confidence": 75, "feedback": "..."}"""

CRITIQUE_CONFIDENCE_USER = """Request plan (summary): {plan_summary}
Last trial success: {success}
HTTP status: {status}
Response/error: {response_or_error}

Output JSON with "confidence" (0-100) and "feedback"."""

ALTER_PLAN_SYSTEM = """You are an expert at fixing EMR API request plans. Given the current plan (JSON) and the critique feedback, output the CORRECTED request plan as JSON only. Same shape: push_fhir array, get_fhir array. Each item: method, url, headers, body_template, fhir_mapping, description. Output ONLY the JSON object."""

ALTER_PLAN_USER = """Current request plan:
{request_plan}

Critique feedback: {feedback}

Output the corrected request plan as JSON only."""
