# FEAT-001: Custom Database Connection - Specification

## Overview

| Field | Value |
|-------|-------|
| **ID** | FEAT-001 |
| **Name** | Custom Database Connection |
| **Priority** | P0 - Critical |
| **Status** | Spec Complete ✅ |
| **Interview** | 2026-01-15 |

## Problem Statement

> Current system only works with the pre-loaded Lending Club dataset. To be commercially viable, customers must be able to connect their own financial databases.

Without this feature, the product only works with the demo dataset. To sell consulting or licenses, customers need to see value with **their own data**.

## Key Decisions (from Interview)

| Decisión | Valor |
|----------|-------|
| Connection UI | **Import desde .env** (DATABASE_URL format) |
| Large schemas | **Selección manual de tablas** + botón "Select All" |
| SSL | **Opciones**: require / prefer / disable |
| Connection loss | **Retry 3x automático** + notificación al usuario |
| Column metadata | **Solo nombres y tipos** (sin descripciones) |
| Free tier limit | **30 queries/mes** (sin límite de conexiones) |
| Target DBs | **Cloud + On-prem** (ambos) |
| Unselected table query | **Prompt**: "¿Quieres habilitar esta tabla?" |
| Credential edit | **Solo borrar y crear nueva** (no editar) |

## Requirements

### Functional Requirements

#### FR-1: Database Connection Management

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1.1 | Import connection from .env file (DATABASE_URL) | Must Have |
| FR-1.2 | System validates connection before saving | Must Have |
| FR-1.3 | Connection credentials stored encrypted (Fernet) | Must Have |
| FR-1.4 | SSL mode selector (require/prefer/disable) | Must Have |
| FR-1.5 | Delete connection (no edit, recreate) | Must Have |
| FR-1.6 | Auto-retry on connection loss (3x) + notify | Should Have |

#### FR-2: Schema & Table Management

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-2.1 | Auto-detect all tables and columns on connection | Must Have |
| FR-2.2 | UI to select which tables to enable for queries | Must Have |
| FR-2.3 | "Select All" / "Deselect All" buttons | Must Have |
| FR-2.4 | Prompt to enable table if query references unselected | Must Have |
| FR-2.5 | Store only column names and types (no descriptions) | Must Have |
| FR-2.6 | Detect primary/foreign keys | Nice to Have |

#### FR-3: Query Adaptation

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-3.1 | SQL Agent uses dynamic schema from selected tables | Must Have |
| FR-3.2 | Prompts adapt to customer's column names | Must Have |
| FR-3.3 | Enforce 30 queries/month limit (Free tier) | Must Have |

### Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1 | Connection validation time | <5 seconds |
| NFR-2 | Schema introspection time | <10 seconds (100 tables) |
| NFR-3 | Credential encryption | Fernet (AES-128) |
| NFR-4 | Connection pooling | 2-10 connections per tenant |
| NFR-5 | Retry on failure | 3 attempts, exponential backoff |

## User Stories

```
As a financial analyst
I want to paste my DATABASE_URL from my .env file
So that I can quickly connect without filling forms
```

```
As a data team lead
I want to select only the relevant tables
So that the AI doesn't get confused with unrelated data
```

```
As a user querying an unselected table
I want to be prompted to enable it
So that I don't have to go back to settings
```

## User Flow

```
1. User clicks "Add Connection"
2. User pastes DATABASE_URL (or uploads .env file)
3. System parses URL, shows extracted values for confirmation
4. User selects SSL mode (default: prefer)
5. User clicks "Test Connection"
   - Success → Continue
   - Fail → Show error, allow retry
6. System introspects schema (shows progress)
7. User sees list of tables with checkboxes
8. User selects tables to enable (or "Select All")
9. Connection saved → Ready to query
```

## Acceptance Criteria

- [ ] User can paste DATABASE_URL and connect
- [ ] Connection credentials are encrypted at rest
- [ ] SSL options work correctly
- [ ] Table selection UI shows all tables with checkboxes
- [ ] "Select All" enables all tables in one click
- [ ] Query to unselected table triggers enable prompt
- [ ] Connection loss triggers 3 retries + notification
- [ ] Deleting connection removes all associated data
- [ ] Free tier enforces 30 queries/month

## Out of Scope (v1)

- MySQL support (PostgreSQL only)
- Real-time schema sync
- Cross-database joins
- Cloud data warehouses (Snowflake, BigQuery)
- Column descriptions / annotations
- Edit existing credentials (only delete + recreate)

## Open Questions (Resolved)

| Question | Decision |
|----------|----------|
| MySQL in v1? | No, PostgreSQL only |
| Form fields vs connection string? | **Import .env** (DATABASE_URL) |
| Column descriptions? | **No**, keep simple |
| Table limit for large schemas? | **Manual selection** with Select All |

---

*Created: 2026-01-15*
*Interview completed: 2026-01-15*
