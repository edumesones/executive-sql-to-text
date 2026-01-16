# FEAT-004: Gradio Migration - Tasks

## Summary

| Metric | Value |
|--------|-------|
| **Total Tasks** | 14 |
| **Completed** | 13 |
| **In Progress** | 1 |
| **Story Points** | 8 |

## Task Checklist

### Phase 1: API (T-001 to T-002)

| ID | Task | Status | SP | Notes |
|----|------|--------|------|-------|
| T-001 | Add /api/demo-query endpoint | ✅ | 0.5 | Optional auth for freemium |
| T-002 | Update CORS in src/api/main.py | ✅ | 0.25 | Added port 7861 |

### Phase 2: Infrastructure (T-003 to T-005)

| ID | Task | Status | SP | Notes |
|----|------|--------|------|-------|
| T-003 | Create run_gradio_app.py launcher | ✅ | 0.25 | Port 7861 |
| T-004 | Create frontend/gradio_main.py skeleton | ✅ | 1 | Main app structure |
| T-005 | Implement DARK_CSS theme | ✅ | 0.5 | Dark mode only |

### Phase 3: Core UI (T-006 to T-009)

| ID | Task | Status | SP | Notes |
|----|------|--------|------|-------|
| T-006 | Demo DB info panel | ✅ | 0.25 | Lending Club info |
| T-007 | Query input (text + voice) | ✅ | 1 | gr.Audio native |
| T-008 | Results display (table, chart, insights) | ✅ | 1.5 | Plotly + DataFrame |
| T-009 | Download CSV functionality | ✅ | 0.5 | Temp file download |

### Phase 4: Freemium Logic (T-010 to T-012)

| ID | Task | Status | SP | Notes |
|----|------|--------|------|-------|
| T-010 | Query counter state management | ✅ | 0.5 | gr.State tracking |
| T-011 | Login prompt after free query | ✅ | 0.5 | Redirect to landing |
| T-012 | Modify gradio_app.py login redirect | ✅ | 0.5 | JS redirect to 7861 |

### Phase 5: Polish (T-013 to T-014)

| ID | Task | Status | SP | Notes |
|----|------|--------|------|-------|
| T-013 | Update .env.example | ✅ | 0.25 | GRADIO_APP_PORT, MAIN_APP_URL |
| T-014 | End-to-end testing | 🔄 | 0.5 | Needs browser test |

## Definition of Done

- [x] App runs on port 7861
- [x] Text query input works
- [x] Voice input with gr.Audio
- [x] Charts render (Plotly)
- [x] Download CSV works
- [x] Dark theme applied
- [x] Demo DB info panel visible
- [x] 1 free query works (freemium)
- [x] Login prompt after free query
- [x] Login redirects from landing
- [ ] Manual browser testing
- [ ] PR merged

## Files Created

| File | Purpose | Status |
|------|---------|--------|
| `frontend/gradio_main.py` | Main query app | ✅ |
| `run_gradio_app.py` | Launcher (7861) | ✅ |

## Files Modified

| File | Changes | Status |
|------|---------|--------|
| `src/api/routes.py` | Added /api/demo-query | ✅ |
| `src/api/main.py` | Updated CORS | ✅ |
| `frontend/gradio_app.py` | Login redirect | ✅ |
| `.env.example` | New vars | ✅ |

## Legend

| Symbol | Meaning |
|--------|---------|
| ⬜ | Not started |
| 🔄 | In progress |
| ✅ | Completed |
| ❌ | Blocked |

---

*Created: 2026-01-15*
*Updated: 2026-01-16*
