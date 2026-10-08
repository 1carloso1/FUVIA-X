"""
Standalone reimplementation of FUVIA's parametric firewall logic,
extracted from the translated backend code, for use in a synthetic verification batch.
This does NOT call the live deployed API -- it runs the same validation rules
in-process so we can measure throughput on a large synthetic batch
without needing network access to the user's Render deployment.
"""

import time

# Constants matching the deployed system (already confirmed against
# the paper's Table 1 and firewall description, Section 2.3)
LIMITE_EDAD_MIN, LIMITE_EDAD_MAX = 1, 365
LIMITE_VOLUMEN_MIN, LIMITE_VOLUMEN_MAX = 2150, 2600
LIMITE_WCM_MIN, LIMITE_WCM_MAX = 0.25, 0.85
LIMITE_ADITIVO_MAX = 4.0
RATIO_GA_MIN, RATIO_GA_MAX = 0.75, 2.72

# Table 1 applicability domain (Yeh dataset boundaries)
TABLA1 = {
    "cement": (71, 600),
    "slag": (0, 359),
    "flyash": (0, 175),
    "water": (120, 228),
    "superplasticizer": (0, 20.8),
    "coarseaggregate": (730, 1322),
    "fineaggregate": (486, 968),
}


def validar_mezcla(v):
    """Returns (accepted: bool, violated_rule: str or None)."""
    # 0. Statistical Applicability Domain (per-variable, Table 1)
    for campo, (lo, hi) in TABLA1.items():
        if not (lo <= v[campo] <= hi):
            return False, "applicability_domain"

    # A. Temporal Domain (ACI 209R)
    if not (LIMITE_EDAD_MIN <= v["age"] <= LIMITE_EDAD_MAX):
        return False, "temporal"

    # B. Volumetric Yield (ACI 318)
    peso_total = (v["cement"] + v["slag"] + v["flyash"] + v["water"]
                  + v["superplasticizer"] + v["coarseaggregate"] + v["fineaggregate"])
    if not (LIMITE_VOLUMEN_MIN <= peso_total <= LIMITE_VOLUMEN_MAX):
        return False, "volumetric_yield"

    # C. Stoichiometry (ACI 211.1)
    cementitious = v["cement"] + v["slag"] + v["flyash"]
    ratio_wcm = v["water"] / cementitious if cementitious else float("inf")
    if not (LIMITE_WCM_MIN <= ratio_wcm <= LIMITE_WCM_MAX):
        return False, "stoichiometry"

    # D. Chemical Addition Limits (ACI 212.3R / ASTM C494)
    dosis_sp_pct = (v["superplasticizer"] / cementitious * 100) if cementitious else 0
    if dosis_sp_pct > LIMITE_ADITIVO_MAX:
        return False, "chemical_addition"

    # E. Geometric Domain (Yeh, 1998)
    ratio_ga = v["coarseaggregate"] / v["fineaggregate"] if v["fineaggregate"] else float("inf")
    if not (RATIO_GA_MIN <= ratio_ga <= RATIO_GA_MAX):
        return False, "geometric_domain"

    return True, None


def timed_validate(v):
    t0 = time.perf_counter()
    accepted, rule = validar_mezcla(v)
    elapsed_ms = (time.perf_counter() - t0) * 1000
    return accepted, rule, elapsed_ms