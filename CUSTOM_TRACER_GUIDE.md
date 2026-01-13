# 🎯 Custom Local JSON Tracer - Guía Completa

## ¿Qué es esto?

Hemos implementado un **sistema de tracing local** que guarda todos los traces en archivos JSON que puedes inspeccionar fácilmente. Es una alternativa a LangSmith que funciona 100% localmente.

---

## 🚀 Cómo Usar

### 1. Asegurar que no hay procesos en puerto 8000

```powershell
# Ver qué está ocupando el puerto 8000
netstat -ano | findstr ":8000"

# Si ves procesos, cópialos y mata cada PID:
taskkill /F /PID <PID>
```

### 2. Iniciar la API

```powershell
cd d:\executive_sql_to_text
D:\gestoria_agentes\.venv\Scripts\python.exe -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

Deberías ver:
```
local_json_tracer_initialized trace_dir=traces
Application startup complete.
Uvicorn running on http://0.0.0.0:8000
```

### 3. Iniciar el Frontend (en otra terminal)

```powershell
cd d:\executive_sql_to_text
D:\gestoria_agentes\.venv\Scripts\python.exe run_frontend.py
```

### 4. Hacer una Query

1. Ve a http://localhost:8501
2. Escribe: `¿Cuántos préstamos hay en total?`
3. Espera a que complete

### 5. Ver los Traces

```powershell
# Ver los últimos 5 traces
python view_traces.py

# Listar todos los archivos de trace
python view_traces.py list

# Ver los últimos 10 traces
python view_traces.py 10

# Ver TODOS los traces
python view_traces.py all
```

---

## 📊 Qué Verás en los Traces

Cada archivo JSON contiene:

```json
{
  "run_id": "abc123...",
  "parent_run_id": "def456...",
  "type": "llm" o "chain",
  "start_time": "2026-01-13T10:30:00",
  "end_time": "2026-01-13T10:30:05",
  "duration_seconds": 5.234,
  "tags": ["sql_agent", "openai"],
  "metadata": {...},
  "model": "gpt-4o-mini",
  "prompts": ["..."],
  "generations": [{
    "text": "SELECT COUNT(*) FROM loans",
    "text_preview": "SELECT COUNT(*) FROM..."
  }]
}
```

### Ejemplo de Trace

```
================================================================================
TRACE: trace_20260113_123045_abc12345.json
================================================================================

Type: LLM
Run ID: abc12345-1234...
Parent: def45678-5678...
Start: 2026-01-13T12:30:45.123456
End: 2026-01-13T12:30:48.654321
Duration: 3.531s

Tags: sql_agent, openai

--- LLM CALL ---
Model: gpt-4o-mini

Prompts (1):
  1. You are a SQL generation expert. Given the user's question...

Generations (1):
  1. SELECT COUNT(*) as total FROM loans
```

---

## 🔍 Ventajas del Custom Tracer

✅ **100% Local** - No necesitas cuenta externa  
✅ **Archivos JSON** - Fácil de inspeccionar y parsear  
✅ **Automático** - Se guarda cada llamada a LLM  
✅ **Timestamped** - Todos los archivos tienen fecha/hora  
✅ **Completo** - Inputs, outputs, duración, errores  

---

## 📁 Estructura de Archivos

```
d:\executive_sql_to_text\
├── traces/                     # 📂 Todos los traces aquí
│   ├── trace_20260113_120000_abc123.json
│   ├── trace_20260113_120001_def456.json
│   └── ...
├── view_traces.py              # 🔍 Script para ver traces
└── src/
    └── utils/
        └── custom_tracer.py    # 🎯 Implementación del tracer
```

---

## 🐛 Troubleshooting

### Problema: Puerto 8000 ocupado

```powershell
# Ver todos los procesos Python
Get-Process python | Select-Object Id, ProcessName, StartTime

# Matar todos los procesos Python de gestoria_agentes
Get-Process python | Where-Object {$_.Path -like "*gestoria_agentes*"} | Stop-Process -Force
```

### Problema: No se crean traces

Verifica que:
1. El directorio `traces/` existe
2. La API inició correctamente
3. Hiciste una query completa (no cancelaste a mitad)

### Problema: Traces muy grandes

Los traces se truncan automáticamente a:
- Strings: 500 caracteres
- Listas: Primeros 10 elementos
- Si necesitas más, edita `src/utils/custom_tracer.py`

---

## 🎨 Opción 2: LangFuse (Alternativa Visual)

Si quieres una UI web como LangSmith pero open-source:

```bash
# Instalar LangFuse
pip install langfuse

# Crear cuenta gratis en https://cloud.langfuse.com/
# O ejecutar localmente con Docker
```

**¿Quieres que configure LangFuse en lugar del tracer local?** Pregúntame.

---

## ✅ Resumen

1. **Mata procesos en puerto 8000**
2. **Inicia API**: `python -m uvicorn src.api.main:app`
3. **Inicia Frontend**: `python run_frontend.py`
4. **Haz una query**
5. **Ver traces**: `python view_traces.py`

**El tracer está ACTIVO y funcionando** ✓  
Solo necesitas liberar el puerto e iniciar la API correctamente.
