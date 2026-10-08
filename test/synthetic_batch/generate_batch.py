"""
Generates a synthetic verification batch for FUVIA's parametric
firewall: a mix of valid vectors and vectors specifically designed to
violate each of the six firewall constraints (Section 2.3 of the
paper) in ISOLATION -- i.e., every field individually respects its
Table 1 (Yeh dataset) range, so the intended downstream rule is the
one that actually fires, not the upstream per-variable Applicability
Domain check.

EXCEPTION: the geometric (CA/FA) rule is mathematically inseparable
from the per-variable Applicability Domain at the extremes, as already
established via the unit test suite (max(coarse)/min(fine) = 1322/486
= 2.7202, almost exactly the CA/FA ceiling itself). This category is
therefore intentionally left as a joint test of both checks, and the
results are reported honestly as such rather than forced.

IMPORTANT: this is a controlled software verification exercise over
synthetically generated vectors -- NOT a field study and NOT a
benchmark of the live deployed API's network latency (a separate,
still-pending measurement). It verifies the correctness and throughput
of the validation logic itself, in the same spirit as Case A/B's
Boundary Value Analysis, but at much larger scale.
"""
import random
import statistics
from firewall_logic import timed_validate, TABLA1

random.seed(42)  # reproducible batch
N_PER_CATEGORY = 2000


def jitter(value, spread, lo, hi):
    """Random perturbation around `value`, clipped to [lo, hi]."""
    return max(lo, min(hi, value + random.uniform(-spread, spread)))


def random_valid_vector():
    # Anchored so total mass is comfortably within [2150, 2600]
    # under all perturbations (worst case ~2200, best case ~2550).
    cement = jitter(480, 40, 400, 550)
    water = jitter(155, 10, 140, 170)
    sp = jitter(5, 3, 0, 10)
    coarse = jitter(1020, 40, 950, 1100)
    fine = jitter(660, 30, 600, 720)
    age = random.randint(7, 90)
    return {"cement": cement, "slag": 0, "flyash": 0, "water": water,
            "superplasticizer": sp, "coarseaggregate": coarse,
            "fineaggregate": fine, "age": age}


def violates_temporal():
    v = random_valid_vector()
    v["age"] = random.choice([0, -5, 400, 1000])
    return v


def violates_volumetric_yield_isolated():
    # All fields within their individual Table 1 range, but summing
    # outside [2150, 2600]. Low-side: near-minimum across the board.
    if random.random() < 0.5:
        cement = jitter(90, 15, 71, 150)
        water = jitter(130, 8, 120, 150)
        coarse = jitter(760, 20, 730, 800)
        fine = jitter(500, 10, 486, 540)
    else:
        cement = jitter(580, 15, 550, 600)
        water = jitter(220, 5, 210, 228)
        coarse = jitter(1300, 15, 1280, 1322)
        fine = jitter(950, 10, 930, 968)
    return {"cement": cement, "slag": 0, "flyash": 0, "water": water,
            "superplasticizer": 0, "coarseaggregate": coarse,
            "fineaggregate": fine, "age": random.randint(7, 90)}


def violates_stoichiometry_isolated():
    # W/CM outside [0.25, 0.85] while every field stays in Table 1
    # range AND total mass stays in [2150, 2600] AND CA/FA stays
    # within [0.75, 2.72].
    if random.random() < 0.5:  # W/CM too high
        cement = jitter(210, 20, 180, 240)
        water = jitter(226, 2, 220, 228)
    else:  # W/CM too low
        cement = jitter(520, 20, 490, 560)
        water = jitter(122, 2, 120, 126)
    coarse = jitter(1050, 30, 950, 1150)
    fine = jitter(780, 20, 700, 850)
    return {"cement": cement, "slag": 0, "flyash": 0, "water": water,
            "superplasticizer": 0, "coarseaggregate": coarse,
            "fineaggregate": fine, "age": random.randint(7, 90)}


