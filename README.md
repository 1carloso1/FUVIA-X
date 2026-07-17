<div align="center">

# FUVIA X | Plataforma de Inteligencia para Concreto

<img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React" />
<img src="https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript" />
<img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind CSS" />
<img src="https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white" alt="Vercel" />

<br />

<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
<img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
<img src="https://img.shields.io/badge/LangGraph-000000?style=for-the-badge&logo=langchain&logoColor=white" alt="LangGraph" />
<img src="https://img.shields.io/badge/ChromaDB-FF6B35?style=for-the-badge&logoColor=white" alt="ChromaDB" />
<img src="https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=white" alt="Render" />
<img src="https://img.shields.io/badge/CatBoost-FFD500?style=for-the-badge&logoColor=black" alt="CatBoost" />

<br /><br />

**FUVIA X** es una plataforma full-stack de ingeniería de concreto asistida por IA. Combina un modelo **CatBoost** para predicción de resistencia a compresión con un **agente LangGraph** que actúa como Copiloto normativo, consultando un stack de normas ACI/ASTM indexadas mediante RAG (Retrieval-Augmented Generation) para responder preguntas técnicas en lenguaje natural.

</div>

---

## 🚀 Prueba Rápida (Demo en Vivo)

1. Abre la aplicación: [👉 **FUVIA X Web App**](https://fuvia-x.vercel.app)
2. Espera a que ambos servidores despierten (pantalla de carga automática)
3. Ingresa una dosificación en el formulario y presiona **"Ejecutar Inferencia"**
4. El Copiloto te preguntará si deseas análisis normativo — responde **"Sí, analizar"**

⚙️ *El agente puede tardar 30-60 segundos en responder la primera vez. Los servidores en Render (plan gratuito) entran en modo suspensión por inactividad.*

---

## ✨ Características Principales

* **Predicción ML:** Estimación de f'c (MPa) con CatBoost entrenado en el dataset Yeh 1998 (1,030 muestras, 8 parámetros de mezcla)
* **Firewall Paramétrico:** 6 validaciones normativas antes de la inferencia (dominio Yeh, ACI 209R, ACI 318, ACI 211.1, ACI 212.3R, ASTM C494)
* **Copiloto IA (RAG):** Agente LangGraph con acceso a ACI 211.1-22, ACI 211.4R-08, ACI 318-19, ASTM C150, C33 y C494 indexados en ChromaDB
* **Análisis Visual:** Curva de Abrams, gráfico de composición volumétrica y métricas de mezcla
* **Reporte PDF:** Exportación técnica con captura de gráficas (html2canvas + FPDF)
* **Warm-up Automático:** Pantalla de carga que despierta ambos servidores Render antes de permitir interacción

---

## 🛠️ Arquitectura

### Frontend — `frontend/`
React 19 · TypeScript · Vite · Tailwind CSS · Recharts · html2canvas

### Backend FUVIA — `backend/`
FastAPI · CatBoost · Pandas · FPDF · Uvicorn

### Agente RAG — `agent/`
FastAPI · LangGraph · LangChain Anthropic · LlamaIndex · ChromaDB · BAAI/bge-small-en-v1.5 · BM25

---

## 🛠️ Guía de Instalación y Ejecución Local

Necesitarás **tres terminales** abiertas en PowerShell. Sigue el orden exacto.

---

### 🐍 1. Backend FUVIA (Puerto 8000)

```powershell
cd fuvia-x\backend

# Primera vez — crear entorno virtual
python -m venv venv

# Activar entorno
.\venv\Scripts\activate

# Primera vez — instalar dependencias
pip install -r requirements.txt

# Levantar servidor
uvicorn main:app --reload --port 8000
```

✅ Listo cuando veas: `Uvicorn running on http://127.0.0.1:8000`

---

### 🤖 2. Agente RAG (Puerto 8001)

#### Primera vez — construir la base de datos vectorial

El agente requiere indexar los documentos normativos en ChromaDB antes de correr por primera vez.

```powershell
cd fuvia-x\agent

# Crear entorno virtual del agente
python -m venv venv

# Activar entorno
.\venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Indexar documentos normativos (solo la primera vez o si cambias data_clean/)
# Tarda aproximadamente 5-10 minutos
python rag\ingest.py
```

✅ Listo cuando veas: `Indexación completada.`

> ⚠️ **Nota:** Si `rag\chroma_db\` ya existe, no es necesario correr `ingest.py` de nuevo. El índice persiste entre sesiones.

#### Levantar el agente

```powershell
# Desde fuvia-x\agent\ con el venv activado
uvicorn api:app --reload --port 8001
```

✅ Listo cuando veas:
```
INFO - Inicializando RAG y agente LangGraph...
INFO - Agente listo.
INFO - Application startup complete.
```

---

### ⚛️ 3. Frontend React (Puerto 5173)

```powershell
cd fuvia-x\frontend

# Primera vez — instalar dependencias
npm install

# Ejecutar en modo desarrollo
npm run dev
```

✅ Abre el navegador en: `http://localhost:5173`

---

### Variables de Entorno

Crea `fuvia-x\.env`:

```dotenv
ANTHROPIC_API_KEY=sk-ant-...
LLAMA_CLOUD_API_KEY=llx-...
VITE_AGENT_URL=http://localhost:8001
```

---

### Orden de arranque (resumen)

```
Terminal 1 → backend\    → uvicorn main:app --reload --port 8000
Terminal 2 → agent\      → uvicorn api:app --reload --port 8001
Terminal 3 → frontend\   → npm run dev
```

Espera a que las terminales 1 y 2 muestren "Application startup complete" antes de abrir el navegador.

---

## 🔄 Pipeline RAG — Construcción del Índice Normativo

Si necesitas re-indexar (por cambios en `data_clean/` o al migrar a otro equipo):

```powershell
cd fuvia-x\agent
.\venv\Scripts\activate

# Opcional: preprocesar PDFs nuevamente
python rag\preprocess_master.py

# Auditar calidad de tablas detectadas
python rag\audit_tables.py
# Revisa: rag\audit_report\audit_index.txt

# Re-indexar en ChromaDB
Remove-Item -Recurse -Force rag\chroma_db
python rag\ingest.py

# Verificar que el RAG responde correctamente
python rag\query.py
```

### Stack normativo indexado

| Documento | Versión | Contenido |
|---|---|---|
| ACI 211.1 | -22 | Dosificación concreto normal |
| ACI 211.4R | -08 | Dosificación alta resistencia |
| ACI 318-19 | -19 | Requisitos estructurales y durabilidad (caps. 2,9,10,18,19,26) |
| ASTM C150 | /C150M-22 | Cemento Portland |
| ASTM C33 | /C33M-13 | Agregados |
| ASTM C494 | /C494M-19 | Aditivos químicos |

---

## ☁️ Despliegue en Producción

### Frontend → Vercel

- **Root Directory:** `frontend`
- **Framework:** Vite (detección automática)
- **Environment Variables en Vercel:**
  ```
  VITE_API_URL=https://firmitas-ai.onrender.com
  VITE_AGENT_URL=https://tu-agente.onrender.com
  ```

### Backend FUVIA → Render (servicio existente)

- URL: `https://firmitas-ai.onrender.com`
- Root Directory: `backend`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Agente RAG → Render (servicio nuevo)

- Root Directory: `agent`
- Start Command: `uvicorn api:app --host 0.0.0.0 --port $PORT`
- Environment Variables en Render:
  ```
  ANTHROPIC_API_KEY=sk-ant-...
  LLAMA_CLOUD_API_KEY=llx-...
  ```

> ⚠️ En Render, `chroma_db/` no persiste entre deploys. El `lifespan` de `api.py` detecta si no existe y corre `ingest.py` automáticamente. El primer deploy puede tardar 10-15 minutos.

### CORS

Ambos `main.py` y `api.py` deben incluir la URL exacta de Vercel:

```python
origins = [
    "http://localhost:5173",
    "https://fuvia-x.vercel.app",
]
```

---

## 📄 Paper Publicado

**"AI-Based Inference System for Concrete Compressive Strength"**  
MDPI Applied Sciences · Noviembre 2025  
DOI: [10.3390/app152312383](https://doi.org/10.3390/app152312383)

## Estructura del Proyecto

```
/
├── backend/                          # API RESTful y lógica del lado del servidor
│   ├── main.py                       # Punto de entrada de FastAPI y definición de endpoints
│   ├── schemas.py                    # Modelos Pydantic para validación de datos (Input/Output)
│   ├── constants.py                  # Diccionarios de traducción y constantes del sistema
│   ├── pdf_service.py                # Motor de generación de reportes técnicos en PDF (FPDF)
│   └── models/                       # Archivos del modelo de Machine Learning (.joblib)
│
├── agent/                            # Agente conversacional de IA (FUVIA X Copiloto)
│   ├── agent.py                      # Grafo LangGraph: orquesta herramientas RAG y FUVIA
│   ├── api.py                        # FastAPI que expone el agente al frontend (POST /api/chat)
│   ├── prompts.py                    # Prompts del sistema: AGENT_SYSTEM_PROMPT y REPORT_SYNTHESIS_PROMPT
│   ├── requirements.txt              # Dependencias del agente (LangGraph, LlamaIndex, ChromaDB, etc.)
│   │
│   ├── rag/                          # Pipeline RAG sobre stack normativo ACI/ASTM
│   │   ├── chroma_db/                # Base de datos vectorial (generada por ingest.py, no en git)
│   │   ├── data_clean/               # Documentos normativos preprocesados por preprocess_master.py
│   │   │   ├── ACI_211.1-22/         # Dosificación concreto normal — un .txt por página
│   │   │   ├── ACI_211.4R-08/        # Dosificación concreto alta resistencia — un .txt por página
│   │   │   ├── ACI_318-19_selected/  # Requisitos estructurales caps. 2,9,10,18,19,26 — un .txt por página
│   │   │   ├── ASTM_C150-22/         # Especificaciones cemento Portland — un .txt por página
│   │   │   ├── ASTM_C33-13/          # Especificaciones agregados — un .txt por página
│   │   │   └── ASTM_C494-19/         # Especificaciones aditivos químicos — un .txt por página
│   │   ├── ingest.py                 # Indexa data_clean/ en ChromaDB con embeddings bge-small-en
│   │   ├── preprocess_master.py      # Preprocesa PDFs: detecta layout, etiqueta CODE/COMMENTARY, enriquece tablas
│   │   └── query.py                  # Motor de consulta RAG: retriever híbrido BM25 + semántico + traducción ES/EN
│   │
│   └── tools/                        # Herramientas LangChain para el agente LangGraph
│       ├── __init__.py               # Inicializador del módulo tools
│       ├── rag_tool.py               # Wrapper de query.py como herramienta LangChain (@tool)
│       └── fuvia_tool.py             # Wrapper del endpoint /api/predecir de FUVIA como herramienta LangChain
│
├── frontend/                         # Aplicación cliente (React + TypeScript + Vite)
│   ├── src/
│   │   ├── components/               # Arquitectura basada en componentes reutilizables
│   │   │   ├── chat/
│   │   │   │   └── CopilotChat.tsx         # Panel conversacional del Copiloto FUVIA X
│   │   │   ├── layout/
│   │   │   │   ├── Header.tsx              # Barra de navegación y branding minimalista
│   │   │   │   ├── MainLayout.tsx          # Layout principal: carrusel (formulario/resultados) + copiloto
│   │   │   │   └── WarmupScreen.tsx        # Pantalla de carga durante activación de servidores Render
│   │   │   ├── results/
│   │   │   │   ├── AbramsLineChart.tsx     # Curva de Abrams — tema claro (usado en PDF)
│   │   │   │   ├── AbramsLineChartDark.tsx # Curva de Abrams — tema oscuro (usado en UI)
│   │   │   │   ├── MixPieChart.tsx         # Composición volumétrica — tema claro (usado en PDF)
│   │   │   │   ├── MixPieChartDark.tsx     # Composición volumétrica — tema oscuro (usado en UI)
│   │   │   │   └── PredictionResultDark.tsx # Métricas de predicción — tema oscuro
│   │   │   ├── tooltips/
│   │   │   │   └── AbramsTooltip.tsx       # Tooltip interactivo para la Curva de Abrams
│   │   │   └── ui/
│   │   │       ├── NumberInput.tsx         # Input numérico — tema claro (legado)
│   │   │       ├── NumberInputDark.tsx     # Input numérico — tema oscuro
│   │   │       └── ValidationModal.tsx     # Modal de validación experimental de resistencia
│   │   │
│   │   ├── constants/
│   │   │   └── concreteConstants.ts        # Estado inicial y constantes del formulario
│   │   ├── hooks/
│   │   │   ├── useAgentChat.ts             # Estado del chat: mensajes, confirmación de análisis, stop
│   │   │   ├── useConcretePrediction.ts    # Estado del formulario, predicción y generación de PDF
│   │   │   └── useSystemWarmup.ts          # Warm-up paralelo de backend y agente al iniciar
│   │   ├── services/
│   │   │   ├── agentService.ts             # Cliente HTTP para el agente LangGraph (api.py)
│   │   │   └── predictionService.ts        # Cliente HTTP para el backend FUVIA (CatBoost)
│   │   ├── types/
│   │   │   └── concreteTypes.ts            # Interfaces TypeScript: ConcreteInputData, PredictionResponse
│   │   └── utils/
│   │       ├── curvaAbrams.ts              # Generación matemática de puntos para la Curva de Abrams
│   │       └── styleMappers.ts             # Mapeo de clases Tailwind según clase de resistencia (dark/light)
│   │
│   ├── App.tsx                       # Contenedor raíz: gate de warmup → WarmupScreen | MainLayout
│   ├── index.css                     # Estilos globales y directivas de Tailwind CSS
│   ├── main.tsx                      # Punto de montaje del Virtual DOM
│   └── package.json                  # Manifiesto de dependencias y scripts de Node.js
│
└── README.md                         # Documentación técnica del proyecto
```

---
