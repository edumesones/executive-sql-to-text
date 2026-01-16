# Feature Development Cycle

## Objetivo

Este documento define el flujo de trabajo exacto para implementar cualquier feature en este proyecto. Siguiendo este ciclo se garantiza consistencia, trazabilidad y calidad.

---

## Resumen Visual

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FEATURE DEVELOPMENT CYCLE                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   1. INTERVIEW          2. PLAN            3. BRANCH         4. IMPLEMENT   │
│   ┌─────────┐          ┌─────────┐        ┌─────────┐       ┌─────────┐    │
│   │ Preguntas│   ───►  │ Explorar │  ───► │ git     │ ───►  │ Código  │    │
│   │ Decisiones│        │ Diseñar │        │ checkout│       │ Tests   │    │
│   │ spec.md  │         │ Plan.md │        │ -b      │       │ TodoWrite│   │
│   └─────────┘          └─────────┘        └─────────┘       └─────────┘    │
│                                                                    │        │
│                                                                    ▼        │
│   6. MERGE              5. PR              ◄────────────────────────        │
│   ┌─────────┐          ┌─────────┐                                          │
│   │ Review  │   ◄───   │ Push    │                                          │
│   │ Approve │          │ gh pr   │                                          │
│   │ Update  │          │ create  │                                          │
│   └─────────┘          └─────────┘                                          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Fase 1: INTERVIEW (Especificación)

### Propósito
Capturar TODAS las decisiones técnicas y de producto ANTES de escribir código.

### Cómo Iniciar
```
"Interview me about FEAT-XXX"
```

### Proceso

1. **Claude hace preguntas estructuradas** sobre:
   - UI/UX decisions
   - Comportamiento del sistema
   - Edge cases
   - Límites y restricciones
   - Integraciones

2. **El usuario responde con opciones claras**:
   - ✅ BIEN: "Import desde .env (DATABASE_URL format)"
   - ✅ BIEN: "Retry 3x automático + notificación"
   - ❌ MAL: "No sé, lo que tú creas"

3. **Claude actualiza el spec.md** con cada decisión en formato tabla:

```markdown
| Decisión | Valor |
|----------|-------|
| Connection UI | Import desde .env |
| SSL | Opciones: require / prefer / disable |
```

### Output
- `docs/features/FEAT-XXX/spec.md` actualizado con todas las decisiones

### Reglas del Interview
- Máximo 3-4 preguntas por turno
- Cada pregunta debe tener opciones sugeridas
- Si el usuario no sabe, Claude propone la opción más sensata
- Todas las decisiones se documentan inmediatamente

---

## Fase 2: PLAN (Diseño Técnico)

### Propósito
Diseñar la implementación ANTES de escribir código.

### Cómo Iniciar
```
/plan Implement FEAT-XXX
```

### Proceso

1. **Claude entra en modo plan** (solo lectura, no edita código)

2. **Exploración del codebase**:
   - Lee archivos relevantes (models.py, routes.py, etc.)
   - Identifica patrones existentes
   - Detecta dependencias

3. **Genera plan detallado** con:
   - Archivos a crear/modificar
   - Orden de implementación
   - Código de ejemplo (pseudocódigo o snippets)
   - Dependencias nuevas
   - Tests necesarios

4. **El usuario revisa y ajusta**:
   - Puede pedir cambios ("añade también MySQL")
   - Puede aprobar ("continua")

### Output
- Plan escrito en archivo `.claude/plans/xxx.md`
- Lista de tareas clara y ordenada

### Reglas del Plan
- NO se escribe código real en esta fase
- Solo lectura y análisis
- El usuario debe aprobar antes de implementar
- Si hay dudas, Claude pregunta ANTES de asumir

---

## Fase 3: BRANCH (Preparación)

### Propósito
Crear rama de trabajo ANTES de escribir código.

### ⚠️ CRÍTICO
```
NUNCA empezar a codear sin crear la rama primero.
```

