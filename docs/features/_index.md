# Features Dashboard

## Estado General del MVP

| Métrica | Valor |
|---------|-------|
| **Total Features** | 5 |
| **Completadas** | 0 |
| **En Progreso** | 2 |
| **Progreso Total** | 40% |
| **Runway** | 1-3 meses |

## Features por Prioridad

### P0 - Críticas (Sin esto no puedes vender)

| Feature | Descripción | Estado | Progreso |
|---------|-------------|--------|----------|
| [FEAT-001](./FEAT-001-core-db/) | Custom DB Connection | 🟡 | 100% (PR pending) |
| [FEAT-002](./FEAT-002-auth/) | Basic Authentication | 🟡 | 100% backend (frontend → FEAT-004) |
| [FEAT-003](./FEAT-003-landing/) | Landing + Pricing | 🔴 | 0% |

### P1 - Altas (Mejora conversión)

| Feature | Descripción | Estado | Progreso |
|---------|-------------|--------|----------|
| [FEAT-004](./FEAT-004-gradio/) | Gradio Migration | 🔴 | 0% |
| [FEAT-005](./FEAT-005-deploy/) | Railway Deployment | 🔴 | 0% |

## Vista Rápida

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FEATURE PROGRESS                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  FEAT-001 Core DB      [████████████████████] 100%  🟡 (PR pending) │
│  FEAT-002 Auth         [████████████████████] 100%  🟡 (backend)    │
│  FEAT-003 Landing      [░░░░░░░░░░░░░░░░░░░░]   0%  🔴              │
│  FEAT-004 Gradio       [░░░░░░░░░░░░░░░░░░░░]   0%  🔴              │
│  FEAT-005 Deploy       [░░░░░░░░░░░░░░░░░░░░]   0%  🔴              │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Orden de Implementación

```
FASE 1: Fundamentos (Semana 1-2)
└── FEAT-001: Core DB Connection

FASE 2: Acceso (Semana 3-4)
├── FEAT-002: Authentication
└── FEAT-003: Landing Page

FASE 3: Polish (Semana 5-6)
└── FEAT-004: Gradio Migration

FASE 4: Launch (Semana 7-8)
└── FEAT-005: Railway Deployment
```

## Dependencias

```
FEAT-001 ─────┬──────▶ FEAT-002 ──────▶ FEAT-003
              │                              │
              └──────▶ FEAT-004 ─────────────┴──────▶ FEAT-005
```

## Story Points

| Feature | SP | Complejidad |
|---------|-------|-------------|
| FEAT-001 | 13 | Alta |
| FEAT-002 | 8 | Media |
| FEAT-003 | 5 | Baja |
| FEAT-004 | 8 | Media |
| FEAT-005 | 5 | Media |
| **Total** | **39** | - |

## Quick Links

### Por Feature

| Feature | Spec | Design | Tasks | Status |
|---------|------|--------|-------|--------|
| FEAT-001 | [spec](./FEAT-001-core-db/spec.md) | [design](./FEAT-001-core-db/design.md) | [tasks](./FEAT-001-core-db/tasks.md) | [status](./FEAT-001-core-db/status.md) |
| FEAT-002 | [spec](./FEAT-002-auth/spec.md) | [design](./FEAT-002-auth/design.md) | [tasks](./FEAT-002-auth/tasks.md) | [status](./FEAT-002-auth/status.md) |
| FEAT-003 | [spec](./FEAT-003-landing/spec.md) | [design](./FEAT-003-landing/design.md) | [tasks](./FEAT-003-landing/tasks.md) | [status](./FEAT-003-landing/status.md) |
| FEAT-004 | [spec](./FEAT-004-gradio/spec.md) | [design](./FEAT-004-gradio/design.md) | [tasks](./FEAT-004-gradio/tasks.md) | [status](./FEAT-004-gradio/status.md) |
| FEAT-005 | [spec](./FEAT-005-deploy/spec.md) | [design](./FEAT-005-deploy/design.md) | [tasks](./FEAT-005-deploy/tasks.md) | [status](./FEAT-005-deploy/status.md) |

### Template

Para crear una nueva feature: [_template/](./_template/)

## Leyenda

| Símbolo | Significado |
|---------|-------------|
| 🔴 | Not Started |
| 🟡 | In Progress |
| 🟢 | Complete |
| ⬜ | Task pending |
| ✅ | Task done |

---

*Última actualización: 2026-01-16*
