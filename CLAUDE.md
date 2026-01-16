## 1. Qué es este proyecto
Executive SQL to Text - App para queries en lenguaje natural a DBs.
Stack: Python, FastAPI, SQLAlchemy, LangChain

## 2. Cómo trabajo
Sigo el ciclo en `docs/feature_cycle.md`:
Interview → Plan → Branch → Implement → PR → Merge

## 3. Estado actual
Ver `docs/features/_index.md` para dashboard completo.

## 4. Tu primer paso
1. Lee `docs/features/_index.md`
2. Identifica la primera feature ⚪ Pending o 🟡 In Progress
3. Si tiene spec.md y es una plantilla igual que el que hay en docs/features/template → "Interview me about FEAT-XXX"
4. Si tiene spec.md y es distinto de todos los demas spec.md → "/plan implement FEAT-XXX"

## 5. Reglas importantes
- NUNCA codear sin rama creada
- NUNCA implementar sin plan aprobado
- Commits incrementales por tarea
- Tests obligatorios


## 6. Regla de Documentación en Tiempo Real

⚠️ **CRÍTICO: Actualizar docs MIENTRAS se implementa, NO después**

Durante la Fase IMPLEMENT:
1. **Al completar cada tarea** → Actualizar `tasks.md` (⬜ → ✅)
2. **Al terminar cada fase** → Actualizar `status.md` (% progreso)
3. **Antes de terminar sesión** → Commit de docs + código

```
NUNCA terminar sesión con:
- Código implementado pero tasks.md sin actualizar
- Progreso real ≠ progreso documentado
```


## Reglas de Terminal

- NO uses `watch` ni comandos que refrescan infinitamente
- Usa `--no-pager` con git: `git diff --no-pager`
- Usa `-n` para limitar output: `git log -n 5`
- Evita `tail -f` o cualquier stream infinito
- Si un comando produce mucho output, redirige a archivo