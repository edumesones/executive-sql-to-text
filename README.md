# Executive Analytics Assistant - Lending Club Dataset

Sistema multi-agente con LangGraph para análisis conversacional de datos financieros dirigido a directivos que necesitan insights sin escribir SQL.

## 🎯 Características Principales

- **Lenguaje Natural a SQL**: Convierte preguntas en queries SQL validadas y seguras
- **Visualizaciones Interactivas**: Gráficos Plotly generados automáticamente según el contexto
- **Multi-Agente con LangGraph**: Orquestación inteligente de especialistas (SQL, Análisis, Visualización, Insights)
- **Memoria Conversacional**: PostgreSQL con contexto de sesiones anteriores
- **API REST + WebSocket**: Backend FastAPI con streaming de respuestas
- **Docker-Ready**: Setup completo en 2 minutos

## 📊 Dataset: Lending Club Loans

Dataset real de préstamos con +2M registros y 150+ features:
- `loan_amount`, `term`, `int_rate`, `grade`, `emp_length`
- `annual_inc`, `loan_status`, `purpose`, `dti`
- Casos de uso: análisis de riesgo, segmentación de clientes, proyecciones financieras

## 🏗️ Arquitectura

### Diagrama de Flujo Completo

![Arquitectura del Sistema](images/arquitectura.png)

### Agentes Especializados

1. **SQL Agent**: Genera queries SQL seguras (sin DROP/DELETE/UPDATE)
2. **Analyst Agent**: Valida resultados, calcula métricas adicionales
3. **Viz Agent**: Selecciona el tipo de gráfico óptimo (bar, line, scatter, heatmap)
4. **Insight Agent**: Genera insights de negocio y recomendaciones

## 🚀 Quick Start

### 1. Prerequisitos

```bash
# Windows
python --version  # 3.10+
docker --version
```

### 2. Setup

```bash
# Clonar y entrar al proyecto
cd D:\executive_sql_to_text

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Variables de entorno
copy .env.example .env
# Editar .env con tus API keys
```

### 3. Levantar servicios Docker

```bash
docker-compose up -d
```

Servicios disponibles:
- PostgreSQL: `localhost:5432`
- pgAdmin: `http://localhost:5050` (admin@example.com / admin)
- API: `http://localhost:8000` (después de correr la app)

### 4. Cargar datos

```bash
# Descargar dataset (primeras 100k filas para demo)
python scripts/download_data.py

# Cargar en PostgreSQL
python scripts/seed_database.py
```

### 5. Ejecutar aplicación

```bash
# Backend API
uvicorn src.api.main:app --reload --port 8000

# Frontend Streamlit (nueva terminal)
streamlit run frontend/streamlit_app.py
```

Acceder a: `http://localhost:8501`

## 📁 Estructura del Proyecto

```
executive_sql_to_text/
├── src/
│   ├── agents/              # Agentes especializados
│   │   ├── base_agent.py
│   │   ├── sql_agent.py
│   │   ├── analyst_agent.py
│   │   ├── viz_agent.py
│   │   └── insight_agent.py
│   ├── graph/               # LangGraph workflow
│   │   ├── state.py
│   │   ├── nodes.py
│   │   └── workflow.py
│   ├── tools/               # Herramientas reutilizables
│   │   ├── sql_executor.py
│   │   ├── chart_generator.py
│   │   └── metric_calculator.py
│   ├── database/            # Modelos y persistencia
│   │   ├── models.py
│   │   ├── connection.py
│   │   └── query_cache.py
│   └── api/                 # FastAPI backend
│       ├── main.py
│       ├── routes.py
│       └── websocket.py
├── frontend/
│   └── streamlit_app.py     # UI para directivos
├── data/
│   ├── raw/                 # CSVs descargados
│   └── processed/           # Datos limpios
├── scripts/
│   ├── download_data.py     # Descarga dataset
│   └── seed_database.py     # Carga en PostgreSQL
├── docker/
│   └── postgres/
│       └── init.sql         # Schema inicial
├── config/
│   ├── agents.yaml          # Configuración de agentes
│   └── database.yaml        # Configuración de DB
├── tests/
│   ├── unit/
│   └── integration/
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## 💬 Ejemplos de Preguntas

### Análisis de Riesgo
```
"¿Cuál es la tasa de default por grade de préstamo?"
"Muéstrame la distribución de loan_status"
"¿Qué factores predicen mejor el default?"
```

### Segmentación
```
"Segmenta clientes por annual_income y loan_amount"
"¿Cuáles son los perfiles de mayor riesgo?"
"Análisis de préstamos por purpose (debt_consolidation, credit_card, etc)"
```

### Proyecciones Financieras
```
"Proyecta ingresos por intereses del próximo trimestre"
"¿Qué grade tiene mejor ROI ajustado por riesgo?"
"Análisis de rentabilidad por term (36 vs 60 meses)"
```

### Operaciones
```
"¿Cuántos préstamos están en mora actualmente?"
"Tiempo promedio hasta el primer pago"
"Distribución geográfica de préstamos (por state)"
```

## 🔧 Configuración

### Variables de Entorno (.env)

```bash
# LLM API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Database
DATABASE_URL=postgresql://analyst:password@localhost:5432/lending_club
DB_PASSWORD=password

