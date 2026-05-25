"""
===========================================================================
ARCHIVO DE CONSTANTES - SISTEMA DE PREDICCIÓN DE CONCRETO
===========================================================================
Este archivo centraliza todos los límites empíricos, normativos y teóricos 
utilizados para la validación y clasificación de mezclas de concreto.
"""

# ==========================================================
# 1. CLASIFICACIÓN DE ESTADO ENDURECIDO (RESISTENCIA)
# ==========================================================
# Clasificación basada en rangos típicos de ingeniería estructural.
RANGOS_CONCRETO = [
    {
        "min": 0, 
        "max": 20, 
        "etiqueta": "Baja Resistencia", 
        "usos": ["Aceras", "Bordillos", "Muros divisorios", "Pisos simples"]
        # Mezclas no estructurales o de soporte secundario.
    },
    {
        "min": 20, 
        "max": 40, 
        "etiqueta": "Resistencia Estándar", 
        "usos": ["Vigas de vivienda", "Losas", "Columnas ligeras", "Pavimentos"]
        # Rango típico comercial (aprox. 3000 a 6000 psi).
    },
    {
        "min": 40, 
        "max": 60, 
        "etiqueta": "Alta Resistencia", 
        "usos": ["Puentes", "Columnas de edificios altos", "Estructuras industriales", "Muelles"]
        # Requiere estrictos controles de calidad y aditivos.
    },
    {
        "min": 60, 
        "max": 9999, # Límite superior abierto para cubrir cualquier predicción extrema.
        "etiqueta": "Ultra Alta Resistencia", 
        "usos": ["Rascacielos", "Búnkers", "Infraestructura crítica", "Soportes marinos"]
        # Concretos de alto desempeño (UHPC).
    }
]

# ==========================================================
# 2. CLASIFICACIÓN QUÍMICA (RELACIÓN AGUA/MATERIAL CEMENTANTE)
# ==========================================================
# Clasificación basada en el impacto de la porosidad capilar en la durabilidad.
RANGOS_RELACION_AC = [
    {
        "min": 0.0,
        "max": 0.4,
        "etiqueta": "Baja",
        "descripcion": "Alta Resistencia",
        "caracteristicas": [
            "Baja permeabilidad", 
            "Difícil trabajabilidad"    
        ]
        # Poca agua libre; requiere plastificantes para ser manejable.
    },
    {
        "min": 0.4,
        "max": 0.6,
        "etiqueta": "Óptima",
        "descripcion": "Balance Ideal",
        "caracteristicas": [
            "Buena cohesión",        
            "Durabilidad adecuada"
        ]
        # Zona estándar recomendada por ACI 211.1 para la mayoría de estructuras.
    },
    {
        "min": 0.6, 
        "max": 9999,
        "etiqueta": "Alta", 
        "descripcion": "Baja Durabilidad",
        "caracteristicas": [
            "Alta porosidad",
            "Riesgo de segregación"     
        ]
        # Exceso de agua capilar que debilita la matriz (Ley de Abrams).
    }
]


# ==========================================================
# 3. CLASIFICACIÓN FÍSICA (RELACIÓN GRAVA/ARENA)
# ==========================================================
# Basado en la reología, empaquetamiento granular y Gráfico de Shilstone.
RANGOS_RELACION_GA = [
    {
        "min": 0.0,
        "max": 1.2,
        "etiqueta": "Mezcla Fina",
        "descripcion": "Alta proporción de arena",
        "caracteristicas": [
            "Alta cohesión",          
            "Mayor demanda de pasta",
        ]
        # Zona IV de Shilstone: Mezcla "pegajosa" que exige mucha agua por exceso de área superficial.
    },
    {
        "min": 1.2,
        "max": 2.0,
        "etiqueta": "Equilibrada",
        "descripcion": "Granulometría óptima",
        "caracteristicas": [
            "Máxima compacidad",       
            "Ideal para bombeo"         
        ]
        # Zona II de Shilstone: Buen empaquetamiento (cercano a la curva de Fuller).
    },
    {
        "min": 2.0,
        "max": 9999,
        "etiqueta": "Mezcla Áspera",
        "descripcion": "Alta proporción de grava",
        "caracteristicas": [
            "Difícil de llanear",       
            "Riesgo de cangrejeras"    
        ]
        # Zona I de Shilstone: Faltan finos para lubricar la mezcla; tendencia a oquedades.
    }
]


