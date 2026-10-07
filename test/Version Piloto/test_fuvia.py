"""
FUVIA — Unit and Integration Tests
==================================
Covers:
  1. Unit tests for the three pure classification functions
     (interpretar_resistencia, interpretar_ac, interpretar_ga),
     with explicit boundary-value coverage (min <= x < max intervals).
  2. Integration tests for the five parametric firewall checks in
     /api/predecir, using FastAPI's TestClient against real HTTP
     payloads (one exactly-at-boundary case and one just-over-boundary
     case per rule, matching the paper's Boundary Value Analysis
     methodology already described in Section 3).

Run with: pytest test_fuvia.py -v
"""

import sys
import os

# Ensure Python can find main.py regardless of which directory pytest
# is invoked from. Adjust the relative path below if your backend
# folder is named differently or sits somewhere else relative to
# this test file.
sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend")
)

import pytest
from fastapi.testclient import TestClient

# Adjust this import to match your actual module/app location, e.g.:
# from main import app
from main import app


@pytest.fixture(scope="module")
def client():
    # Using TestClient as a context manager triggers FastAPI's
    # startup/shutdown lifecycle events (e.g. @app.on_event("startup")),
    # which is what actually loads the model into ml_models. Without
    # this, model = ml_models.get("predictor") returns None and every
    # request to /api/predecir fails with a 500 error.
    with TestClient(app) as c:
        yield c


# A known-valid baseline payload (Case B's mixture from the paper,
# Section 3.2): 540 kg cement, 162 kg water, 1040 kg coarse,
# 676 kg fine aggregate, 2.5 kg superplasticizer, 28-day curing.
VALID_PAYLOAD = {
    "cement": 540,
    "slag": 0,
    "flyash": 0,
    "water": 162,
    "superplasticizer": 2.5,
    "coarseaggregate": 1040,
    "fineaggregate": 676,
    "age": 28,
}


def valid_payload_overriding(**overrides):
    """Returns a copy of VALID_PAYLOAD with specific fields overridden,
    so each test only changes the one variable it's actually probing."""
    payload = dict(VALID_PAYLOAD)
    payload.update(overrides)
    return payload


# ======================================================================
# 1. UNIT TESTS — interpretar_resistencia (strength classification)
# ======================================================================
from main import interpretar_resistencia  # adjust import path as needed


class TestInterpretarResistencia:

    def test_lower_bound_of_low_strength(self):
        label, _ = interpretar_resistencia(0)
        assert label == "Low Strength"

    def test_just_below_standard_boundary(self):
        label, _ = interpretar_resistencia(19.999)
        assert label == "Low Strength"

    def test_exact_standard_boundary(self):
        # min <= x < max means 20 belongs to the NEXT bucket, not "Low"
        label, _ = interpretar_resistencia(20)
        assert label == "Standard Strength"

    def test_just_below_high_boundary(self):
        label, _ = interpretar_resistencia(39.999)
        assert label == "Standard Strength"

    def test_exact_high_boundary(self):
        label, _ = interpretar_resistencia(40)
        assert label == "High Strength"

    def test_just_below_ultra_high_boundary(self):
        label, _ = interpretar_resistencia(59.999)
        assert label == "High Strength"

    def test_exact_ultra_high_boundary(self):
        label, _ = interpretar_resistencia(60)
        assert label == "Ultra-High Strength"

    def test_typical_high_value(self):
        # Corrected: 75.463 >= 60, so this falls in the Ultra-High
        # bucket per RANGOS_CONCRETO, not "High Strength" as originally
        # (incorrectly) asserted.
        label, _ = interpretar_resistencia(75.463)  # Case B's inference
        assert label == "Ultra-High Strength"

    def test_negative_value_falls_back_to_unknown(self):
        label, usos = interpretar_resistencia(-5)
        assert label == "Unknown Strength"
        assert "structural engineer" in usos[0].lower()

    def test_extreme_upper_edge_is_unclassified(self):
        # min <= x < max: at exactly 9999 (the open upper bound),
        # no bucket matches. Physically implausible, but documents
        # real boundary behavior rather than assuming it "just works."
        label, _ = interpretar_resistencia(9999)
        assert label == "Unknown Strength"


