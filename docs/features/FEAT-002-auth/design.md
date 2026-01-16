# FEAT-002: Basic Authentication - Technical Design

## Architecture

### Auth Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                     AUTHENTICATION FLOW                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  User                  Frontend                 Backend              │
│    │                      │                        │                 │
│    │── Email/Pass ───────▶│                        │                 │
│    │                      │── POST /auth/login ───▶│                 │
│    │                      │                        │                 │
│    │                      │       Supabase Auth    │                 │
│    │                      │       validates ───────┼──────────▶      │
│    │                      │                        │                 │
│    │                      │◀── JWT Token ──────────│                 │
│    │◀── Redirect to App ──│                        │                 │
│    │                      │                        │                 │
│    │── Query (+ JWT) ────▶│                        │                 │
│    │                      │── /api/query ─────────▶│                 │
│    │                      │   (Auth header)        │                 │
│    │                      │                        │── Verify JWT    │
│    │                      │◀── Results ───────────│                  │
│    │◀── Display ──────────│                        │                 │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Auth Provider Decision

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **Supabase Auth** | Free tier, built-in, fast | Vendor lock-in | **MVP Choice** |
| Auth0 | Feature-rich | Cost at scale | Future option |
| Custom JWT | Full control | More work | Not for MVP |

## Data Model

```sql
-- Using Supabase Auth, users table is managed by Supabase
-- We add a profiles table for app-specific data

CREATE TABLE user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    display_name VARCHAR(255),
    company VARCHAR(255),
    tier VARCHAR(20) DEFAULT 'free',  -- free, pro, enterprise
    query_count_month INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_user_profiles_tier ON user_profiles(tier);
```

## API Design

```yaml
# Auth endpoints (handled by Supabase client)
POST /auth/signup:
  request: { email: string, password: string }
  response: { user: object, session: object }

POST /auth/login:
  request: { email: string, password: string }
  response: { user: object, session: object, access_token: string }

POST /auth/logout:
  headers: { Authorization: "Bearer <token>" }
  response: { success: boolean }

GET /auth/user:
  headers: { Authorization: "Bearer <token>" }
  response: { user: object, profile: object }
```

## Implementation Details

### FastAPI Integration

```python
# src/api/auth.py
from supabase import create_client, Client
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(credentials = Depends(security)):
    """Validate JWT and return user."""
    token = credentials.credentials
    try:
        user = supabase.auth.get_user(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        return user.user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
```

### Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `src/api/auth.py` | Create | Supabase auth integration |
| `src/api/routes.py` | Modify | Add auth dependency |
| `src/database/models.py` | Modify | Add UserProfile |
| `frontend/` | Modify | Add login/register UI |
| `.env.example` | Modify | Add Supabase keys |

### Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| `supabase` | >=2.0.0 | Auth client |

### Environment Variables

```env
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...  # For admin operations
```

## Security Considerations

1. Never log passwords or tokens
2. Use httpOnly cookies or secure storage for JWT
3. Enforce HTTPS in production
4. Rate limit auth endpoints (5 attempts → 15min lockout)
5. Validate JWT on every protected request

## Error Handling

| Error | HTTP Code | User Message |
|-------|-----------|--------------|
| Invalid credentials | 401 | "Invalid email or password" |
| Token expired | 401 | "Session expired, please login again" |
| Rate limited | 429 | "Too many attempts, try again later" |

---

*Created: 2026-01-15*
