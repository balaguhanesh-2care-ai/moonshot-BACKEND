# Single flow: Audio → Scribe → FHIR → EMR

Base URL (hosted): **https://moonshot-backend-seven.vercel.app**

## Endpoint: `POST /api/pipeline/audio-to-emr`

Runs in one call: upload Scribe audio → transcribe → convert to FHIR → store in Supabase → push to EkaCare EMR.

### Headers

| Header     | Required | Description                          |
|-----------|----------|--------------------------------------|
| `X-Pt-Id` | **Yes**  | Eka Care patient OID (from test-patient) |
| Eka auth  | **Yes** (or set in .env) | Either `X-Eka-Api-Token` or `X-Eka-Client-Id` + `X-Eka-Client-Secret`; optional `X-Eka-Base-Url`. See `EKA_PARAMS.md`. |
| `Content-Type` | Yes* | `application/json` for JSON body, or `multipart/form-data` for file upload |

\* Omit for multipart; browser/client sets it with boundary.

### Query (optional)

| Param             | Default | Description                    |
|-------------------|---------|--------------------------------|
| `document_type`   | `ps`    | EkaCare document type          |
| `include_metadata`| `false` | Send FHIR as metadata (set `true` if EkaCare supports it) |

### Body (choose one)

**Option A – Audio URL (JSON)**

```json
{
  "audio_url": "https://example.com/path/to/recording.mp3"
}
```

**Option B – File upload (multipart/form-data)**

- One or more form fields whose value is a file (e.g. `file`, `audio`, or any name).  
- The first file(s) with readable content are used as audio.

### Response (200)

Returns intermediate steps and final results in pipeline order:

```json
{
  "scribe": { ... },
  "bundle": { ... },
  "db": {
    "id": "uuid-of-supabase-row",
    "created_at": "2026-01-29T..."
  },
  "emr": {
    "document_id": "eka-document-uuid",
    "batch_response": [...]
  }
}
```

- **scribe** – EkaScribe transcription output (JSON) before FHIR conversion.
- **bundle** – FHIR Bundle (Patient, Encounter, Conditions, etc.) before DB/EMR.
- **db** – Supabase row id and created_at.
- **emr** – EkaCare Records upload result (document_id, batch_response).

### Example: cURL (audio URL)

```bash
curl -X POST "https://moonshot-backend-seven.vercel.app/api/pipeline/audio-to-emr?document_type=ps&include_metadata=false" \
  -H "Content-Type: application/json" \
  -H "X-Pt-Id: YOUR_EKA_PATIENT_OID" \
  -d '{"audio_url":"https://example.com/recording.mp3"}'
```

### Example: cURL (file upload)

```bash
curl -X POST "https://moonshot-backend-seven.vercel.app/api/pipeline/audio-to-emr" \
  -H "X-Pt-Id: YOUR_EKA_PATIENT_OID" \
  -F "file=@/path/to/recording.mp3"
```

### Example: PowerShell (audio URL)

```powershell
$body = '{"audio_url":"https://example.com/recording.mp3"}'
Invoke-RestMethod -Uri "https://moonshot-backend-seven.vercel.app/api/pipeline/audio-to-emr" -Method POST -ContentType "application/json" -Headers @{ "X-Pt-Id" = "YOUR_EKA_PATIENT_OID" } -Body $body
```

### Getting `X-Pt-Id` (Eka patient OID)

Create a test patient (or use an existing Eka patient OID):

```bash
curl -X POST "https://moonshot-backend-seven.vercel.app/api/eka-abdm/test-patient" \
  -H "Content-Type: application/json"
```

Response includes `oid` — use that value as `X-Pt-Id` in the single-flow request.