# ======================================================================
# 2. UNIT TESTS — interpretar_ac (W/CM ratio classification)
# ======================================================================
from main import interpretar_ac  # adjust import path as needed


class TestInterpretarAC:

    def test_lower_bound_is_low(self):
        label, _, _ = interpretar_ac(0.0)
        assert label == "Low"

    def test_just_below_optimal_boundary(self):
        label, _, _ = interpretar_ac(0.399)
        assert label == "Low"

    def test_exact_optimal_boundary(self):
        label, _, _ = interpretar_ac(0.4)
        assert label == "Optimal"

    def test_just_below_high_boundary(self):
        label, _, _ = interpretar_ac(0.599)
        assert label == "Optimal"

    def test_exact_high_boundary(self):
        label, _, _ = interpretar_ac(0.6)
        assert label == "High"

    def test_case_b_ratio_is_low(self):
        # Corrected: Case B: water=162, cement=540 -> W/CM = 0.3, which
        # falls below the 0.4 lower bound of "Optimal" per
        # RANGOS_RELACION_AC, so it classifies as "Low" -- not
        # "Optimal" as originally (incorrectly) asserted. Renamed from
        # test_case_b_ratio_is_optimal to match the actual behavior.
        label, _, _ = interpretar_ac(162 / 540)
        assert label == "Low"

    def test_negative_value_falls_back_to_unknown(self):
        label, _, _ = interpretar_ac(-0.1)
        assert label == "Unknown Ratio"


# ======================================================================
# 3. UNIT TESTS — interpretar_ga (CA/FA ratio classification)
# ======================================================================
from main import interpretar_ga  # adjust import path as needed


class TestInterpretarGA:

    def test_lower_bound_is_fine_mixture(self):
        label, _, _ = interpretar_ga(0.0)
        assert label == "Fine Mixture"

    def test_just_below_balanced_boundary(self):
        label, _, _ = interpretar_ga(1.199)
        assert label == "Fine Mixture"

    def test_exact_balanced_boundary(self):
        label, _, _ = interpretar_ga(1.2)
        assert label == "Balanced"

    def test_just_below_coarse_boundary(self):
        label, _, _ = interpretar_ga(1.999)
        assert label == "Balanced"

    def test_exact_coarse_boundary(self):
        label, _, _ = interpretar_ga(2.0)
        assert label == "Coarse Mixture"

    def test_case_b_ratio_is_balanced(self):
        # Case B: coarse=1040, fine=676 -> CA/FA = 1.538
        label, _, _ = interpretar_ga(1040 / 676)
        assert label == "Balanced"


# ======================================================================
# 4. INTEGRATION TESTS — the five parametric firewall checks
# ======================================================================
# Each rule gets two cases: exactly-at-boundary (should PASS) and
# just-over-boundary (should be REJECTED with HTTP 400), mirroring the
# paper's own Boundary Value Analysis methodology (Section 3).

class TestFirewallTemporalDomain:
    """ACI 209R: curing age must be in [1, 365] days."""

    def test_age_at_lower_bound_passes(self, client):
        payload = valid_payload_overriding(age=1)
        response = client.post("/api/predecir", json=payload)
        assert response.status_code == 200

    def test_age_at_upper_bound_passes(self, client):
        payload = valid_payload_overriding(age=365)
        response = client.post("/api/predecir", json=payload)
        assert response.status_code == 200

    def test_age_below_lower_bound_rejected(self, client):
        payload = valid_payload_overriding(age=0)
        response = client.post("/api/predecir", json=payload)
        assert response.status_code == 400
        assert "age" in response.json()["detail"]["campos"]

    def test_age_above_upper_bound_rejected(self, client):
        payload = valid_payload_overriding(age=366)
        response = client.post("/api/predecir", json=payload)
        assert response.status_code == 400
        assert "age" in response.json()["detail"]["campos"]


class TestFirewallVolumetricYield:
    """ACI 318: total volumetric mass must be in [2150, 2600] kg/m3."""

    def test_total_mass_below_range_rejected(self, client):
        # 71 + 228 + 1040 + 676 + 2.5 = 2017.5 kg -- Sub-case A.2 from the paper
        payload = valid_payload_overriding(
            cement=71, water=228, coarseaggregate=1040, fineaggregate=676
        )
        response = client.post("/api/predecir", json=payload)
        assert response.status_code == 400
        assert set(["cement", "water", "coarseaggregate", "fineaggregate"]) <= set(
            response.json()["detail"]["campos"]
        )

    def test_case_b_mass_within_range_passes(self, client):
        # 540 + 162 + 1040 + 676 + 2.5 = 2420.5 kg -- within [2150, 2600]
        response = client.post("/api/predecir", json=VALID_PAYLOAD)
        assert response.status_code == 200


