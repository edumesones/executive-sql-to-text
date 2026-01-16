# FEAT-001: Custom Database Connection - Technical Design

## Architecture

### System Context

```
┌────────────────┐     ┌─────────────────────────┐     ┌────────────────┐
│                │     │   Executive Analytics   │     │   Customer's   │
│     User       │────▶│       Assistant         │────▶│   PostgreSQL   │
│                │     │                         │     │    Database    │
└────────────────┘     └─────────────────────────┘     └────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  App Database   │
                       │  (connections,  │
                       │   schema cache) │
                       └─────────────────┘
```

### Component Design

| Component | Responsibility |
|-----------|---------------|
| `TenantConnectionManager` | Manage connection pools per customer |
| `SchemaIntrospector` | Discover tables/columns from DB |
| `CredentialEncryptor` | Encrypt/decrypt connection strings |
| `ConnectionValidator` | Test and validate connections |

## Data Model

```sql
-- New table for customer database connections
CREATE TABLE database_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    connection_string_encrypted BYTEA NOT NULL,
    schema_cache JSONB,
    is_active BOOLEAN DEFAULT true,
    last_used TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT unique_user_connection_name UNIQUE (user_id, name)
);

CREATE INDEX idx_database_connections_user_id ON database_connections(user_id);
```

### Schema Cache Structure

```json
{
    "tables": [
        {
            "name": "loans",
            "columns": [
                {"name": "id", "type": "integer", "nullable": false, "description": "Primary key"},
                {"name": "amount", "type": "numeric", "nullable": false, "description": "Loan amount in USD"}
            ],
            "primary_key": ["id"],
            "row_count_estimate": 150000
        }
    ],
    "introspected_at": "2026-01-15T10:00:00Z"
}
```

## API Design

```yaml
POST /api/connections:
  description: Create new database connection
  request:
    name: string
    host: string
    port: integer (default 5432)
    database: string
    username: string
    password: string
    ssl_mode: string (default "prefer")
  response:
    connection_id: uuid
    status: "connected" | "failed"
    schema: object

GET /api/connections:
  description: List user's database connections
  response:
    connections: array[{id, name, status, table_count, last_used}]

DELETE /api/connections/{id}:
  description: Remove database connection
  response:
    success: boolean

POST /api/connections/{id}/test:
  description: Test connection with sample query
  request:
    query: string (optional, defaults to "SELECT 1")
  response:
    success: boolean
    execution_time_ms: integer

POST /api/connections/{id}/introspect:
  description: Re-introspect schema
  response:
    schema: object
    introspected_at: timestamp
```

## Implementation Details

### Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `src/database/models.py` | Modify | Add `DatabaseConnection` model |
| `src/database/connection.py` | Modify | Add `TenantConnectionManager` |
| `src/api/routes.py` | Modify | Add connection endpoints |
| `src/api/schemas.py` | Modify | Add Pydantic models |
| `src/agents/sql_agent.py` | Modify | Use dynamic schema |
| `src/utils/encryption.py` | Create | Fernet encryption utility |
| `src/utils/introspection.py` | Create | Schema introspection |

### Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| `cryptography` | >=41.0.0 | Fernet encryption |
| `asyncpg` | (existing) | Async PostgreSQL |
| `sqlalchemy` | (existing) | ORM |

## Security Considerations

1. **Credential Storage**: Use Fernet symmetric encryption with key from environment
2. **Connection Isolation**: Each tenant uses separate connection pool
3. **Query Sandboxing**: Maintain SELECT-only validation
4. **Timeout Protection**: 30s query timeout, 5s connection timeout
5. **Rate Limiting**: Max 100 queries/minute per connection

### Encryption Implementation

```python
# src/utils/encryption.py
from cryptography.fernet import Fernet
import os

class CredentialEncryptor:
    def __init__(self):
        key = os.environ.get("ENCRYPTION_KEY")
        if not key:
            raise ValueError("ENCRYPTION_KEY not set")
        self.cipher = Fernet(key.encode())

    def encrypt(self, plaintext: str) -> bytes:
        return self.cipher.encrypt(plaintext.encode())

    def decrypt(self, ciphertext: bytes) -> str:
        return self.cipher.decrypt(ciphertext).decode()
```

## Performance Considerations

- Connection pools: 2-10 connections per tenant
- Schema cache TTL: 24 hours (re-introspect on demand)
- Lazy pool initialization (create on first query)
- Connection health checks every 60 seconds

## Error Handling

| Error Case | User Message | Technical Action |
|------------|--------------|------------------|
| Connection refused | "Unable to connect. Check host/port." | Log error, return 400 |
| Auth failed | "Authentication failed. Check credentials." | Log (no password), return 401 |
| Timeout | "Connection timed out. Server may be unreachable." | Log, return 504 |
| SSL required | "SSL connection required by server." | Suggest ssl_mode=require |

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Complex schemas (100+ tables) | Medium | High | Pagination, limit to 100 tables initially |
| Slow connections | Low | Medium | Timeouts, async operations |
| Credential exposure | Low | Critical | Encryption + never log passwords |

---

*Created: 2026-01-15*
