# FUVIA X — Estructura del Proyecto

```
/
├── backend/                          # API RESTful y lógica del lado del servidor
│   ├── main.py                       # Punto de entrada de FastAPI y definición de endpoints
│   ├── schemas.py                    # Modelos Pydantic para validación de datos (Input/Output)
│   ├── constants.py                  # Diccionarios de traducción y constantes del sistema
│   ├── pdf_service.py                # Motor de generación de reportes técnicos en PDF (FPDF)
│   ├── models/                       # Archivos serializados del modelo de Machine Learning (.pkl)
│   ├── venv/                         # Entorno virtual de Python (ignorado en .gitignore)
│   └── requirements.txt              # Manifiesto de dependencias del backend
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
│   │   │   ├── forms/
│   │   │   │   └── FormularioConcreto.tsx  # Interfaz principal de ingesta de parámetros
│   │   │   ├── layout/
│   │   │   │   └── Header.tsx              # Barra de navegación y branding (Logo)
│   │   │   ├── results/
│   │   │   │   ├── AbramsLineChart.tsx     # Renderizado de la Curva de Abrams (Recharts)
│   │   │   │   ├── MixPieChart.tsx         # Gráfico de composición volumétrica
│   │   │   │   └── PredictionResult.tsx    # Tarjeta de métricas inferidas por la IA
│   │   │   ├── tooltips/
│   │   │   │   └── AbramsTooltip.tsx       # Tooltips interactivos para visualización de datos
│   │   │   └── ui/
│   │   │       ├── NumberInput.tsx         # Componente atómico para captura de inputs numéricos
│   │   │       └── ValidationModal.tsx     # Modal de validación de resistencia en laboratorio
│   │   │
│   │   ├── constants/
│   │   │   └── concreteConstants.ts        # Variables de configuración global del frontend
│   │   ├── hooks/
│   │   │   └── useConcretePrediction.ts    # Custom Hook: controlador de estado y flujos de la UI
│   │   ├── services/
│   │   │   ├── predictionService.ts        # Cliente HTTP para comunicación con backend FUVIA
│   │   │   └── agentService.ts             # Cliente HTTP para comunicación con el agente (api.py)
│   │   ├── types/
│   │   │   └── concreteTypes.ts            # Definición de interfaces estrictas para TypeScript
│   │   └── utils/
│   │       ├── curvaAbrams.ts              # Motor de cálculo matemático para simulación de la curva
│   │       └── styleMappers.ts             # Lógica de renderizado dinámico según rangos de MPa
│   │
│   ├── App.tsx                       # Contenedor raíz de la aplicación
│   ├── index.css                     # Estilos globales y directivas de Tailwind CSS
│   ├── main.tsx                      # Punto de montaje del Virtual DOM
│   └── package.json                  # Manifiesto de dependencias y scripts de Node.js
│
└── README.md                         # Documentación técnica del proyecto
```

---

## Flujo de datos

```
Usuario
  ↓
frontend/src/components/forms/FormularioConcreto.tsx
  ↓ hook
frontend/src/hooks/useConcretePrediction.ts
  ↓ service
frontend/src/services/predictionService.ts → backend/main.py (puerto 8000)
                                           → CatBoost (.pkl) → PredictionResponse
  ↓ resultado
frontend/src/components/results/ (AbramsLineChart, MixPieChart, PredictionResult)
  ↓ trigger automático post-cálculo
frontend/src/services/agentService.ts → agent/api.py (puerto 8001)
  ↓
agent/agent.py (LangGraph)
  ├── agent/tools/rag_tool.py → agent/rag/query.py → agent/rag/chroma_db/
  └── agent/tools/fuvia_tool.py → backend/main.py /api/predecir
  ↓
ChatResponse { response, report, tools_called }
  ↓
frontend/src/components/chat/CopilotChat.tsx  ← componente a crear
```

---

## Variables de entorno

```bash
# .env (raíz del proyecto)

# Backend FUVIA
VITE_API_URL=http://localhost:8000

# Agente FUVIA X
VITE_AGENT_URL=http://localhost:8001
ANTHROPIC_API_KEY=sk-...
LLAMA_CLOUD_API_KEY=...
```

---

## Comandos de desarrollo

```bash
# Backend FUVIA (terminal 1)
cd backend && uvicorn main:app --reload --port 8000

# Agente FUVIA X (terminal 2)
cd agent && uvicorn api:app --reload --port 8001

# Frontend (terminal 3)
cd frontend && npm run dev
```
