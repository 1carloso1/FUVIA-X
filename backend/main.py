from contextlib import asynccontextmanager
from fastapi import Depends
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pdf_service import generar_pdf_bytes
from schemas import ConcretoInput, ConcretoOutput, ReporteRequest
import joblib
import pandas as pd
import numpy as np
import shap
import os
from constants import (
    RANGOS_CONCRETO,
    RANGOS_RELACION_AC,
    RANGOS_RELACION_GA,
    RATIO_GRAVA_ARENA_MIN,
    RATIO_GRAVA_ARENA_MAX,
    LIMITE_EDAD_MIN,
    LIMITE_EDAD_MAX,
    LIMITE_VOLUMEN_MIN,
    LIMITE_VOLUMEN_MAX,
    LIMITE_WCM_MIN,
    LIMITE_WCM_MAX,
    LIMITE_ADITIVO_MAX,
    YEH_BOUNDARIES
)
from database import create_db_and_tables, get_session, InferenceRecord
from sqlmodel import Session

# Nombres de features en el mismo orden de entrenamiento — usados para el output SHAP
FEATURE_NAMES = [
    "Cement",
    "Blast Furnace Slag",
    "Fly Ash",
    "Water",
    "Superplasticizer",
    "Coarse Aggregate",
    "Fine Aggregate",
    "Age",
]

# Diccionario global para almacenar modelos cargados de forma segura
ml_models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Lógica de Arranque (Startup) ---
    create_db_and_tables()
    ruta_modelo = "models/cb_model.joblib"
    if os.path.exists(ruta_modelo):
        model = joblib.load(ruta_modelo)
        ml_models["predictor"] = model
        # Crear el explainer SHAP una sola vez — TreeExplainer es O(ms) por fila
        ml_models["explainer"] = shap.TreeExplainer(model)
        print(f"Modelo y explainer SHAP cargados correctamente desde {ruta_modelo}.")
    else:
        print(f"ALERTA: No hay modelo en la ruta {ruta_modelo}.")

    yield  # Aquí la aplicación se queda corriendo y recibiendo peticiones

    # --- Lógica de Apagado (Shutdown) ---
    ml_models.clear()
    print("Memoria liberada. Modelo y explainer descargados.")


# Inicializamos FastAPI inyectando el lifespan
app = FastAPI(title="Sistema de Predicción de Concreto - DB: Yeh", lifespan=lifespan)

# ORÍGENES EXACTOS
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://fuvia-x.vercel.app",
    "https://fuvia-x.vercel.app/",
]

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def interpretar_resistencia(mpa: float):
    for rango in RANGOS_CONCRETO:
        if rango["min"] <= mpa < rango["max"]:
            return rango["etiqueta"], rango["usos"]
    return "Resistencia Desconocida", ["Consultar a un ingeniero estructural"]


def interpretar_ga(ratio_ga: float):
    for rango in RANGOS_RELACION_GA:
        if rango["min"] <= ratio_ga < rango["max"]:
            return rango["etiqueta"], rango["descripcion"], rango["caracteristicas"]
    return "Desconocida", "Fuera de rango", ["Sin datos"]


def interpretar_ac(ratio: float):
    for rango in RANGOS_RELACION_AC:
        if rango["min"] <= ratio < rango["max"]:
            return rango["etiqueta"], rango["descripcion"], rango["caracteristicas"]
    return "Relación Desconocida", "Fuera de rango estándar", ["Consultar a un ingeniero estructural"]


