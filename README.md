## MediViewAI – Multimodal Radiology & Report Analyzer

Production-ready scaffold for a multimodal clinical imaging assistant. Backed by FastAPI + PyTorch/Transformers, PostgreSQL, S3-compatible object storage, and a Next.js + Tailwind front-end. Ships with Docker Compose and baseline Kubernetes manifests (coming next step).

### Phase 1 Deliverable (Completed)
- Secure upload flow using presigned URLs for object storage (MinIO/S3)
- Direct client upload to MinIO (no backend proxying of file bytes)
- Async analysis job orchestration (enqueue job, process in background)
- Job status polling endpoint to track progress until completion
- ML is intentionally stubbed; the goal here is a reliable end-to-end data and job pipeline

### Phase 2 Deliverable (Completed)
- Added Redis + Celery worker for background jobs
- New endpoints:
  - `POST /api/uploads/presign` – presigned URL for direct client upload
  - `POST /api/analyze/start` – enqueue analysis job, returns `job_id`
  - `GET /api/jobs/{job_id}` – poll job status/result
- Frontend updated to: presign → direct upload → start job → poll status
- `Job` table persisted in Postgres; stubs simulate progress/results

### Features in this scaffold
- Backend FastAPI with modular routers for: health, analyze endpoints (legacy single-call and async job), and stubs for VQA, DocQA, Summarization
- Hugging Face integration layer with lazy pipelines (works offline by stubbing until models configured)
- SQLAlchemy models for `Study`, `Report`, `Finding`, `Job` with auto `create_all` on startup
- S3 (MinIO) storage wrapper for image/report artifacts + presigned uploads
- Redis + Celery worker for async jobs
- Next.js (App Router) + Tailwind UI starter
- Dockerfiles + docker-compose (Postgres + MinIO + app services)
- `.env.example` to configure everything

### Quick start
1) Copy envs
```bash
cp .env.example .env
```

2) Start stack
```bash
docker compose up -d --build
```

3) Open services
- Backend: http://localhost:8000/docs
- Frontend: http://localhost:3000
- MinIO Console: http://localhost:9001 (user: `MINIO_ROOT_USER`, pass: `MINIO_ROOT_PASSWORD`)

### Backend local dev (without Docker)
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir backend
```

### Endpoints
- `GET /health` – readiness
- `POST /api/analyze` – legacy single-call analyze (multipart)
- `POST /api/uploads/presign` – presigned PUT/POST payload for direct S3/MinIO upload
- `POST /api/analyze/start` – enqueue analysis job from uploaded S3 key
- `GET /api/jobs/{job_id}` – poll job status and result

### Configure models (optional now)
Populate model names/tokens in `.env` to enable real inference via Hugging Face:
- `HF_API_TOKEN`, `HF_IMG_CLS_MODEL`, `HF_IMG_SEG_MODEL`, `HF_VQA_MODEL`, `HF_DQA_MODEL`, `HF_SUMM_MODEL`

### Notes
- This scaffold avoids heavyweight model loads until you set envs. It will return deterministic stubbed outputs otherwise, so the UI and pipeline wiring can be built and tested first.

### Verify Phase 2 (manual test)
1) Presign
```
curl -s -X POST http://localhost:8000/api/uploads/presign \
  -H 'Content-Type: application/json' \
  -d '{"filename":"test.png","content_type":"image/png","use_post":false}'
```
2) Upload (PUT the file to returned URL)
```
curl -X PUT -H 'Content-Type: image/png' --data-binary @/path/to/test.png "<presigned_url>"
```
3) Start job
```
curl -s -X POST http://localhost:8000/api/analyze/start \
  -H 'Content-Type: application/json' \
  -d '{"s3_key":"<key_from_presign>","report_text":"optional"}'
```
4) Poll status
```
curl -s http://localhost:8000/api/jobs/<job_id>
```


### Roadmap
- Phase 3: Real model integrations (HF/torch) for classification/segmentation, VQA/DocQA, summarization; streaming job progress via SSE/WebSocket; persist findings
- Phase 4: Study viewer overlays, feedback/annotation, audit logging, auth/roles
- Phase 5: GPU model service, caching, observability, and evaluation gates

### Next Phase Plan (Phase 3)
- Models
  - Enable real HF pipelines via envs, add CPU-safe defaults
  - Implement image classification + (optional) basic detection/segmentation
- Pipeline
  - Refactor analyze task to use a pluggable Pipeline with stages
  - Persist `Finding` rows with model names/versions and confidences
- Streaming progress
  - SSE endpoint `/api/jobs/{id}/events` to stream step/progress
  - Frontend subscribe and live-update job state
- Safety & logging
  - Request ID middleware + structured logs
  - Mask PHI in logs, opt-in verbose traces by env

### Phase 3 To-Do (brief)
- [ ] Implement `Pipeline` and first two stages (classify, summarize)
- [ ] Wire HF models via envs; add graceful fallback to stubs
- [ ] Persist findings to DB and return in job result
- [ ] Add SSE events for job progress; frontend consumption
- [ ] Basic API key auth for job endpoints


