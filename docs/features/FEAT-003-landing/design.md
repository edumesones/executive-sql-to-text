# FEAT-003: Landing Page + Pricing - Technical Design

## Architecture

### Page Structure

```
/ (Landing)
├── Hero Section
├── Features Section
├── Pricing Section
├── CTA Section
└── Footer

/app (Main application - requires auth)
/pricing (Detailed pricing)
/contact (Consulting inquiry form)
```

### Implementation Approach

For MVP, implement landing as part of the Gradio/Streamlit app to avoid maintaining separate stack.

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Same frontend (Gradio) | Single stack | Limited design | **MVP** |
| Next.js | SEO, design flexibility | New stack | v2 |
| Webflow | Fast, no code | Cost, separate | Not now |

## Page Components

### Hero Component

```python
# Landing section with value proposition
gr.Markdown("""
# Ask Your Data in Plain English

AI-powered analytics for financial teams.
No SQL required. Insights in seconds.
""")

with gr.Row():
    gr.Button("Start Free Trial", variant="primary")
    gr.Button("Watch Demo", variant="secondary")
```

### Features Component

| Feature | Icon | Copy |
|---------|------|------|
| Natural Language | 💬 | "Ask questions like 'What's our default rate?'" |
| Instant Insights | ⚡ | "Get charts and recommendations in <30s" |
| Financial Focus | 🏦 | "Built for lending and financial data" |
| Voice Enabled | 🎤 | "Speak your queries, hands-free analysis" |

### Pricing Component

```
┌─────────────────┬─────────────────┬─────────────────┐
│      FREE       │       PRO       │   ENTERPRISE    │
├─────────────────┼─────────────────┼─────────────────┤
│ $0/month        │ $99/month       │ Custom          │
├─────────────────┼─────────────────┼─────────────────┤
│ 100 queries/mo  │ Unlimited       │ Unlimited       │
│ 1 DB connection │ 5 connections   │ Unlimited       │
│ Basic charts    │ All chart types │ All + custom    │
│ Community       │ Email support   │ Dedicated       │
│                 │ Voice input     │ On-premise opt  │
│                 │ Export CSV      │ SSO / Audit     │
├─────────────────┼─────────────────┼─────────────────┤
│ [Start Free]    │ [Upgrade]       │ [Contact Us]    │
└─────────────────┴─────────────────┴─────────────────┘
```

## SEO Requirements

| Element | Content |
|---------|---------|
| Title | "Executive Analytics - AI SQL for Finance" |
| Description | "Query your financial data in plain English" |
| Keywords | sql analytics, natural language sql, finance |

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `frontend/pages/landing.py` | Create | Landing page component |
| `frontend/pages/pricing.py` | Create | Pricing detail page |
| `frontend/static/` | Create | Images, icons |

## Assets Needed

- Logo (text-based for MVP)
- Hero image/screenshot
- Feature icons (emoji for MVP)
- Product screenshot

---

*Created: 2026-01-15*
