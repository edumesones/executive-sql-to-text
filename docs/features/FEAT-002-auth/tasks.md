# FEAT-002: Basic Authentication - Tasks

## Summary

| Metric | Value |
|--------|-------|
| **Total Tasks** | 12 |
| **Completed** | 8 |
| **Deferred** | 4 (to FEAT-004) |
| **Story Points** | 8 |

## ⚠️ Cambio de Arquitectura

**Decisión:** Se cambió de Supabase a JWT nativo con bcrypt + PyJWT.
**Razón:** Mayor control, sin dependencia externa, cookies httpOnly más seguras.

## Task Checklist

### Phase 1: Auth Setup (Adaptado de Supabase a JWT Nativo)

| ID | Task | Status | SP | Notes |
|----|------|--------|------|-------|
| T-001 | ~~Crear proyecto en Supabase~~ → Implementar JWT nativo | ✅ | 0.5 | src/auth/jwt.py |
| T-002 | Configurar variables de entorno | ✅ | 0.5 | SECRET_KEY, ALGORITHM en .env |
| T-003 | ~~Instalar supabase-py~~ → Instalar bcrypt, PyJWT | ✅ | 0.5 | requirements.txt |

### Phase 2: Backend Integration

| ID | Task | Status | SP | Notes |
|----|------|--------|------|-------|
| T-004 | Crear `src/api/auth.py` con JWT | ✅ | 1 | 401 líneas, 8 endpoints |
| T-005 | Implementar dependency `get_current_user` | ✅ | 1 | src/auth/dependencies.py |
| T-006 | Proteger endpoints existentes con auth | ✅ | 1 | /api/query, /api/history protegidos |
| T-007 | Crear tabla `users` + `password_reset_tokens` | ✅ | 1 | src/database/models.py |
| T-008 | Añadir tests de auth | ✅ | 1 | tests/unit/test_auth.py (244 líneas) |

### Phase 3: Frontend Integration (⏸️ Deferred to FEAT-004)

> **Nota:** Frontend auth se implementará junto con migración a Gradio (FEAT-004).
> Razón: No tiene sentido invertir en Streamlit UI que se descartará.

| ID | Task | Status | SP | Notes |
|----|------|--------|------|-------|
| T-009 | Crear formulario Login | ⏸️ | 0.5 | → FEAT-004 (Gradio) |
| T-010 | Crear formulario Register | ⏸️ | 0.5 | → FEAT-004 (Gradio) |
| T-011 | Manejar estado de sesión | ⏸️ | 1 | → FEAT-004 (Gradio) |
| T-012 | Redirect a login si no autenticado | ⏸️ | 0.5 | → FEAT-004 (Gradio) |

## Definition of Done

- [ ] User can register with email/password
- [ ] User can login and get JWT
- [ ] Protected endpoints reject 401 without token
- [ ] Tests passing
- [ ] PR merged

## Dependencies

| Depends On | Status |
|------------|--------|
| None | - |

## Blockers

| Blocker | Impact | Action |
|---------|--------|--------|
| (None) | - | - |

## Files to Modify

| File | Changes |
|------|---------|
| `src/api/auth.py` | Create: Supabase integration |
| `src/api/routes.py` | Add auth dependency |
| `src/database/models.py` | Add UserProfile |
| `frontend/` | Add login/register UI |
| `.env.example` | Add Supabase keys |

## Legend

| Symbol | Meaning |
|--------|---------|
| ⬜ | Not started |
| 🔄 | In progress |
| ✅ | Completed |
| ❌ | Blocked |

---

*Created: 2026-01-15*
