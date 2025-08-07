## MediViewAI – Multimodal Radiology & Report Analyzer

Production-ready scaffold for a multimodal clinical imaging assistant. Backed by FastAPI + PyTorch/Transformers, PostgreSQL, S3-compatible object storage, and a Next.js + Tailwind front-end. Ships with Docker Compose and baseline Kubernetes manifests (coming next step).

### Features in this scaffold
- Backend FastAPI with modular routers for: health, unified analyze endpoint (image + text), and stubs for VQA, DocQA, Summarization
- Hugging Face integration layer with lazy pipelines (works offline by stubbing until models configured)
- SQLAlchemy models for `Study`, `Report`, `Finding` with auto `create_all` on startup
- S3 (MinIO) storage wrapper for image/report artifacts
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
- `POST /api/analyze` – multipart form with `image` (file) and optional `report_text`, returns structured findings (stub) and summary

### Configure models (optional now)
Populate model names/tokens in `.env` to enable real inference via Hugging Face:
- `HF_API_TOKEN`, `HF_IMG_CLS_MODEL`, `HF_IMG_SEG_MODEL`, `HF_VQA_MODEL`, `HF_DQA_MODEL`, `HF_SUMM_MODEL`

### Notes
- This scaffold avoids heavyweight model loads until you set envs. It will return deterministic stubbed outputs otherwise, so the UI and pipeline wiring can be built and tested first.


