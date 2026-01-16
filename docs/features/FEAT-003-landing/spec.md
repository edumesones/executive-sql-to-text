# FEAT-003: Landing Page + Pricing - Specification

## Overview

| Field | Value |
|-------|-------|
| **ID** | FEAT-003 |
| **Name** | Landing Page + Pricing |
| **Priority** | P0 - Critical |
| **Status** | Ready for Implementation |

## Problem Statement

> No public presence to attract customers. Need a landing page to explain product value, show pricing, and convert visitors.

Without landing page:
- No way to explain the product
- No visibility of prices
- No acquisition channel
- Can't do GTM (Product Hunt, LinkedIn, etc.)

## Technical Decisions (Interview 2026-01-16)

| Decision | Value | Rationale |
|----------|-------|-----------|
| **Stack** | Gradio (`gr.HTML`, `gr.Markdown`) | Coherente con FEAT-004 (Gradio migration) |
| **Start Free Trial** | → `/register` | Usa auth de FEAT-002 |
| **Contact** | `mailto:e.gzlzmesones@gmail.com` | Simple, directo |
| **Estilo visual** | Gradiente moderno, SaaS style | Colores vivos, profesional |
| **Demo** | GIF/Video embed | Crear grabación de pantalla |
| **Pricing display** | 3 tiers (Free, Pro placeholder, Enterprise) | Pro sin precio fijo aún |

## Requirements

### Functional Requirements

#### FR-1: Landing Page Content

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1.1 | Hero section with value proposition | Must Have |
| FR-1.2 | Feature highlights (3-4 key benefits) | Must Have |
| FR-1.3 | Demo GIF/Video embed | Must Have |
| FR-1.4 | Testimonials placeholder | Nice to Have |

#### FR-2: Pricing Display

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-2.1 | Free tier details ($0, 100 queries/mo) | Must Have |
| FR-2.2 | Pro tier (Coming Soon, sin precio) | Must Have |
| FR-2.3 | Enterprise "Contact Us" | Must Have |
| FR-2.4 | Feature comparison table | Should Have |

#### FR-3: Call to Action

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-3.1 | "Start Free Trial" → `/register` | Must Have |
| FR-3.2 | "Contact Us" → `mailto:e.gzlzmesones@gmail.com` | Must Have |
| FR-3.3 | "Watch Demo" → scroll to video section | Should Have |

## Content Strategy

### Hero Section
```
Headline: "Ask Your Data in Plain English"
Subheadline: "AI-powered analytics for financial teams.
              No SQL required. Insights in seconds."

CTA Primary: "Start Free Trial" → /register
CTA Secondary: "Watch Demo" → scroll to demo section
```

### Visual Style
```
- Gradiente moderno (purple/blue tones típico SaaS)
- Fondo con gradiente sutil
- Cards con sombras suaves
- Tipografía limpia y grande
- Espaciado generoso
```

### Pricing Tiers

| Tier | Price | Features |
|------|-------|----------|
| Free | $0/month | 100 queries/mo, 1 DB, basic charts |
| Pro | Coming Soon | Unlimited queries, 5 DBs, voice input, CSV export |
| Enterprise | Contact Us | Unlimited, on-prem option, SSO, dedicated support |

### Demo Video/GIF
```
Contenido a grabar:
1. Abrir la app
2. Escribir query en lenguaje natural: "Show me top 10 loans by amount"
3. Ver resultado: SQL generado, tabla, gráfico
4. Mostrar insight generado automáticamente
Duración: 15-30 segundos
Formato: GIF o MP4
```

## Acceptance Criteria

- [ ] Landing page accessible at root URL (Gradio)
- [ ] Clear value proposition visible above fold
- [ ] Pricing tiers displayed (Free, Pro placeholder, Enterprise)
- [ ] "Start Free Trial" navigates to /register
- [ ] "Contact Us" opens mailto:e.gzlzmesones@gmail.com
- [ ] Demo GIF/video visible
- [ ] Mobile responsive layout
- [ ] Gradiente moderno style applied

## Out of Scope (v1)

- Blog
- Documentation site
- Customer portal
- Multi-language
- Payment integration (Stripe)
- Actual Pro tier pricing

---

*Created: 2026-01-15*
*Updated: 2026-01-16 (Interview completed)*
