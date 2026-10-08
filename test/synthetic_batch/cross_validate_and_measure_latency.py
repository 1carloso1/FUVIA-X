"""
FUVIA -- Cross-Validation and Real Latency Measurement
=======================================================
Sends a small batch of vectors to the REAL deployed backend
(/api/predecir on Render) and:

  1. Cross-validates the deployed firewall's verdict (HTTP 200/400)
     against the standalone firewall_logic.py reimplementation used
     in the synthetic batch -- confirming the two agree, i.e. that
     the local reimplementation is a faithful model of the deployed
     system, not just an independent copy that happens to look right.

  2. Measures REAL end-to-end latency (network + validation +
     inference), reporting p50/p95/p99, to replace the paper's
     current approximate range (200-500 ms) with real numbers.

Unlike generate_batch.py (14,000 vectors, in-memory, sub-millisecond),
this script makes actual HTTP requests, so the batch is deliberately
small (140 vectors) and a warm-up request precedes the timed run so
cold-start (~30-60s per the paper) doesn't contaminate the latency
measurement.
"""
import time
import statistics
import requests

# ---- SET THIS TO YOUR REAL DEPLOYED BACKEND URL ----
BASE_URL = "https://firmitas-ai.onrender.com"
ENDPOINT = f"{BASE_URL}/api/predecir"

N_PER_CATEGORY = 20  # 20 x 7 categories = 140 total requests
TIMEOUT_S = 90  # generous, in case of cold start on the warm-up call

# Re-import the same generators used in the synthetic batch, so the
# vectors here are drawn from the exact same distributions (same
# random seed -> same vectors as a subset of the 14,000-vector batch).
from firewall_logic import validar_mezcla
from generate_batch import (
    random_valid_vector, violates_temporal,
    violates_volumetric_yield_isolated, violates_stoichiometry_isolated,
    violates_chemical_addition_isolated, violates_geometric_domain_joint,
    violates_applicability_domain,
)

CATEGORIES = [
    ("valid", random_valid_vector),
    ("violates_temporal", violates_temporal),
    ("violates_volumetric_yield", violates_volumetric_yield_isolated),
    ("violates_stoichiometry", violates_stoichiometry_isolated),
    ("violates_chemical_addition", violates_chemical_addition_isolated),
    ("violates_geometric_domain", violates_geometric_domain_joint),
    ("violates_applicability_domain", violates_applicability_domain),
]


def warm_up():
    print("Warming up the backend (this may take up to ~60s on cold start)...")
    v = random_valid_vector()
    t0 = time.perf_counter()
    try:
        requests.post(ENDPOINT, json=v, timeout=TIMEOUT_S)
    except requests.RequestException as e:
        print(f"Warm-up request failed: {e}")
    print(f"Warm-up complete in {time.perf_counter() - t0:.1f}s. Starting timed run.\n")


def run():
    warm_up()

    results = []
    mismatches = []

    for label, generator in CATEGORIES:
        for _ in range(N_PER_CATEGORY):
            v = generator()
            local_ok, local_rule = validar_mezcla(v)

            t0 = time.perf_counter()
            try:
                resp = requests.post(ENDPOINT, json=v, timeout=TIMEOUT_S)
                elapsed_ms = (time.perf_counter() - t0) * 1000
                remote_ok = resp.status_code == 200
            except requests.RequestException as e:
                elapsed_ms = None
                remote_ok = None
                print(f"Request failed for category {label}: {e}")

            results.append({
                "category": label, "elapsed_ms": elapsed_ms,
                "local_ok": local_ok, "remote_ok": remote_ok,
            })

            if remote_ok is not None and remote_ok != local_ok:
                mismatches.append({
                    "category": label, "vector": v,
                    "local_verdict": local_ok, "local_rule": local_rule,
                    "remote_status": resp.status_code,
                })

    # ---- Cross-validation summary ----
    total = len([r for r in results if r["remote_ok"] is not None])
    agree = len([r for r in results if r["remote_ok"] == r["local_ok"]])
    print(f"\n=== Cross-validation: local reimplementation vs. deployed backend ===")
    print(f"Agreement: {agree}/{total} ({100*agree/total:.2f}%)")
    if mismatches:
        print(f"\n{len(mismatches)} MISMATCHES found:")
        for m in mismatches:
            print(f"  [{m['category']}] local={m['local_verdict']} "
                  f"(rule={m['local_rule']}) vs remote_status={m['remote_status']}")
            print(f"    vector: {m['vector']}")
    else:
        print("No mismatches -- the local reimplementation's verdicts match the "
              "deployed backend's on every request in this batch.")

    # ---- Real latency summary ----
    timings = [r["elapsed_ms"] for r in results if r["elapsed_ms"] is not None]
    print(f"\n=== Real end-to-end latency (network + validation + inference) ===")
    print(f"N = {len(timings)} successful requests")
    print(f"mean: {statistics.mean(timings):.1f} ms")
    print(f"p50:  {statistics.median(timings):.1f} ms")
    print(f"p95:  {statistics.quantiles(timings, n=100)[94]:.1f} ms")
    print(f"p99:  {statistics.quantiles(timings, n=100)[98]:.1f} ms")
    print(f"min:  {min(timings):.1f} ms")
    print(f"max:  {max(timings):.1f} ms")


if __name__ == "__main__":
    run()