# FEAT-004: Gradio Migration - Tasks

## Summary

| Metric | Value |
|--------|-------|
| **Total Tasks** | 16 |
| **Completed** | 0 |
| **In Progress** | 0 |
| **Story Points** | 8 |

## Task Checklist

### Phase 1: Setup

| ID | Task | Status | SP | Notes |
|----|------|--------|------|-------|
| T-001 | Instalar gradio y dependencias | ⬜ | 0.5 | |
| T-002 | Crear estructura base `gradio_app.py` | ⬜ | 0.5 | |
| T-003 | Configurar tema personalizado | ⬜ | 0.5 | |

### Phase 2: Component Migration

| ID | Task | Status | SP | Notes |
|----|------|--------|------|-------|
| T-004 | Query input (text + submit) | ⬜ | 0.5 | |
| T-005 | Voice input (microphone) | ⬜ | 1 | |
| T-006 | Results table (dataframe) | ⬜ | 0.5 | |
| T-007 | Chart visualization (Plotly) | ⬜ | 1 | |
| T-008 | Insights display (markdown) | ⬜ | 0.5 | |
| T-009 | SQL output (code block) | ⬜ | 0.5 | |

### Phase 3: Integration

| ID | Task | Status | SP | Notes |
|----|------|--------|------|-------|
| T-010 | Integrar auth (login/register) | ⬜ | 1 | |
| T-011 | Integrar API client (httpx) | ⬜ | 0.5 | |
| T-012 | Manejar estados de carga | ⬜ | 0.5 | |
| T-013 | Error handling UI | ⬜ | 0.5 | |

### Phase 4: Polish

| ID | Task | Status | SP | Notes |
|----|------|--------|------|-------|
| T-014 | Responsive layout | ⬜ | 0.5 | |
| T-015 | Dark/Light mode | ⬜ | 0.5 | |
| T-016 | Testing manual en browsers | ⬜ | 0.5 | Chrome, Firefox, Safari |

## Definition of Done

- [ ] All Streamlit features work in Gradio
- [ ] Voice input working
- [ ] Charts rendering
- [ ] Auth integrated
- [ ] Responsive
- [ ] PR merged

## Dependencies

| Depends On | Status |
|------------|--------|
| FEAT-001 (connections) | For connection dropdown |
| FEAT-002 (auth) | For login UI |

## Blockers

| Blocker | Impact | Action |
|---------|--------|--------|
| (None) | - | - |

## Files to Create

| File | Purpose |
|------|---------|
| `frontend/gradio_app.py` | Main app |
| `frontend/components/` | UI components |
| `frontend/auth.py` | Auth state |

## Legend

| Symbol | Meaning |
|--------|---------|
| ⬜ | Not started |
| 🔄 | In progress |
| ✅ | Completed |
| ❌ | Blocked |

---

*Created: 2026-01-15*
