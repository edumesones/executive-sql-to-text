# FEAT-004: Gradio Migration - Specification

## Overview

| Field | Value |
|-------|-------|
| **ID** | FEAT-004 |
| **Name** | Gradio Migration |
| **Priority** | P1 - High |
| **Status** | 🟡 In Progress |
| **Timeline** | ASAP |

## Problem Statement

> Streamlit works but has limitations for a commercial product. Gradio offers better default styling, more flexibility, and better AI/ML workflow integration.

Streamlit limitations:
- Less professional appearance
- Limited theming options
- Harder to customize layouts
- Not ideal for production SaaS

## Architecture Decision

| Decision | Value |
|----------|-------|
| **Landing** | Puerto 7860 (FEAT-003) |
| **App Principal** | Puerto 7861 (nueva) |
| **Flujo** | Landing → Login → Redirect a App |

## Interview Results (2026-01-16)

| Pregunta | Decisión |
|----------|----------|
| Voice Input | `gr.Audio(source="microphone")` nativo Gradio |
| Auth Model | Freemium: 1 query gratis sin login |
| Demo Data | Sin login → Demo DB (lending_club sample) con descripción en UI |
| Theme | Dark mode only |
| Must Have | Voice input, Download CSV |
| Nice to Have | Query history, Example queries |

## Requirements

### Functional Requirements

#### FR-1: Core Features (Must Have)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1.1 | Text query input | Must Have |
| FR-1.2 | Voice input (`gr.Audio` nativo) | Must Have |
| FR-1.3 | Query results display (table) | Must Have |
| FR-1.4 | Chart visualization (Plotly) | Must Have |
| FR-1.5 | Insights display (markdown) | Must Have |
| FR-1.6 | Download CSV | Must Have |
| FR-1.7 | Demo DB info panel | Must Have |

#### FR-2: UI Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-2.1 | Dark theme only | Must Have |
| FR-2.2 | Loading states and progress | Must Have |
| FR-2.3 | Error handling with friendly messages | Must Have |
| FR-2.4 | Responsive layout | Should Have |

#### FR-3: Authentication & Freemium

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-3.1 | Login state from landing page | Must Have |
| FR-3.2 | Freemium: 1 query sin login | Must Have |
| FR-3.3 | Query counter (sin login) | Must Have |
| FR-3.4 | Prompt login after free query | Must Have |

#### FR-4: Nice to Have

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-4.1 | Query history sidebar | Should Have |
| FR-4.2 | Example queries | Should Have |

## Demo Database Info

Panel visible para usuarios sin login:

```
📊 Demo Database: Lending Club Loans

Esta base de datos contiene información de préstamos incluyendo:
- Monto del préstamo (loan_amnt)
- Tasa de interés (int_rate)
- Grado del préstamo (grade: A-G)
- Estado del préstamo (loan_status)
- Propósito (purpose)
- Estado/ubicación (addr_state)

Ejemplos de queries:
• "Show me top 10 loans by amount"
• "What is the default rate by grade?"
• "Average interest rate by state"
```

## User Stories

```
As a visitor (sin login)
I want to try 1 query on demo data
So that I can evaluate the product before registering
```

```
As an analyst
I want a professional dark-themed interface
So that I can present it to stakeholders
```

```
As a user
I want voice input to work seamlessly
So that I can query hands-free
```

## Acceptance Criteria

- [ ] App runs on port 7861
- [ ] Text query input works
- [ ] Voice input with gr.Audio transcribes and submits
- [ ] Charts render correctly (Plotly)
- [ ] Download CSV button works
- [ ] Dark theme applied
- [ ] Demo DB info panel visible (sin login)
- [ ] 1 free query works (sin login)
- [ ] After free query, prompt to login
- [ ] Login redirects from landing (7860)
- [ ] Loading states visible during API calls
- [ ] Error messages are user-friendly

## Out of Scope (v1)

- Light theme
- Custom component development
- Advanced animations
- Offline support
- Multiple database connections

## Files to Create

| File | Purpose |
|------|---------|
| `frontend/gradio_main.py` | Main app (queries) |
| `run_gradio_app.py` | Launcher for main app (7861) |

## Files to Modify

| File | Changes |
|------|---------|
| `frontend/gradio_app.py` | Add redirect to 7861 after login |
| `.env.example` | Add GRADIO_APP_PORT=7861 |

---

*Created: 2026-01-15*
*Updated: 2026-01-16 (Interview completed)*
