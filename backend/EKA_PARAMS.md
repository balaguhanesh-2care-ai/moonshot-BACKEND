# EkaCare / EkaScribe – Params and auth (separate keys)

EkaScribe (transcription) and Eka EMR (records, patient, ABDM) use **separate** credentials.

## Pipeline: client-only auth

For **`POST /api/pipeline/audio-to-fhir`** and **`POST /api/pipeline/audio-to-emr`**, the backend **does not use server `.env`** for Scribe or EMR. All keys come from the client:

- **Scribe:** client reads from its own env (e.g. `EKA_CLIENT_SCRIBE_SECRET`, `EKA_CLIENT_SCRIBE_CLIENT_ID`) and sends headers. Backend requires Scribe credentials in headers; returns **400** if missing.
- **EMR:** client sends values from the EkaCare dialog (e.g. `X-Pt-Id`, `X-Eka-Client-Id`, `X-Eka-Client-Secret` / `X-EkaEmr-Api-Token`). Backend requires EMR credentials in headers; returns **400** if missing.

Backend’s only job for pipeline is to process the request and run the pipeline using the supplied headers.

---

## Server (.env)

Used by **non-pipeline** routes (e.g. `POST /api/ekascribe/transcribe`) and as optional fallback where applicable. **Pipeline routes do not read Eka keys from server .env.**

