# Python Environment Configuration

**IMPORTANTE:** Este proyecto usa un entorno virtual compartido centralizado.

## Entorno Virtual

**Ubicación del entorno virtual:**
```
D:\gestoria_agentes\.venv
```

**Gestor de paquetes:** `uv`

## Ejecución de Python

### ✅ Forma Correcta de Ejecutar Python

Cuando necesites ejecutar código Python o instalar paquetes, **SIEMPRE** usa:

```bash
# Ejecutar scripts Python
/d/gestoria_agentes/.venv/Scripts/python.exe script.py

# O desde cualquier directorio
cd D:/mi_proyecto
/d/gestoria_agentes/.venv/Scripts/python.exe run.py
```

### ✅ Instalación de Paquetes

Para instalar paquetes nuevos, usa `uv` en el directorio del entorno:

```bash
cd D:/gestoria_agentes
uv pip install nombre-paquete
```

### ❌ NO Usar

- ❌ `python script.py` (usa el Python del sistema)
- ❌ `pip install paquete` (instala en el Python del sistema)
- ❌ Crear un nuevo entorno virtual en este proyecto
- ❌ `D:\lab_provectus\.venv` (no existe, es compartido)

## Verificar Paquetes Instalados

```bash
cd D:/gestoria_agentes
uv pip list
```

## Activar el Entorno (Opcional)

Si necesitas trabajar interactivamente:

```bash
# Windows
D:\gestoria_agentes\.venv\Scripts\activate
```

Después de activar, puedes usar `python` y `pip` normalmente.

## Filosofía del Entorno Compartido

Este proyecto usa un **entorno virtual centralizado** para:

1. **Evitar duplicación**: No reinstalar las mismas librerías en cada proyecto
2. **Ahorro de espacio**: Un solo lugar con todas las dependencias
3. **Gestión centralizada**: Actualizar librerías una sola vez
4. **Rapidez**: No esperar instalaciones repetidas

## Para Claude Code / IA Assistants

Cuando ejecutes código Python en este proyecto:

```bash
# ✅ CORRECTO
/d/gestoria_agentes/.venv/Scripts/python.exe -c "import numpy; print(numpy.__version__)"

# ✅ CORRECTO - Ejecutar script
/d/gestoria_agentes/.venv/Scripts/python.exe run_llm.py --llm openai --prompt "test"

# ❌ INCORRECTO
python script.py  # Esto usa el Python del sistema
```

## Dependencias de Este Proyecto

Las dependencias específicas de este proyecto están listadas en:
```
requirements.txt
```

Para instalarlas en el entorno compartido (si faltan):
```bash
cd D:/gestoria_agentes
uv pip install -r D:/lab_provectus/requirements.txt
```

## Troubleshooting

### Error: "ModuleNotFoundError"

Si falta un módulo:
```bash
cd D:/gestoria_agentes
uv pip install nombre-modulo
```

### Error: "python: command not found"

Usa la ruta completa al ejecutable:
```bash
/d/gestoria_agentes/.venv/Scripts/python.exe
```

### Verificar que estás usando el entorno correcto

```bash
/d/gestoria_agentes/.venv/Scripts/python.exe -c "import sys; print(sys.executable)"
```

Debería mostrar: `D:\gestoria_agentes\.venv\Scripts\python.exe`

## Variables de Entorno

Si necesitas configurar variables de entorno, usa un archivo `.env` en la raíz del proyecto.

Este proyecto ya tiene `.env` configurado con API keys.