# ==========================================================
# 4. LÍMITES EMPÍRICOS DEL DATASET (I.C. YEH, 1998)
# ==========================================================
# Evita extrapolaciones ("Garbage In, Garbage Out") restringiendo los inputs 
# a los valores mínimos y máximos exactos con los que la IA fue entrenada.
YEH_BOUNDARIES = {
    "cement": {"min": 71.0, "max": 600.0, "name": "Cemento"},
    "slag": {"min": 0.0, "max": 359.0, "name": "Escoria"},
    "flyash": {"min": 0.0, "max": 175.0, "name": "Ceniza Volante"},
    "water": {"min": 120.0, "max": 228.0, "name": "Agua"},
    "superplasticizer": {"min": 0.0, "max": 20.8, "name": "Superplastificante"},
    "coarseaggregate": {"min": 730.0, "max": 1322.0, "name": "Agregado Grueso"},
    "fineaggregate": {"min": 486.0, "max": 968.0, "name": "Agregado Fino"},
}

# Límites de la relación G/A inferidos del dataset de Yeh:
# Min = La menor cantidad de grava posible dividida por la mayor de arena.
RATIO_GRAVA_ARENA_MIN = YEH_BOUNDARIES["coarseaggregate"]["min"] / YEH_BOUNDARIES["fineaggregate"]["max"]
# Max = La mayor cantidad de grava posible dividida por la menor de arena.
RATIO_GRAVA_ARENA_MAX = YEH_BOUNDARIES["coarseaggregate"]["max"] / YEH_BOUNDARIES["fineaggregate"]["min"]


# ==========================================================
# 5. LÍMITES NORMATIVOS PARA DISEÑO DE MEZCLAS (ACI / ASTM)
# ==========================================================

# Rendimiento Volumétrico (ACI 318): 
# Densidad teórica del concreto de peso normal en kg/m3. Mezclas fuera de este rango son físicamente inviables.
LIMITE_VOLUMEN_MIN = 2150
LIMITE_VOLUMEN_MAX = 2600

# Relación Agua/Material Cementante (ACI 211.1): 
# < 0.25 deja partículas sin hidratar; > 0.85 colapsa la tensión superficial (segregación masiva).
LIMITE_WCM_MIN = 0.25
LIMITE_WCM_MAX = 0.85

# Dosis de Superplastificante (ACI 212.3R / ASTM C494): 
# > 4.0% de la masa cementante causa retardo crítico de fraguado y exceso de aire atrapado.
LIMITE_ADITIVO_MAX = 4.0

# Edad de Curado (ACI 209R): 
# Comportamiento asintótico válido. < 1 día es estado plástico, > 365 días la ganancia de resistencia es casi nula.
LIMITE_EDAD_MIN = 1
LIMITE_EDAD_MAX = 365

# Mapeo de nombres técnicos a nombres profesionales en español
TRADUCCIONES_MATERIALES = {
    "cement": {"nombre": "Cemento", "unidad": "kg/m³"},
    "slag": {"nombre": "Escoria de alto horno", "unidad": "kg/m³"},
    "flyash": {"nombre": "Ceniza volante", "unidad": "kg/m³"},
    "water": {"nombre": "Agua", "unidad": "kg/m³"},
    "superplasticizer": {"nombre": "Superplastificante", "unidad": "kg/m³"},
    "coarseaggregate": {"nombre": "Agregado Grueso / Grava", "unidad": "kg/m³"},
    "fineaggregate": {"nombre": "Agregado Fino / Arena", "unidad": "kg/m³"},
    "age": {"nombre": "Edad (días)", "unidad": "Días"}
}