### Proceso

1. **Verificar estado actual**:
```bash
git status
git branch
```

2. **Cambiar a rama principal y crear feature branch**:
```bash
git checkout master
git checkout -b feature/XXX-nombre-descriptivo
```

### Convención de Nombres
```
feature/001-core-db        ✅ (número + descripción corta)
feature/auth-basic         ✅ (sin número si no hay)
feat-001                   ❌ (muy corto)
nueva-feature              ❌ (no descriptivo)
```

### Output
- Nueva rama creada desde master
- Working directory limpio

---

## Fase 4: IMPLEMENT (Desarrollo)

### Propósito
Implementar el código siguiendo el plan.

### Proceso

1. **Inicializar TodoWrite** con todas las tareas del plan:
```
- Task 1: Create encryption utility
- Task 2: Add database models
- Task 3: Create API router
...
```

2. **Implementar en orden**:
   - Marcar tarea como `in_progress` ANTES de empezar
   - Completar tarea
   - Marcar como `completed` INMEDIATAMENTE después
   - Pasar a la siguiente

3. **Estructura de implementación típica**:
   1. Utilidades/helpers primero
   2. Modelos de datos
   3. Lógica de negocio
   4. API endpoints
   5. Integración con sistema existente
   6. Tests

### Reglas de Implementación

```
✅ HACER:
- Un archivo a la vez
- Commit mental por cada archivo completado
- Tests para cada módulo nuevo
- Seguir patrones existentes del codebase

❌ NO HACER:
- Implementar todo de golpe
- Saltarse el orden del plan
- Ignorar tests
- Inventar nuevos patrones sin justificación
```

### ⚠️ Documentación en Tiempo Real

**CRÍTICO**: La documentación se actualiza DURANTE la implementación, no al final.

| Momento | Acción | Archivo |
|---------|--------|---------|
| Al completar tarea | Marcar ⬜ → ✅ | `tasks.md` |
| Al terminar fase | Actualizar % | `status.md` |
| Antes de terminar sesión | Commit docs + código | Ambos |

```bash
# Ejemplo: después de completar T-001
# 1. Actualizar tasks.md
# 2. Actualizar status.md con nuevo %
# 3. git add docs/features/FEAT-XXX/
# 4. Continuar con siguiente tarea
```

**Anti-pattern**: Implementar todo → Actualizar docs al final → Olvidarse
**Correcto**: Tarea completada → Doc actualizada → Siguiente tarea

### Gestión de Dependencias

Seguir las instrucciones de `PYTHON_ENV.md`:
```bash
# Ver entorno
/d/gestoria_agentes/.venv/Scripts/python.exe -c "import sys; print(sys.executable)"

# Instalar dependencias
cd D:/gestoria_agentes
uv pip install nombre-paquete
```

### Output
- Código implementado
- Tests escritos
- TodoWrite 100% completado

---

## Fase 5: PR (Pull Request)

### Propósito
Preparar el código para review y merge.

### Proceso

1. **Verificar estado**:
```bash
git status
git diff --stat
```

2. **Stage solo archivos de la feature**:
```bash
git add src/... tests/... requirements.txt
# NO añadir archivos no relacionados
```

3. **Commit con mensaje descriptivo**:
```bash
git commit -m "$(cat <<'EOF'
Implement FEAT-XXX: Nombre Descriptivo

Descripción breve de qué hace la feature.

Features:
- Feature 1
- Feature 2
- Feature 3

New Files:
- path/to/new/file.py

Modified Files:
- path/to/modified/file.py

Tests:
- tests/unit/test_xxx.py
EOF
)"
```

4. **Push y crear PR**:
```bash
git push -u origin feature/XXX-nombre
gh pr create --title "FEAT-XXX: Nombre" --body "..." --base master
```

### Estructura del PR Body