| Env var | Used for | Fallback |
|---------|----------|----------|
| **EkaScribe (transcription)** | | |
| `EKASCRIBE_API_TOKEN` | Scribe API (upload, init, poll). Same Bearer token as EMR: **long-lived token** or token from **Connect Login** (client_id + client_secret). Per [Eka docs](https://developer.eka.care/api-reference/authorization/getting-started): long-lived token is used in `Authorization: Bearer <<token>>` for all API requests including EkaScribe. | `EKA_API_TOKEN`, `EKA_CLIENT_SCRIBE_SECRET` |
| `EKASCRIBE_CLIENT_ID` | Scribe Connect login | `EKA_CLIENT_ID`, `EKA_CLIENT_SCRIBE_CLIENT_ID` |
| `EKASCRIBE_CLIENT_SECRET` | Scribe Connect login | `EKA_CLIENT_SECRET` |
| `EKASCRIBE_BASE_URL` | Scribe API base | `EKA_BASE_URL` |
| **Eka EMR (records, patient, ABDM)** | | |
| `EKAEMR_API_TOKEN` | EMR API (records, test-patient, etc.) | `EKA_API_TOKEN` |
| `EKAEMR_CLIENT_ID` | EMR Connect login | `EKA_CLIENT_ID` |
| `EKAEMR_CLIENT_SECRET` | EMR Connect login | `EKA_CLIENT_SECRET` |
| `EKAEMR_BASE_URL` | EMR API base | `EKA_BASE_URL` |
| **Legacy (both)** | | |
| `EKA_API_TOKEN` | Used for Scribe and EMR if `EKASCRIBE_*` / `EKAEMR_*` not set | — |
| `EKA_CLIENT_ID`, `EKA_CLIENT_SECRET`, `EKA_BASE_URL` | Same | — |

Server can start without Eka env vars if only pipeline (client-only auth) is used.

**If EkaScribe returns 403:** EkaScribe uses the same long-lived or Connect token as EMR. A 403 on `/v1/file-upload` can be due to: workspace/product not entitled to EkaScribe, [IP whitelisting](https://developer.eka.care/api-reference/health-ai/ekascribe/ip-whitelisting-for-clients), wrong base URL (e.g. `api.dev.eka.care` vs `api.eka.care`), or expired/invalid token. Confirm the token and workspace have EkaScribe access in Eka Console.

---

## Client (headers)

For **pipeline** endpoints, the client **must** send Scribe and (for audio-to-emr) EMR credentials in headers; server does not fall back to `.env`.

### Scribe (transcription)

Used by: `POST /api/pipeline/audio-to-fhir`, and the Scribe step of `POST /api/pipeline/audio-to-emr`.

| Header | Description |
|--------|-------------|
| `X-EkaScribe-Api-Token` | Scribe API token (client: from `EKA_CLIENT_SCRIBE_SECRET`). Required for pipeline. |
| `X-EkaScribe-Client-Id` or `X-Eka-Scribe-Client-Id` | Scribe client id (client: from `EKA_CLIENT_SCRIBE_CLIENT_ID` when set). Optional. |
| `X-EkaScribe-Client-Secret` | Scribe Connect client secret |
| `X-EkaScribe-Base-Url` | Scribe API base (optional) |
| **Legacy** | |
| `X-Eka-Api-Token` | Used for Scribe when `X-EkaScribe-*` not set |
| `X-Eka-Client-Id`, `X-Eka-Client-Secret`, `X-Eka-Base-Url` | Same |

### EMR (records, patient, ABDM)

Used by: `POST /api/eka-abdm/*`, and the EMR push step of `POST /api/pipeline/audio-to-emr`.

| Header | Description |
|--------|-------------|
| `X-EkaEmr-Api-Token` | EMR API token (client: same value as `X-Eka-Client-Secret` from EkaCare dialog). Required for audio-to-emr. |
| `X-EkaEmr-Client-Id` | EMR Connect client id |
| `X-EkaEmr-Client-Secret` | EMR Connect client secret |
| `X-EkaEmr-Base-Url` | EMR API base (optional) |
| **Legacy** | |
| `X-Eka-Api-Token` | Used for EMR when `X-EkaEmr-*` not set |
| `X-Eka-Client-Id`, `X-Eka-Client-Secret`, `X-Eka-Base-Url` | EMR from EkaCare dialog (patient OID, client id, client secret) |

### Patient (for push)

| Header | Required | Description |
|--------|----------|-------------|
| `X-Pt-Id` | Yes for push / audio-to-emr | Eka Care patient OID (e.g. from `POST /api/eka-abdm/test-patient`). |

---

## What to change on the client

1. **No change (backward compatible)**  
   Keep sending `X-Eka-Api-Token` (or `X-Eka-Client-Id` + `X-Eka-Client-Secret`). The server uses them for both Scribe and EMR as before.

2. **Use separate credentials per service**  
   - For **Scribe** (audio-to-fhir, or Scribe part of audio-to-emr): send `X-EkaScribe-Api-Token` or `X-EkaScribe-Client-Id` + `X-EkaScribe-Client-Secret`; optional `X-EkaScribe-Base-Url`.  
   - For **EMR** (test-patient, push-fhir, push-fhir-from-db, or EMR part of audio-to-emr): send `X-EkaEmr-Api-Token` or `X-EkaEmr-Client-Id` + `X-EkaEmr-Client-Secret`; optional `X-EkaEmr-Base-Url`.

3. **Example – audio-to-emr with separate Scribe and EMR auth**
   ```bash
   curl -X POST "http://localhost:8000/api/pipeline/audio-to-emr" \
     -H "Content-Type: application/json" \
     -H "X-Pt-Id: YOUR_PATIENT_OID" \
     -H "X-EkaScribe-Api-Token: YOUR_SCRIBE_TOKEN" \
     -H "X-EkaEmr-Api-Token: YOUR_EMR_TOKEN" \
     -d '{"audio_url":"https://example.com/audio.mp3"}'
   ```

4. **Example – EMR only (test-patient, push-fhir-from-db)**
   ```bash
   curl -X POST "http://localhost:8000/api/eka-abdm/test-patient" \
     -H "X-EkaEmr-Api-Token: YOUR_EMR_TOKEN"
   ```

---

## Endpoints

- **Scribe:** `POST /api/pipeline/audio-to-fhir`; Scribe step of `POST /api/pipeline/audio-to-emr` → use **Scribe** headers (or legacy `X-Eka-*`).
- **EMR:** `POST /api/eka-abdm/test-patient`, `POST /api/eka-abdm/records/push-fhir`, `POST /api/eka-abdm/records/push-fhir-from-db`, `POST /api/eka-abdm/care-context/data/on-push`; EMR step of `POST /api/pipeline/audio-to-emr` → use **EMR** headers (or legacy `X-Eka-*`).
