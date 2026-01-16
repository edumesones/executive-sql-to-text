# FEAT-002: Basic Authentication - Specification

## Overview

| Field | Value |
|-------|-------|
| **ID** | FEAT-002 |
| **Name** | Basic Authentication |
| **Priority** | P0 - Critical |
| **Status** | Spec Complete ✅ |
| **Interview** | 2026-01-15 |

## Problem Statement

> Current system has no authentication. For commercial use, we need user registration, login, session management, and per-user data isolation.

Without authentication:
- Cannot isolate data between customers
- Cannot limit usage by tier (free/pro)
- Cannot track who uses what
- Not commercially viable

## Key Decisions (from Interview)

| Decisión | Valor |
|----------|-------|
| Tipo de token | **JWT stateless** |
| Almacenamiento frontend | **httpOnly cookie** |
| Email verification | **No en MVP** (implementar después) |
| Expiración JWT | **24 horas** |
| Rate limiting login | **5 intentos → 15 min lockout** |
| Forgot password | **Sí, con email (SendGrid)** |
| Usuario:Conexión | **1:1** (una conexión por usuario) |
| Borrar usuario | **Hard delete** (todo inmediatamente) |
| Servicio email | **SendGrid** (100 emails/día gratis) |
| UI Login | **Páginas separadas** (`/login`, `/register`, `/forgot-password`) |
| Post-login redirect | **Dashboard principal** |
| Campos registro | **Solo email + password** (mínimo viable) |

## Requirements

### Functional Requirements

#### FR-1: User Registration

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1.1 | Register with email + password | Must Have |
| FR-1.2 | Email verification | Should Have |
| FR-1.3 | Password strength validation | Must Have |

#### FR-2: User Login

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-2.1 | Login with email + password | Must Have |
| FR-2.2 | JWT token generation | Must Have |
| FR-2.3 | Remember me (extended session) | Should Have |
| FR-2.4 | Logout / token invalidation | Must Have |

#### FR-3: Password Management

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-3.1 | Forgot password flow | Should Have |
| FR-3.2 | Change password | Should Have |

### Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1 | Password hashing | bcrypt (cost 12) |
| NFR-2 | JWT expiration | 24 hours (extendable) |
| NFR-3 | Rate limiting | 5 failed attempts → 15min lockout |

## User Stories

```
As a new user
I want to register with my email
So that I can access the application
```

```
As a returning user
I want to login securely
So that my data is protected
```

## Acceptance Criteria

- [ ] User can register with email/password
- [ ] User can login and receive JWT
- [ ] API endpoints reject unauthenticated requests (401)
- [ ] User can only access their own database connections
- [ ] Login state persists across browser sessions
- [ ] Logout invalidates session

## User Flow

```
REGISTRO:
1. Usuario va a /register
2. Introduce email + password
3. Sistema valida password strength
4. Sistema crea usuario + envía a dashboard
5. (Sin verificación de email en MVP)

LOGIN:
1. Usuario va a /login
2. Introduce email + password
3. Sistema valida credenciales
4. Si OK → JWT en httpOnly cookie → redirect a dashboard
5. Si FAIL → contador +1, si ≥5 → lockout 15min

FORGOT PASSWORD:
1. Usuario va a /forgot-password
2. Introduce email
3. Sistema envía link de reset via SendGrid
4. Usuario hace clic en link → /reset-password?token=xxx
5. Usuario pone nueva password → redirect a /login

LOGOUT:
1. Usuario hace clic en logout
2. Sistema borra cookie
3. Redirect a /login
```

## Out of Scope (v1)

- SSO / OAuth providers (Google, GitHub, etc.)
- Two-factor authentication (2FA)
- API key authentication
- Role-based access control (RBAC)
- Email verification
- Múltiples conexiones por usuario

## Security Checklist

- [ ] Passwords never logged or exposed in errors
- [ ] JWT stored securely
- [ ] HTTPS enforced in production
- [ ] Rate limiting on auth endpoints
- [ ] SQL injection prevention maintained

---

*Created: 2026-01-15*
*Interview completed: 2026-01-15*