```markdown
## Summary
[1-3 bullet points explicando QUÉ hace]

## Features Implemented
[Lista de checkboxes con cada feature]

## Files Changed
[Agrupar por: New Files, Modified Files, Tests]

## Test Results
[Resumen de tests pasados]

## Dependencies Added
[Si aplica]

## Next Steps After Merge
[Qué hay que hacer después: migrations, env vars, etc.]
```

### Output
- PR creado en GitHub
- URL del PR para review

---

## Fase 6: MERGE (Cierre)

### Propósito
Cerrar el ciclo y actualizar documentación.

### Proceso

1. **Review del PR** (por el usuario u otro dev)

2. **Aprobar y Merge** en GitHub

3. **Actualizar documentación**:
   - `docs/features/FEAT-XXX/status.md` → 🟢 Complete
   - `docs/features/_index.md` → Actualizar progreso

4. **Limpiar**:
```bash
git checkout master
git pull
git branch -d feature/XXX-nombre  # Borrar rama local
```

---

## Checklist Rápido

```
□ INTERVIEW
  □ Preguntas hechas
  □ Decisiones documentadas en spec.md
  □ Usuario confirmó decisiones

□ PLAN
  □ /plan ejecutado
  □ Codebase explorado
  □ Plan escrito y aprobado
  □ Lista de tareas clara

□ BRANCH
  □ git checkout master
  □ git checkout -b feature/XXX
  □ Rama creada ANTES de codear

□ IMPLEMENT
  □ TodoWrite inicializado
  □ Tareas en orden
  □ Tests escritos
  □ Dependencias instaladas
  □ Tests pasando

□ PR
  □ git add (solo archivos relevantes)
  □ git commit (mensaje descriptivo)
  □ git push -u origin
  □ gh pr create

□ MERGE
  □ PR aprobado
  □ Merged a master
  □ Documentación actualizada
  □ Rama local borrada
```

---

## Comandos Útiles

```bash
# Ver estado
git status
git log --oneline -5

# Crear rama
git checkout master && git checkout -b feature/XXX

# Ejecutar tests
/d/gestoria_agentes/.venv/Scripts/python.exe -m pytest tests/ -v --no-cov -p no:asyncio

# Instalar dependencias
cd D:/gestoria_agentes && uv pip install paquete

# Crear PR
gh pr create --title "..." --body "..." --base master

# Ver PRs
gh pr list
```

---

## Anti-Patterns (Qué NO Hacer)

| ❌ Anti-Pattern | ✅ Correcto |
|----------------|-------------|
| Empezar a codear sin interview | Siempre hacer interview primero |
| Empezar a codear sin rama | SIEMPRE crear rama antes |
| Codear sin plan | /plan primero, implementar después |
| Commits gigantes | Commits incrementales por módulo |
| Ignorar tests | Tests para cada módulo nuevo |
| PR sin descripción | PR con resumen detallado |
| Mezclar features | Una feature = una rama = un PR |
| Actualizar docs al final | Actualizar docs después de cada tarea |

---

## Tiempos Típicos

| Fase | Duración Típica |
|------|-----------------|
| Interview | 10-15 min |
| Plan | 15-30 min |
| Branch | 1 min |
| Implement | Variable (depende de complejidad) |
| PR | 5-10 min |
| Merge | 5 min |

---

## Ejemplo Real: FEAT-001

Este ciclo se usó para implementar FEAT-001 (Custom Database Connection):

1. **Interview**: 8 decisiones capturadas (SSL, retry, limits, etc.)
2. **Plan**: 11 tareas identificadas
3. **Branch**: `feature/001-core-db` desde master
4. **Implement**: 12 archivos, 1331 líneas, 9 tests
5. **PR**: #3 creado con descripción completa
6. **Merge**: Pendiente de review

**Resultado**: Feature completa, documentada, testeada y lista para merge.

---

*Última actualización: 2026-01-15*
*Basado en: Implementación de FEAT-001*
