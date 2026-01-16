# FEAT-001: Custom Database Connection - Tasks

## Summary

| Metric | Value |
|--------|-------|
| **Total Tasks** | 16 |
| **Completed** | 16 |
| **In Progress** | 0 |
| **Story Points** | 13 |

## Task Checklist

### Phase 1: Data Model

| ID | Task | Status | SP | Notes |
|----|------|--------|------|-------|
| T-001 | Crear modelo `DatabaseConnection` en SQLAlchemy | ✅ | 2 | CustomerConnection en models.py |
| T-002 | Crear tabla `database_connections` con migración | ✅ | 1 | TableConfig, QueryUsage añadidos |
| T-003 | Implementar encriptación de credenciales (Fernet) | ✅ | 2 | src/database/encryption.py |
| T-004 | Añadir tests para el modelo | ✅ | 1 | test_encryption.py |

### Phase 2: API Endpoints

| ID | Task | Status | SP | Notes |
|----|------|--------|------|-------|
| T-005 | `POST /api/connections` - Crear conexión | ✅ | 2 | src/api/connections.py |
| T-006 | `GET /api/connections` - Listar conexiones | ✅ | 1 | src/api/connections.py |
| T-007 | `DELETE /api/connections/{id}` - Eliminar | ✅ | 1 | src/api/connections.py |
| T-008 | `POST /api/connections/{id}/test` - Test query | ✅ | 1 | src/api/connections.py |
| T-009 | `POST /api/connections/{id}/introspect` - Re-scan | ✅ | 1 | src/api/connections.py |

### Phase 3: Schema Introspection

| ID | Task | Status | SP | Notes |
|----|------|--------|------|-------|
| T-010 | Función para detectar tablas y columnas | ✅ | 2 | src/database/introspection.py |
| T-011 | Inferir tipos de datos y nullability | ✅ | 1 | DatabaseAdapter pattern |
| T-012 | Detectar PKs y FKs | ✅ | 1 | PostgreSQL/MySQL adapters |
| T-013 | Cachear schema en JSONB | ✅ | 1 | cached_schema en models.py |

### Phase 4: Agent Integration

| ID | Task | Status | SP | Notes |
|----|------|--------|------|-------|
| T-014 | SQL Agent usa schema dinámico del connection | ✅ | 2 | sql_agent.py modificado |
| T-015 | Adaptar prompts para nombres de columnas custom | ✅ | 1 | Prompts dinámicos |
| T-016 | Connection pool por tenant | ✅ | 2 | TenantConnectionManager |

## Definition of Done

- [x] Código implementado y revisado
- [x] Tests unitarios pasan (>80% coverage)
- [ ] Documentación de API actualizada
- [ ] PR mergeado a main
- [ ] Probado con una DB real (no mock)

## Dependencies

| Depends On | Status |
|------------|--------|
| None | - |

## Blockers

| Blocker | Impact | Action |
|---------|--------|--------|
| (None) | - | - |

## Files to Modify

| File | Changes |
|------|---------|
| `src/database/models.py` | Add `DatabaseConnection` |
| `src/database/connection.py` | Add `TenantConnectionManager` |
| `src/api/routes.py` | Add connection endpoints |
| `src/api/schemas.py` | Add Pydantic models |
| `src/agents/sql_agent.py` | Use dynamic schema |
| `src/utils/encryption.py` | Create (new) |
| `config/database.yaml` | Make tenant-aware |

## Legend

| Symbol | Meaning |
|--------|---------|
| ⬜ | Not started |
| 🔄 | In progress |
| ✅ | Completed |
| ❌ | Blocked |

---

*Created: 2026-01-15*
