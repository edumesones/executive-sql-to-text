# FEAT-001: Data Ingestion Pipeline - Specification

## Overview

| Field | Value |
|-------|-------|
| **ID** | FEAT-001 |
| **Name** | OneDrive to PostgreSQL Data Ingestion |
| **Priority** | P0 |
| **Status** | Not Started |

## Problem Statement

> Los usuarios necesitan una forma sencilla de proporcionar sus datos (archivos CSV, Excel, JSON) para que la aplicación pueda trabajar con ellos. Actualmente no existe un mecanismo para transformar archivos raw en datos estructurados y consultables. Esta feature permite que el owner del producto ingeste los archivos depositados por usuarios en OneDrive y los convierta en tablas PostgreSQL.

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Conectar con OneDrive via API (OAuth2) para leer archivos de una carpeta específica | Must Have |
| FR-2 | Parsear archivos CSV con detección automática de delimitador y encoding | Must Have |
| FR-3 | Parsear archivos Excel (.xlsx, .xls) con soporte multi-sheet | Must Have |
| FR-4 | Parsear archivos JSON (arrays de objetos y objetos anidados nivel 1) | Must Have |
| FR-5 | Inferir automáticamente el schema (tipos de datos) de cada archivo | Must Have |
| FR-6 | Crear tablas en PostgreSQL basadas en el schema inferido | Must Have |
| FR-7 | Insertar datos con manejo de duplicados (upsert basado en primary key configurable) | Must Have |
| FR-8 | Generar logs de ingesta (archivos procesados, filas insertadas, errores) | Must Have |
| FR-9 | Soportar ingesta incremental (solo archivos nuevos/modificados) | Should Have |
| FR-10 | Permitir configurar mapping manual de columnas cuando la inferencia falle | Should Have |
| FR-11 | Validar datos antes de inserción (nulls, tipos, constraints) | Should Have |

### Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1 | Tiempo de procesamiento por archivo | < 30s para archivos < 100MB |
| NFR-2 | Memoria máxima por proceso | < 512MB (streaming para archivos grandes) |
| NFR-3 | Tasa de éxito de inferencia de schema | > 95% para formatos estándar |
| NFR-4 | Disponibilidad del proceso | Ejecutable on-demand sin downtime de app |

## User Stories
```
As the product owner
I want to ingest files from a user's OneDrive folder
So that the data becomes available in PostgreSQL for the application
```
```
As the product owner
I want to see a log of what was ingested
So that I can verify the process completed correctly and debug issues
```
```
As the product owner
I want the system to handle different file formats automatically
So that I don't need to write custom parsers for each user
```

## Acceptance Criteria

- [ ] Puede autenticarse con OneDrive y listar archivos de una carpeta configurada
- [ ] Procesa correctamente archivos CSV con diferentes delimitadores (, ; \t)
- [ ] Procesa correctamente archivos Excel con múltiples hojas (cada hoja = una tabla)
- [ ] Procesa correctamente archivos JSON (arrays de objetos planos)
- [ ] Crea tablas en PostgreSQL con nombres derivados del nombre del archivo
- [ ] Infiere tipos: string, integer, float, boolean, date, datetime
- [ ] No falla si un archivo tiene errores (lo reporta y continúa con los demás)
- [ ] Genera un reporte/log al finalizar con: archivos procesados, filas totales, errores
- [ ] Es idempotente: ejecutar dos veces no duplica datos

## Technical Design (High Level)
```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌────────────┐
│  OneDrive   │────▶│   Extractor  │────▶│ Transformer │────▶│  Loader    │
│  (Source)   │     │  (API/Auth)  │     │  (Schema)   │     │ (PostgreSQL)│
└─────────────┘     └──────────────┘     └─────────────┘     └────────────┘
                           │                    │                   │
                           ▼                    ▼                   ▼
                    ┌─────────────────────────────────────────────────┐
                    │                   Logger/Reporter                │
                    └─────────────────────────────────────────────────┘
```

### Componentes principales

| Componente | Responsabilidad | Tech Stack |
|------------|-----------------|------------|
| OneDrive Connector | Auth OAuth2, listar y descargar archivos | `msal`, `httpx` |
| File Parser | Detectar formato y parsear a DataFrame | `pandas`, `openpyxl` |
| Schema Inferrer | Detectar tipos de columnas | `pandas.dtypes`, custom rules |
| DB Loader | Crear tablas, insertar datos | `sqlalchemy`, `psycopg2` |
| Ingestion Logger | Registrar progreso y errores | `logging`, tabla en PostgreSQL |

### Configuración necesaria
```python
# config.yaml o .env
ONEDRIVE_CLIENT_ID=xxx
ONEDRIVE_CLIENT_SECRET=xxx
ONEDRIVE_TENANT_ID=xxx
ONEDRIVE_FOLDER_PATH=/Users/shared/data

POSTGRES_HOST=localhost
POSTGRES_DB=app_db
POSTGRES_USER=xxx
POSTGRES_PASSWORD=xxx

INGESTION_SCHEMA=raw_data  # Schema donde se crean las tablas
```

## Out of Scope

- Autenticación multi-usuario (cada usuario con su OneDrive) → FEAT-002
- Transformaciones complejas (joins, agregaciones) → Post-ingesta en app
- Otros cloud storage (Google Drive, S3, Dropbox) → Futuras features
- Scheduling automático (cron) → Puede añadirse después
- UI para visualizar estado de ingesta → CLI/logs por ahora

## Open Questions

1. ¿Cómo nombrar las tablas? ¿`{filename}` o `{username}_{filename}` para cuando haya multi-usuario?
2. ¿Qué hacer si un archivo se modifica? ¿Truncate + reload o merge inteligente?
3. ¿Límite de tamaño de archivo? (100MB? 500MB? 1GB?)
4. ¿El JSON anidado (nivel 2+) se aplana automáticamente o se guarda como JSONB?

## Dependencies

- Cuenta de Azure AD con app registration para OneDrive API
- Instancia PostgreSQL accesible
- Credenciales configuradas en entorno seguro

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Archivos con encoding raro fallan | Medio | Detectar encoding con `chardet`, fallback a UTF-8 con errores='replace' |
| Archivos muy grandes causan OOM | Alto | Implementar chunked reading con pandas |
| Rate limiting de OneDrive API | Bajo | Implementar retry con exponential backoff |
| Inferencia de tipos incorrecta | Medio | Permitir override manual via config por archivo |

---

*Created: 2025-01-15*