# API
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:8501,http://localhost:3000

# LangSmith (opcional para tracing)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__...
LANGCHAIN_PROJECT=executive-analytics
```

### Configuración de Agentes (config/agents.yaml)

```yaml
sql_agent:
  model: gpt-4o-mini
  temperature: 0.0
  max_retries: 3
  allowed_operations: [SELECT]
  
viz_agent:
  model: gpt-4o-mini
  temperature: 0.3
  chart_library: plotly
  default_theme: plotly_white
```

## 🧪 Testing

```bash
# Tests unitarios
pytest tests/unit -v

# Tests de integración (requiere Docker corriendo)
pytest tests/integration -v

# Coverage
pytest --cov=src tests/
```

## 📊 Schema de Base de Datos

### Tabla Principal: `loans`

```sql
CREATE TABLE loans (
    id SERIAL PRIMARY KEY,
    loan_amnt DECIMAL(10, 2),
    term VARCHAR(20),
    int_rate DECIMAL(5, 2),
    grade VARCHAR(1),
    sub_grade VARCHAR(2),
    emp_length VARCHAR(20),
    home_ownership VARCHAR(20),
    annual_inc DECIMAL(12, 2),
    verification_status VARCHAR(50),
    loan_status VARCHAR(50),
    purpose VARCHAR(50),
    dti DECIMAL(5, 2),
    delinq_2yrs INTEGER,
    earliest_cr_line DATE,
    open_acc INTEGER,
    pub_rec INTEGER,
    revol_bal DECIMAL(12, 2),
    revol_util DECIMAL(5, 2),
    total_acc INTEGER,
    addr_state VARCHAR(2),
    issue_d DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_loan_status ON loans(loan_status);
CREATE INDEX idx_grade ON loans(grade);
CREATE INDEX idx_issue_date ON loans(issue_d);
```

### Tabla de Conversaciones

```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL,
    user_query TEXT,
    sql_query TEXT,
    results JSONB,
    chart_config JSONB,
    insights TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🎨 Frontend Features

- **Chat Interface**: Conversación natural con el sistema
- **SQL Transparency**: Ver query generada (expandible)
- **Gráficos Interactivos**: Zoom, pan, hover tooltips
- **Exportación**: Descargar datos en CSV/Excel
- **Historial**: Acceso a consultas anteriores
- **Métricas en Tiempo Real**: KPIs destacados

## 🔐 Seguridad

- ✅ SQL Injection Protection: Queries parametrizadas con SQLAlchemy
- ✅ Solo operaciones SELECT permitidas
- ✅ Rate limiting en API (100 req/min por IP)
- ✅ Validación de schemas con Pydantic
- ✅ CORS configurado para dominios específicos

## 🚢 Deployment

### Docker Production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Variables para Producción

```bash
# .env.prod
DATABASE_URL=postgresql://user:pass@prod-db:5432/lending_club
OPENAI_API_KEY=sk-...
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=production
LOG_LEVEL=INFO
```

## 📈 Roadmap

- [ ] **Fase 1** (Actual): Sistema base funcional con 4 agentes
- [ ] **Fase 2**: Añadir agente de ML para predicciones (default risk)
- [ ] **Fase 3**: Benchmarking de modelos (GPT-4 vs Claude vs Llama)
- [ ] **Fase 4**: Multi-dataset support (añadir otros CSV)
- [ ] **Fase 5**: Autenticación y multi-tenancy

## 🤝 Contribución

Este es un proyecto de portfolio, pero sugerencias son bienvenidas:

1. Fork del repo
2. Crea branch (`git checkout -b feature/amazing`)
3. Commit (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing`)
5. Abre Pull Request

## 📄 Licencia

MIT License - ver `LICENSE` file

## 👤 Autor

**Glemes - GLEMES FFT (Focus Flow Tech)**
- Data Scientist & Python Expert
- Especialización: ML/AI para banca y retail
- LinkedIn: [tu-linkedin]
- Portfolio: [tu-portfolio]

---

**⭐ Si te resulta útil, dale una estrella al repo!**
