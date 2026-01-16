# FEAT-005: Railway Deployment - Technical Design

## Architecture

### Railway Setup

```
┌─────────────────────────────────────────────────────────────────────┐
│                          RAILWAY                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────┐      ┌─────────────────┐                       │
│  │    Backend      │      │    Frontend     │                       │
│  │    FastAPI      │◄────▶│    Gradio       │                       │
│  │  :8000          │      │  :7860          │                       │
│  │  CPU: 0.5       │      │  CPU: 0.5       │                       │
│  │  RAM: 512MB     │      │  RAM: 512MB     │                       │
│  └────────┬────────┘      └─────────────────┘                       │
│           │                                                          │
│           ▼                                                          │
│  ┌─────────────────┐                                                │
│  │   PostgreSQL    │                                                │
│  │   (Managed)     │                                                │
│  │   1GB Storage   │                                                │
│  └─────────────────┘                                                │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Dockerfile (Backend)

```dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY config/ ./config/
COPY run_api.py .

RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s \
    CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["python", "run_api.py"]
```

### Environment Variables

```env
# Auto-injected by Railway
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Manual config
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
ENCRYPTION_KEY=your-32-byte-key

# App
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=https://your-app.railway.app
LOG_LEVEL=INFO
```

### Cost Estimation

| Resource | Monthly Cost |
|----------|--------------|
| Backend (512MB) | ~$5 |
| Frontend (512MB) | ~$5 |
| PostgreSQL (1GB) | ~$5 |
| **Subtotal** | **~$15** |
| OpenAI API | ~$10-30 |
| **Total** | **~$25-45** |

## Files to Create

| File | Purpose |
|------|---------|
| `Dockerfile` | Backend container |
| `frontend/Dockerfile` | Frontend container |
| `railway.toml` | Railway config |
| `.env.production.example` | Env template |

### CI/CD (GitHub Actions)

```yaml
name: Deploy to Railway

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: railwayapp/railway-action@v1
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

## Rollback Plan

1. Railway maintains deploy history
2. Click "Rollback" in dashboard
3. If Railway fails, migrate to Render

## Future: AWS Migration

When ready to scale:
1. Export PostgreSQL data
2. Create AWS ECS cluster
3. Create RDS instance
4. Update DNS

---

*Created: 2026-01-15*