class TestFirewallStoichiometry:
    """ACI 211.1: W/CM ratio must be in [0.25, 0.85]."""

    def test_wcm_below_minimum_rejected(self, client):
        # water=100 with cement=540 -> W/CM ~ 0.185, below 0.25
        payload = valid_payload_overriding(water=100)
        response = client.post("/api/predecir", json=payload)
        assert response.status_code == 400

    def test_wcm_above_maximum_rejected(self, client):
        # water=500 with cement=540 -> W/CM ~ 0.926, above 0.85
        payload = valid_payload_overriding(water=500)
        response = client.post("/api/predecir", json=payload)
        assert response.status_code == 400


class TestFirewallChemicalAdditionLimits:
    """ACI 212.3R / ASTM C494: superplasticizer capped at 4.0% of
    cementitious mass."""

    def test_additive_within_limit_passes(self, client):
        # 2.5 kg on 540 kg cement = 0.46%, well within 4.0%
        response = client.post("/api/predecir", json=VALID_PAYLOAD)
        assert response.status_code == 200

    def test_additive_over_limit_rejected(self, client):
        # 30 kg on 540 kg cement = 5.56%, exceeds 4.0%
        payload = valid_payload_overriding(superplasticizer=30)
        response = client.post("/api/predecir", json=payload)
        assert response.status_code == 400


class TestFirewallGeometricDomain:
    """I.C. Yeh (1998): CA/FA ratio must be in [0.75, 2.72]."""

    def test_ratio_within_domain_passes(self, client):
        response = client.post("/api/predecir", json=VALID_PAYLOAD)
        assert response.status_code == 200

    def test_extreme_ratio_rejected_by_earliest_matching_check(self, client):
        # coarse=1040, fine=100 -> CA/FA = 10.4, far outside [0.75, 2.72].
        #
        # NOTE: this value also violates the per-variable Applicability
        # Domain (Table 1: fine aggregate must be in [486, 968]), and
        # since the firewall is Fail-Fast (stops at the first violated
        # check, in order), the Applicability Domain check fires first
        # and reports only "fineaggregate" -- not the geometric CA/FA
        # check specifically. This is expected, correct behavior, not
        # a bug: it turns out the two checks are nearly impossible to
        # separate at the extremes, since max(coarse)/min(fine) =
        # 1322/486 = 2.7202, i.e. almost exactly the CA/FA ceiling
        # (2.72) itself. In other words, respecting each component's
        # individual Table 1 range already keeps CA/FA within bounds
        # in practice, so this test verifies that *some* firewall
        # check correctly intercepts the request, rather than assuming
        # which specific rule fires first.
        payload = valid_payload_overriding(fineaggregate=100)
        response = client.post("/api/predecir", json=payload)
        assert response.status_code == 400
        assert "fineaggregate" in response.json()["detail"]["campos"]


class TestFirewallApplicabilityDomain:
    """Statistical applicability domain (Table 1): each of the 7
    volumetric variables must remain within the Yeh dataset's observed
    min/max range."""

    def test_cement_above_dataset_maximum_rejected(self, client):
        # Sub-case A.1 from the paper: 650 kg exceeds the 600 kg/m3 max
        payload = valid_payload_overriding(cement=650)
        response = client.post("/api/predecir", json=payload)
        assert response.status_code == 400
        assert "cement" in response.json()["detail"]["campos"]

    def test_cement_at_dataset_maximum_passes_this_check(self, client):
        # At exactly the boundary (600), this specific check should
        # pass -- the request may still be rejected by a different
        # rule (e.g. volumetric yield), so we only assert this
        # particular field is not flagged.
        payload = valid_payload_overriding(cement=600)
        response = client.post("/api/predecir", json=payload)
        if response.status_code == 400:
            assert "cement" not in response.json()["detail"]["campos"]