def violates_chemical_addition_isolated():
    # Superplasticizer > 4% of cementitious mass, sp itself within
    # Table 1 [0, 20.8], everything else safely valid.
    cement = jitter(420, 20, 380, 460)
    sp = jitter(19, 1, 17, 20.8)  # >4% of ~420-460 kg cement
    water = jitter(160, 8, 145, 175)
    coarse = jitter(1020, 30, 970, 1080)
    fine = jitter(680, 20, 630, 730)
    return {"cement": cement, "slag": 0, "flyash": 0, "water": water,
            "superplasticizer": sp, "coarseaggregate": coarse,
            "fineaggregate": fine, "age": random.randint(7, 90)}


def violates_geometric_domain_joint():
    # See module docstring: at the extremes this is mathematically
    # inseparable from the Applicability Domain check, so this
    # category intentionally tests both together.
    v = random_valid_vector()
    v["fineaggregate"] = random.uniform(50, 200)
    return v


def violates_applicability_domain():
    v = random_valid_vector()
    field = random.choice(list(TABLA1.keys()))
    lo, hi = TABLA1[field]
    v[field] = random.choice([lo - random.uniform(10, 50),
                               hi + random.uniform(10, 50)])
    return v


def run_category(label, generator_fn):
    accepted, rejected = 0, 0
    reasons = {}
    timings = []
    for _ in range(N_PER_CATEGORY):
        v = generator_fn()
        ok, rule, ms = timed_validate(v)
        timings.append(ms)
        if ok:
            accepted += 1
        else:
            rejected += 1
            reasons[rule] = reasons.get(rule, 0) + 1
    return {
        "label": label, "n": N_PER_CATEGORY,
        "accepted": accepted, "rejected": rejected,
        "reasons": reasons,
        "mean_ms": statistics.mean(timings),
        "p50_ms": statistics.median(timings),
        "p95_ms": statistics.quantiles(timings, n=100)[94],
        "p99_ms": statistics.quantiles(timings, n=100)[98],
    }


if __name__ == "__main__":
    categories = [
        ("valid", random_valid_vector),
        ("violates_temporal", violates_temporal),
        ("violates_volumetric_yield (isolated)", violates_volumetric_yield_isolated),
        ("violates_stoichiometry (isolated)", violates_stoichiometry_isolated),
        ("violates_chemical_addition (isolated)", violates_chemical_addition_isolated),
        ("violates_geometric_domain (joint w/ appl.domain)", violates_geometric_domain_joint),
        ("violates_applicability_domain", violates_applicability_domain),
    ]
    results = [run_category(l, f) for l, f in categories]

    print(f"{'Category':<48} {'N':>5} {'Accept':>7} {'Reject':>7}  Top reason")
    print("-" * 100)
    for r in results:
        top = max(r["reasons"].items(), key=lambda kv: kv[1]) if r["reasons"] else ("-", 0)
        print(f"{r['label']:<48} {r['n']:>5} {r['accepted']:>7} {r['rejected']:>7}  {top[0]} ({top[1]})")

    invalid_results = [r for r in results if r["label"] != "valid"]
    total_invalid_n = sum(r["n"] for r in invalid_results)
    total_invalid_rejected = sum(r["rejected"] for r in invalid_results)
    valid_r = results[0]

    print()
    print(f"Interception rate (intentionally-invalid categories): "
          f"{total_invalid_rejected}/{total_invalid_n} "
          f"({100*total_invalid_rejected/total_invalid_n:.2f}%)")
    print(f"False-rejection rate (intentionally-valid category): "
          f"{valid_r['rejected']}/{valid_r['n']} "
          f"({100*valid_r['rejected']/valid_r['n']:.2f}%)")

    print()
    print(f"{'Category':<48} {'mean(ms)':>9} {'p50(ms)':>9} {'p95(ms)':>9} {'p99(ms)':>9}")
    print("-" * 88)
    for r in results:
        print(f"{r['label']:<48} {r['mean_ms']:>9.5f} {r['p50_ms']:>9.5f} {r['p95_ms']:>9.5f} {r['p99_ms']:>9.5f}")

    all_timings = [t for r in results for t in [r["mean_ms"]]]
    print()
    print(f"Overall mean processing time across all {sum(r['n'] for r in results)} vectors: "
          f"{statistics.mean(all_timings):.5f} ms")