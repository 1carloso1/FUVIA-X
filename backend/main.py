from contextlib import asynccontextmanager
from fastapi import Depends
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pdf_service import generar_pdf_bytes
from schemas import ConcretoInput, ConcretoOutput, ReporteRequest
import joblib
import pandas as pd
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

# Diccionario global para almacenar modelos cargados de forma segura
ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Lógica de Arranque (Startup) ---
    create_db_and_tables()
    ruta_modelo = "models/cb_model.joblib"
    if os.path.exists(ruta_modelo):
        ml_models["predictor"] = joblib.load(ruta_modelo)
        print(f"Modelo cargado correctamente desde {ruta_modelo}.")
    else:
        print(f"ALERTA: No hay modelo en la ruta {ruta_modelo}.")
    
    yield # Aquí la aplicación se queda corriendo y recibiendo peticiones
    
    # --- Lógica de Apagado (Shutdown) ---
    ml_models.clear()
    print("Memoria liberada. Modelo descargado.")

# Inicializamos FastAPI inyectando el lifespan
app = FastAPI(title="Sistema de Predicción de Concreto - DB: Yeh", lifespan=lifespan)

# ORÍGENES EXACTOS
origins = [
    "http://localhost:5173",             
    "http://localhost:3000",             
    "https://fuvia.vercel.app",    
    "https://fuvia.vercel.app/"    
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
    # Extraemos el modelo del diccionario de memoria
    model = ml_models.get("predictor")
    
    if model is None:
        raise HTTPException(status_code=500, detail="El modelo de IA no está disponible en el servidor.")

    try: 
        # ==========================================================
        # FASE 0: VALIDACIÓN DEL DOMINIO DE APLICABILIDAD (YEH)
        # ==========================================================
        datos_dict = datos.model_dump() # Extraemos el esquema Pydantic
        
        for campo, limites in YEH_BOUNDARIES.items():
            valor_ingresado = datos_dict.get(campo)
            
            # Verificamos si el valor rompe la frontera matemática
            if valor_ingresado < limites["min"] or valor_ingresado > limites["max"]:

                raise HTTPException(
                    status_code=400, 
                    detail={
                        "campos": [campo],
                        "mensaje": f"Fuera del Dominio de Aplicabilidad: El valor de {limites['name']} ({valor_ingresado} kg/m³) excede las fronteras del modelo de IA ({limites['min']} a {limites['max']} kg/m³). Riesgo de extrapolación detectado (Ref: I.C. Yeh, 1998)."
                    }
                )
        # ==========================================================
        # FASE 1: CÁLCULO DE PROPORCIONES FÍSICAS Y QUÍMICAS
        # ==========================================================
        
        # 1.1 Relación Grava / Arena
        ratio_grava_arena = (datos.coarseaggregate / datos.fineaggregate) if datos.fineaggregate > 0 else 0.0

        # 1.2 Material Cementante Total (w/cm) y Rendimiento Volumétrico
        material_cementante = datos.cement + datos.slag + datos.flyash
        peso_total = (datos.cement + datos.slag + datos.flyash + 
                      datos.water + datos.superplasticizer + 
                      datos.coarseaggregate + datos.fineaggregate)

        # 1.3 Relación Agua / Material Cementante
        ratio_wcm = (datos.water / material_cementante) if material_cementante > 0 else 0.0
            
        # 1.4 Porcentaje de Superplastificante (%)
        dosis_sp = (datos.superplasticizer / material_cementante * 100) if material_cementante > 0 else 0.0

        # ==========================================================
        # FASE 2: BARRERAS DE SEGURIDAD (NORMATIVAS ACI/ASTM)
        # ==========================================================

        # A) Límite de Edad
        if datos.age < LIMITE_EDAD_MIN or datos.age > LIMITE_EDAD_MAX:
            raise HTTPException(
                status_code=400, 
                detail={
                    "campos": ["age"],
                    "mensaje": f"Extrapolación temporal: La edad ingresada es inválida. El modelo predictivo asintótico se restringe al periodo de {LIMITE_EDAD_MIN} a {LIMITE_EDAD_MAX} días (Ref: ACI 209R)."
                }
            )

        # B) Límite Volumétrico
        if peso_total < LIMITE_VOLUMEN_MIN or peso_total > LIMITE_VOLUMEN_MAX:
            raise HTTPException(
                status_code=400, 
                detail={
                    "campos": ["cement", "slag", "flyash", "water", "superplasticizer", "coarseaggregate", "fineaggregate"],
                    "mensaje": f"Inviabilidad física: Un metro cúbico de concreto normal debe pesar entre {LIMITE_VOLUMEN_MIN} y {LIMITE_VOLUMEN_MAX} kg. Su diseño suma {round(peso_total, 3)} kg, lo que implica un error de rendimiento volumétrico (Ref: ACI 318)."
                }
            )

        # C) Límite Químico de Agua/Material Cementante
        if ratio_wcm < LIMITE_WCM_MIN or ratio_wcm > LIMITE_WCM_MAX:
            raise HTTPException(
                status_code=400, 
                detail={
                    "campos": ["water", "cement", "slag", "flyash"],
                    "mensaje": f"Fuera de dominio químico: La relación Agua/Material-Cementante calculada ({round(ratio_wcm, 3)}) es inválida. La estequiometría exige un mínimo de {LIMITE_WCM_MIN}, y superar {LIMITE_WCM_MAX} causa segregación severa (Ref: ACI 211.1)."
                }
            )

        # D) Límite de Aditivo
        if dosis_sp > LIMITE_ADITIVO_MAX:
            raise HTTPException(
                status_code=400, 
                detail={
                    "campos": ["superplasticizer", "cement", "slag", "flyash"],
                    "mensaje": f"Sobredosis de aditivo: El superplastificante es el {round(dosis_sp, 3)}% del peso cementante. Superar el {LIMITE_ADITIVO_MAX}% provoca retardo crítico de fraguado y exceso de aire atrapado (Ref: ACI 212.3R / ASTM C494)."
                }
            )

        # E) Límites Geométricos de Agregados (Dominio Empírico de la IA)
        if ratio_grava_arena < RATIO_GRAVA_ARENA_MIN or ratio_grava_arena > RATIO_GRAVA_ARENA_MAX:
            raise HTTPException(
                status_code=400, 
                detail={
                    "campos": ["coarseaggregate", "fineaggregate"],
                    "mensaje": f"Fuera de dominio algorítmico: La relación Grava/Arena calculada ({round(ratio_grava_arena, 3)}) es inválida. La relación se debe mantener entre {round(RATIO_GRAVA_ARENA_MIN, 3)} y {round(RATIO_GRAVA_ARENA_MAX, 3)} para evitar sobresaturación extrema de agregados finos o gruesos (Ref: I.C. Yeh, 1998)."
                }
            )

        # ==========================================================
        # FASE 3: PREDICCIÓN ML Y GENERACIÓN DE RESULTADOS
        # ==========================================================

        # Creamos el DataFrame FORZANDO el orden exacto de las columnas de entrenamiento
        columnas_entrenamiento = [
            "cement", "slag", "flyash", "water", 
            "superplasticizer", "coarseaggregate", "fineaggregate", "age"
        ]
        
        # Extraemos los datos del usuario como diccionario
        datos_dict = datos.model_dump()
        
        # Construimos el DataFrame asegurando que cada valor caiga en la columna correcta
        df_input = pd.DataFrame(
            [[datos_dict[col] for col in columnas_entrenamiento]], 
            columns=columnas_entrenamiento
        )
        
        # Predicción
        prediccion = float(model.predict(df_input)[0])

        # Interpretaciones
        clase, uso = interpretar_resistencia(prediccion)
        clase_ga, desc_ga, caracteristicas_ga = interpretar_ga(ratio_grava_arena)
        clase_ac, desc_ac, caracteristicas_ac = interpretar_ac(ratio_wcm) # Usamos ratio_wcm que es el correcto analíticamente

        # Retorno actualizado
        return {
            "resistencia_estimada": round(prediccion, 3),
            "relacion_grava_arena": round(ratio_grava_arena, 3),
            "relacion_agua_cemento": round(ratio_wcm, 3), # Usamos el w/cm exacto
            "clase_resistencia": clase,
            "recomendaciones": uso,       
            "clase_ga": clase_ga,
            "descripcion_ga": desc_ga,
            "caracteristicas_ga": caracteristicas_ga,
            "clase_ac": clase_ac,
            "descripcion_ac": desc_ac,
            "caracteristicas_ac": caracteristicas_ac,
            "mensaje": "Cálculo exitoso"
        }

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/api/generar-reporte")
async def generar_reporte_endpoint(
    datos: ReporteRequest,
    session: Session = Depends(get_session)
    ):
    try:
        # ==========================================================
        # FASE A: GUARDAR TELEMETRÍA EN BASE DE DATOS (MLOps)
        # ==========================================================
        is_valid = datos.resistencia_real is not None
        error_abs = None
        error_rel = None
        
        # Solo calculamos el error si no omitieron el dato
        if is_valid:
            error_abs = abs(datos.prediccion.resistencia_estimada - datos.resistencia_real)
            # Protegemos contra división por cero por buenas prácticas
            if datos.resistencia_real > 0:
                error_rel = (error_abs / datos.resistencia_real) * 100
            else:
                error_rel = 0.0
            
        # Armamos la fila de la base de datos
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
            is_validated=is_valid
        )
        
        # Guardamos en SQLite
        session.add(nuevo_registro)
        session.commit()
        
        # ==========================================================
        # FASE B: GENERAR PDF (Tu código original)
        # ==========================================================
        pdf_bytes = generar_pdf_bytes(datos, is_valid, error_abs, error_rel)
        
        return Response(
            content=pdf_bytes, 
            media_type="application/pdf"
        )
    except Exception as e:
        print(f"Error generando PDF o guardando DB: {e}")
        raise HTTPException(status_code=500, detail="Error al generar el documento PDF")