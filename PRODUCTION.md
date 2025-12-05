# Production Deployment Guide

## 1. Environment Variables
Ensure all environment variables in `.env` are set for production:
- `ENV=production`
- `SECRET_KEY`: Generate a strong random string (e.g., `openssl rand -hex 32`).
- `ALLOWED_ORIGINS`: Set to your actual domain (e.g., `https://mediview.ai`).
- `DATABASE_URL`: Point to your production Postgres instance.
- `S3_ENDPOINT_URL`: Point to your production MinIO/S3.

## 2. Docker Deployment
The application is containerized. Use `docker-compose` or Kubernetes.

```bash
docker-compose -f docker-compose.yml up -d --build
```

### Optimizations:
- **Backend**: Update `Dockerfile` to use a production WSGI server like `gunicorn` with `uvicorn` workers, or tune `uvicorn` settings.
- **Frontend**: The `Dockerfile` currently runs `npm run dev`. Update it to build for production:
  ```dockerfile
  RUN npm run build
  CMD ["npm", "start"]
  ```

## 3. Database Migrations
Run Alembic migrations on the production database:
```bash
docker-compose exec backend alembic upgrade head
```

## 4. HTTPS & Reverse Proxy
Put a reverse proxy (Nginx, Traefik, or AWS ALB) in front of the services.
- Terminate SSL/TLS at the proxy.
- Forward `/api` requests to backend:8000.
- Forward other requests to frontend:3000.

## 5. Monitoring
- Configure logging (e.g., CloudWatch, ELK).
- Set up monitoring (Prometheus/Grafana).

## 6. Security Checklist
- [x] Change default passwords (DB, MinIO).
- [x] Rotate `SECRET_KEY`.
- [x] Ensure `DEBUG=False` (implied by `ENV=production`).
- [x] Limit `ALLOWED_ORIGINS`.
