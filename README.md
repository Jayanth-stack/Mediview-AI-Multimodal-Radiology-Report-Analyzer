## MediViewAI – Multimodal Radiology & Report Analyzer

[![MediViewAI Landing Page](assets/landing-page.png)](assets/landing-page.png)

Production-ready scaffold for a multimodal clinical imaging assistant. Backed by FastAPI, PostgreSQL, S3-compatible object storage, and a Next.js front-end. It ships with Docker Compose for easy setup.

### Features
- **Secure File Uploads**: Utilizes presigned URLs for direct client-to-S3/MinIO uploads, ensuring file bytes don't pass through the backend.
- **Asynchronous Analysis**: Employs Celery and Redis for background job processing, allowing for non-blocking analysis tasks.
- **Pluggable Pipeline**: A decoupled analysis workflow with composable stages (e.g., `classify`, `summarize`, `persist`).
- **Database Persistence**: Uses SQLAlchemy and Postgres to store information about studies, findings, reports, and jobs.
- **Containerized**: Fully containerized with Docker for both development and production environments.
- **Modern Frontend**: A reactive user interface built with Next.js and Tailwind CSS.
- **ML Integration Layer**: A service layer for integrating machine learning models from providers like Hugging Face and Google Gemini.

### Tech Stack

- **Backend**: FastAPI, Python 3.11, Celery
- **Database**: PostgreSQL
- **Cache & Message Broker**: Redis
- **Object Storage**: MinIO (S3 Compatible)
- **Frontend**: Next.js, React, Tailwind CSS
- **Containerization**: Docker, Docker Compose

### Quick Start

1.  **Clone the repository**
    ```bash
    git clone <repository-url>
    cd MediViewAI
    ```

2.  **Set up environment variables**
    Copy the example environment file and customize it as needed.
    ```bash
    cp .env.example .env
    ```

3.  **Start the application stack**
    ```bash
    docker compose up -d --build
    ```

4.  **Access the services**
    - **Frontend**: [http://localhost:3000](http://localhost:3000)
    - **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
    - **MinIO Console**: [http://localhost:9001](http://localhost:9001) (Credentials are in your `.env` file)

### Project Structure
```
.
├── backend/
│   ├── app/
│   │   ├── api/         # FastAPI routers
│   │   ├── core/        # Configuration
│   │   ├── db/          # Database models and session management
│   │   ├── pipeline/    # Analysis pipeline stages
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic for external services (S3, ML models)
│   │   └── tasks/       # Celery tasks
│   ├── alembic/         # Database migrations
│   └── Dockerfile
├── frontend/
│   ├── app/             # Next.js app router pages
│   ├── components/      # React components
│   └── Dockerfile
├── docker-compose.yml   # Docker services definition
└── README.md
```

### API Endpoints

-   `GET /health`: Health check.
-   `POST /api/uploads/presign`: Get a presigned URL for file uploads.
-   `POST /api/analyze/start`: Start an analysis job for an uploaded file.
-   `GET /api/jobs/{job_id}`: Poll for job status and results.

An example job result payload:
```json
{
  "id": "<job_id>",
  "status": "completed",
  "progress": 100,
  "error": null,
  "result": {
    "study_id": 123,
    "num_findings": 1,
    "s3_key": "uploads/<key>"
  }
}
```

### Configuration

To enable real inference with machine learning models, populate the model names and API tokens in your `.env` file. The application is designed to work with stubbed outputs if these are not configured.

-   `HF_API_TOKEN`, `HF_IMG_CLS_MODEL`, `HF_SUMM_MODEL`, etc.
-   `GEMINI_API_KEY`

### Roadmap

-   **Phase 3**: Real model integrations; streaming job progress via WebSockets/SSE; authentication and logging.
-   **Phase 4**: Study viewer with finding overlays; user feedback and annotation capabilities; audit logging and role-based access control.
-   **Phase 5**: GPU-enabled model serving; caching strategies; enhanced observability and model evaluation gates.


