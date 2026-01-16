# FEAT-XXX: [Feature Name] - Technical Design

## Architecture

### System Context

```
[Diagram or description of how this feature fits in the system]
```

### Component Design

| Component | Responsibility |
|-----------|---------------|
| [Component 1] | [What it does] |
| [Component 2] | [What it does] |

## Data Model

```sql
-- New tables or changes
CREATE TABLE example (
    id UUID PRIMARY KEY,
    ...
);
```

## API Design

```yaml
POST /api/endpoint:
  description: [What it does]
  request:
    field: type
  response:
    field: type
```

## Implementation Details

### Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `src/path/file.py` | Create | [Purpose] |
| `src/path/existing.py` | Modify | [Changes] |

### Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| [package] | [version] | [why needed] |

## Security Considerations

- [Security aspect 1]
- [Security aspect 2]

## Performance Considerations

- [Performance aspect 1]

## Error Handling

| Error Case | Handling |
|------------|----------|
| [Error 1] | [How to handle] |

---

*Created: YYYY-MM-DD*
