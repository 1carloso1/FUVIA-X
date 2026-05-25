from pydantic import BaseModel
from typing import Optional

# 1. Molde para los componentes de entrada del concreto
class ConcretoInput(BaseModel):
    cement: float
    slag: float
    flyash: float
    water: float
    superplasticizer: float
    coarseaggregate: float
    fineaggregate: float
    age: int

# 2. Molde para los resultados de la predicción y las interpretaciones
class ConcretoOutput(BaseModel):
    resistencia_estimada: float
    relacion_grava_arena: float
    relacion_agua_cemento: float
    clase_resistencia: str
    recomendaciones: list[str]
    clase_ga: str
    descripcion_ga: str
    caracteristicas_ga: list[str]
    clase_ac: str
    descripcion_ac: str
    caracteristicas_ac: list[str]
    mensaje: str


# 3. Molde para el reporte completo que se guardará en el PDF desde el frontend
class ReporteRequest(BaseModel):
    inputs: ConcretoInput
    prediccion: ConcretoOutput
    resistencia_real: Optional[float] = None
    graficas_base64: str
    version: str
