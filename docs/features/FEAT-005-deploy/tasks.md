# FEAT-005: Railway Deployment - Tasks

## Summary

| Metric | Value |
|--------|-------|
| **Total Tasks** | 15 |
| **Completed** | 0 |
| **In Progress** | 0 |
| **Story Points** | 5 |

## Task Checklist

### Phase 1: Railway Setup

| ID | Task | Status | SP | Notes |
|----|------|--------|------|-------|
| T-001 | Crear cuenta en Railway | ⬜ | 0.25 | |
| T-002 | Crear proyecto | ⬜ | 0.25 | |
| T-003 | Añadir PostgreSQL plugin | ⬜ | 0.25 | |
| T-004 | Configurar variables de entorno | ⬜ | 0.5 | |

### Phase 2: Containerization

| ID | Task | Status | SP | Notes |
|----|------|--------|------|-------|
| T-005 | Crear Dockerfile para backend | ⬜ | 0.5 | |
| T-006 | Crear Dockerfile para frontend | ⬜ | 0.5 | |
| T-007 | Crear railway.toml | ⬜ | 0.25 | |
| T-008 | Test local con Docker | ⬜ | 0.5 | |

### Phase 3: Deployment

| ID | Task | Status | SP | Notes |
|----|------|--------|------|-------|
| T-009 | Deploy backend service | ⬜ | 0.5 | |
| T-010 | Deploy frontend service | ⬜ | 0.5 | |
| T-011 | Verificar health check | ⬜ | 0.25 | |
| T-012 | Test end-to-end en producción | ⬜ | 0.5 | |

### Phase 4: Domain & CI/CD

| ID | Task | Status | SP | Notes |
|----|------|--------|------|-------|
| T-013 | Comprar dominio (opcional) | ⬜ | 0.25 | |
| T-014 | Configurar custom domain | ⬜ | 0.25 | |
| T-015 | Setup GitHub Actions deploy | ⬜ | 0.5 | |

## Definition of Done

- [ ] Backend accessible via URL
- [ ] Frontend accessible via URL
- [ ] Database connected
- [ ] Health check green
- [ ] Auto-deploy working
- [ ] Cost <$50/month

## Dependencies

| Depends On | Status |
|------------|--------|
| FEAT-001, 002, 003 | App must be functional |

## Blockers

| Blocker | Impact | Action |
|---------|--------|--------|
| (None) | - | - |

## Files to Create

| File | Purpose |
|------|---------|
| `Dockerfile` | Backend container |
| `frontend/Dockerfile` | Frontend container |
| `railway.toml` | Railway config |
| `.github/workflows/deploy.yml` | CI/CD |

## Legend

| Symbol | Meaning |
|--------|---------|
| ⬜ | Not started |
| 🔄 | In progress |
| ✅ | Completed |
| ❌ | Blocked |

---

*Created: 2026-01-15*