@app.post("/api/predecir", response_model=ConcretoOutput)
def predecir_resistencia(datos: ConcretoInput):
    model    = ml_models.get("predictor")
    explainer = ml_models.get("explainer")

    if model is None:
        raise HTTPException(status_code=500, detail="El modelo de IA no está disponible en el servidor.")

    try:
        # ==========================================================
        # FASE 0: VALIDACIÓN DEL DOMINIO DE APLICABILIDAD (YEH)
        # ==========================================================
        datos_dict = datos.model_dump()

        for campo, limites in YEH_BOUNDARIES.items():
            valor_ingresado = datos_dict.get(campo)
            if valor_ingresado < limites["min"] or valor_ingresado > limites["max"]:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "campos": [campo],
                        "mensaje": (
                            f"Fuera del Dominio de Aplicabilidad: El valor de {limites['name']} "
                            f"({valor_ingresado} kg/m³) excede las fronteras del modelo de IA "
                            f"({limites['min']} a {limites['max']} kg/m³). "
                            f"Riesgo de extrapolación detectado (Ref: I.C. Yeh, 1998)."
                        ),
                    },
                )

        # ==========================================================
        # FASE 1: CÁLCULO DE PROPORCIONES FÍSICAS Y QUÍMICAS
        # ==========================================================
        ratio_grava_arena = (datos.coarseaggregate / datos.fineaggregate) if datos.fineaggregate > 0 else 0.0
        material_cementante = datos.cement + datos.slag + datos.flyash
        peso_total = (
            datos.cement + datos.slag + datos.flyash
            + datos.water + datos.superplasticizer
            + datos.coarseaggregate + datos.fineaggregate
        )
        ratio_wcm  = (datos.water / material_cementante) if material_cementante > 0 else 0.0
        dosis_sp   = (datos.superplasticizer / material_cementante * 100) if material_cementante > 0 else 0.0

        # ==========================================================
        # FASE 2: BARRERAS DE SEGURIDAD (NORMATIVAS ACI/ASTM)
        # ==========================================================
        if datos.age < LIMITE_EDAD_MIN or datos.age > LIMITE_EDAD_MAX:
            raise HTTPException(
                status_code=400,
                detail={
                    "campos": ["age"],
                    "mensaje": (
                        f"Extrapolación temporal: La edad ingresada es inválida. "
                        f"El modelo predictivo asintótico se restringe al periodo de "
                        f"{LIMITE_EDAD_MIN} a {LIMITE_EDAD_MAX} días (Ref: ACI 209R)."
                    ),
                },
            )

        if peso_total < LIMITE_VOLUMEN_MIN or peso_total > LIMITE_VOLUMEN_MAX:
            raise HTTPException(
                status_code=400,
                detail={
                    "campos": ["cement", "slag", "flyash", "water", "superplasticizer", "coarseaggregate", "fineaggregate"],
                    "mensaje": (
                        f"Inviabilidad física: Un metro cúbico de concreto normal debe pesar entre "
                        f"{LIMITE_VOLUMEN_MIN} y {LIMITE_VOLUMEN_MAX} kg. Su diseño suma "
                        f"{round(peso_total, 3)} kg, lo que implica un error de rendimiento "
                        f"volumétrico (Ref: ACI 318)."
                    ),
                },
            )

        if ratio_wcm < LIMITE_WCM_MIN or ratio_wcm > LIMITE_WCM_MAX:
            raise HTTPException(
                status_code=400,
                detail={
                    "campos": ["water", "cement", "slag", "flyash"],
                    "mensaje": (
                        f"Fuera de dominio químico: La relación Agua/Material-Cementante calculada "
                        f"({round(ratio_wcm, 3)}) es inválida. La estequiometría exige un mínimo de "
                        f"{LIMITE_WCM_MIN}, y superar {LIMITE_WCM_MAX} causa segregación severa "
                        f"(Ref: ACI 211.1)."
                    ),
                },
            )

        if dosis_sp > LIMITE_ADITIVO_MAX:
            raise HTTPException(
                status_code=400,
                detail={
                    "campos": ["superplasticizer", "cement", "slag", "flyash"],
                    "mensaje": (
                        f"Sobredosis de aditivo: El superplastificante es el {round(dosis_sp, 3)}% "
                        f"del peso cementante. Superar el {LIMITE_ADITIVO_MAX}% provoca retardo "
                        f"crítico de fraguado y exceso de aire atrapado (Ref: ACI 212.3R / ASTM C494)."
                    ),
                },
            )

        if ratio_grava_arena < RATIO_GRAVA_ARENA_MIN or ratio_grava_arena > RATIO_GRAVA_ARENA_MAX:
            raise HTTPException(
                status_code=400,
                detail={
                    "campos": ["coarseaggregate", "fineaggregate"],
                    "mensaje": (
                        f"Fuera de dominio algorítmico: La relación Grava/Arena calculada "
                        f"({round(ratio_grava_arena, 3)}) es inválida. La relación se debe mantener "
                        f"entre {round(RATIO_GRAVA_ARENA_MIN, 3)} y {round(RATIO_GRAVA_ARENA_MAX, 3)} "
                        f"para evitar sobresaturación extrema de agregados finos o gruesos "
                        f"(Ref: I.C. Yeh, 1998)."
                    ),
                },
            )

        # ==========================================================
        # FASE 3: PREDICCIÓN ML Y GENERACIÓN DE RESULTADOS
        # ==========================================================
        columnas_entrenamiento = [
            "cement", "slag", "flyash", "water",
            "superplasticizer", "coarseaggregate", "fineaggregate", "age",
        ]
        datos_dict = datos.model_dump()
        df_input   = pd.DataFrame(
            [[datos_dict[col] for col in columnas_entrenamiento]],
            columns=columnas_entrenamiento,
        )

        # Predicción
        prediccion = float(model.predict(df_input)[0])

        # ==========================================================
        # FASE 4: CÁLCULO SHAP
        # Solo se ejecuta si el explainer está disponible y la predicción fue exitosa.
        # TreeExplainer sobre una fila única agrega ~2–5 ms al tiempo de respuesta.
        # ==========================================================
        shap_base_value    = 0.0
        shap_contributions = []

        if explainer is not None:
            shap_vals = explainer.shap_values(df_input)
            # shap_vals es un array (1, 8); tomamos la primera (y única) fila
            vals_row = shap_vals[0] if isinstance(shap_vals, np.ndarray) else shap_vals[0][0]

            shap_base_value = float(explainer.expected_value)

            # Construir lista ordenada de mayor a menor contribución absoluta
            contributions = [
                {"feature": FEATURE_NAMES[i], "value": round(float(vals_row[i]), 4)}
                for i in range(len(FEATURE_NAMES))
            ]
            shap_contributions = sorted(contributions, key=lambda x: abs(x["value"]), reverse=True)

        # Interpretaciones
        clase, uso                           = interpretar_resistencia(prediccion)
        clase_ga, desc_ga, caracteristicas_ga = interpretar_ga(ratio_grava_arena)
        clase_ac, desc_ac, caracteristicas_ac = interpretar_ac(ratio_wcm)

        return {
            "resistencia_estimada":  round(prediccion, 3),
            "relacion_grava_arena":  round(ratio_grava_arena, 3),
            "relacion_agua_cemento": round(ratio_wcm, 3),
            "clase_resistencia":     clase,
            "recomendaciones":       uso,
            "clase_ga":              clase_ga,
            "descripcion_ga":        desc_ga,
            "caracteristicas_ga":    caracteristicas_ga,
            "clase_ac":              clase_ac,
            "descripcion_ac":        desc_ac,
            "caracteristicas_ac":    caracteristicas_ac,
            "mensaje":               "Cálculo exitoso",
            "shap_base_value":       round(shap_base_value, 3),
            "shap_contributions":    shap_contributions,
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generar-reporte")
async def generar_reporte_endpoint(
    datos: ReporteRequest,
    session: Session = Depends(get_session),
):
    try:
        is_valid  = datos.resistencia_real is not None
        error_abs = None
        error_rel = None

        if is_valid:
            error_abs = abs(datos.prediccion.resistencia_estimada - datos.resistencia_real)
            if datos.resistencia_real > 0:
                error_rel = (error_abs / datos.resistencia_real) * 100
            else:
                error_rel = 0.0

        nuevo_registro = InferenceRecord(
            cement=datos.inputs.cement,
            slag=datos.inputs.slag,
            flyash=datos.inputs.flyash,
            water=datos.inputs.water,
            superplasticizer=datos.inputs.superplasticizer,
            coarseaggregate=datos.inputs.coarseaggregate,
            fineaggregate=datos.inputs.fineaggregate,
            age=datos.inputs.age,
            predicted_strength=datos.prediccion.resistencia_estimada,
            real_strength=datos.resistencia_real,
            absolute_error=error_abs,
            relative_error=error_rel,
            is_validated=is_valid,
        )
        session.add(nuevo_registro)
        session.commit()

        pdf_bytes = generar_pdf_bytes(datos, is_valid, error_abs, error_rel)
        return Response(content=pdf_bytes, media_type="application/pdf")

    except Exception as e:
        print(f"Error generando PDF o guardando DB: {e}")
        raise HTTPException(status_code=500, detail="Error al generar el documento PDF")


@app.get("/api/health")
def health():
    return {"status": "ok"}