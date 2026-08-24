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
        "etiqueta": "Low Strength", 
        "usos": ["Sidewalks", "Curbs", "Partition Walls", "Simple Flooring"]
        # Mezclas no estructurales o de soporte secundario.
    },
    {
        "min": 20, 
        "max": 40, 
        "etiqueta": "Standard Strength", 
        "usos": ["Residential Beams", "Slabs", "Light Columns", "Pavements"]
        # Rango típico comercial (aprox. 3000 a 6000 psi).
    },
    {
        "min": 40, 
        "max": 60, 
        "etiqueta": "High Strength", 
        "usos": ["Bridges", "High-Rise Building Columns", "Industrial Structures", "Piers"]
        # Requiere estrictos controles de calidad y aditivos.
    },
    {
        "min": 60, 
        "max": 9999, # Límite superior abierto para cubrir cualquier predicción extrema.
        "etiqueta": "Ultra-High Strength", 
        "usos": ["Skyscrapers", "Bunkers", "Critical Infrastructure", "Marine Supports"]
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
        "etiqueta": "Low",
        "descripcion": "High Strength",
        "caracteristicas": [
            "Low Permeability", 
            "Difficult Workability"    
        ]
        # Poca agua libre; requiere plastificantes para ser manejable.
    },
    {
        "min": 0.4,
        "max": 0.6,
        "etiqueta": "Optimal",
        "descripcion": "Ideal Balance",
        "caracteristicas": [
            "Good Cohesion",        
            "Adequate Durability"
        ]
        # Zona estándar recomendada por ACI 211.1 para la mayoría de estructuras.
    },
    {
        "min": 0.6, 
        "max": 9999,
        "etiqueta": "High", 
        "descripcion": "Low Durability",
        "caracteristicas": [
            "High Porosity",
            "Segregation Risk"     
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
        "etiqueta": "Fine Mixture",
        "descripcion": "High Sand Proportion",
        "caracteristicas": [
            "High Cohesion",          
            "Higher Paste Demand",
        ]
        # Zona IV de Shilstone: Mezcla "pegajosa" que exige mucha agua por exceso de área superficial.
    },
    {
        "min": 1.2,
        "max": 2.0,
        "etiqueta": "Balanced",
        "descripcion": "Optimal Gradation",
        "caracteristicas": [
            "Maximum Compactness",       
            "Ideal for Pumping"         
        ]
        # Zona II de Shilstone: Buen empaquetamiento (cercano a la curva de Fuller).
    },
    {
        "min": 2.0,
        "max": 9999,
        "etiqueta": "Coarse Mixture",
        "descripcion": "High Gravel Proportion",
        "caracteristicas": [
            "Difficult to Finish (Trowel)",       
            "Risk of Honeycombing"    
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
    "cement": {"min": 71.0, "max": 600.0, "name": "Cement"},
    "slag": {"min": 0.0, "max": 359.0, "name": "Blast Furnace Slag"},
    "flyash": {"min": 0.0, "max": 175.0, "name":"Fly Ash"},
    "water": {"min": 120.0, "max": 228.0, "name": "Water"},
    "superplasticizer": {"min": 0.0, "max": 20.8, "name": "Superplasticizer"},
    "coarseaggregate": {"min": 730.0, "max": 1322.0, "name": "Coarse Aggregate"},
    "fineaggregate": {"min": 486.0, "max": 968.0, "name": "Fine Aggregate"},
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
    "cement": {"nombre": "Cement", "unidad": "kg/m³"},
    "slag": {"nombre": "Blast Furnace Slag", "unidad": "kg/m³"},
    "flyash": {"nombre": "Fly Ash", "unidad": "kg/m³"},
    "water": {"nombre": "Water", "unidad": "kg/m³"},
    "superplasticizer": {"nombre": "Superplasticizer", "unidad": "kg/m³"},
    "coarseaggregate": {"nombre": "Coarse Aggregate", "unidad": "kg/m³"},
    "fineaggregate": {"nombre": "Fine Aggregate", "unidad": "kg/m³"},
    "age": {"nombre": "Age (days)", "unidad": "Days"}
}
