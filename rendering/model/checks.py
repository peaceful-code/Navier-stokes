"""Independent numerical checks; no claim to validate the theorem's solution.

Run from the project root: .venv/bin/python -m rendering.model.checks
"""

import json
from pathlib import Path

import numpy as np
from scipy.integrate import quad
from scipy.special import jv

from .comparison import ComparisonModel, f0_series


def run_checks():
    m = ComparisonModel()
    rng = np.random.default_rng(293714)
    X = rng.uniform(0, m.X_limit * .95, 600)
    eta = rng.uniform(-m.settings.eta_limit * .95, m.settings.eta_limit * .95, 600)
    # Resolve the thin angular core as well as the broader coordinate region.
    eta[:300] = rng.uniform(-.025, .025, 300)
    theta = rng.uniform(-np.pi, np.pi, 600)
    t = m.settings.time
    points = m.points_from_similarity(X, eta, theta, t)
    X1, eta1, q = m.similarity(points, t)
    residual_q = q - points[:, 2] ** 2 * q ** (2 * m.settings.h) - (1 - t)
    coordinate_checks = dict(
        relative_q_residual=float(np.max(np.abs(residual_q)) / (1 - t)),
        max_X_roundtrip_error=float(np.max(np.abs(X1 - X))),
        max_eta_roundtrip_error=float(np.max(np.abs(eta1 - eta))),
    )

    divergence_checks = []
    for step in [2e-5, 1e-5, 5e-6]:
        diagonal = []
        for axis in range(3):
            d = np.zeros(3)
            d[axis] = step
            diagonal.append((m.velocity(points + d, t)[:, axis] -
                             m.velocity(points - d, t)[:, axis]) / (2 * step))
        diagonal = np.array(diagonal)
        div = diagonal.sum(axis=0)
        scale = np.abs(diagonal).sum(axis=0)
        divergence_checks.append(dict(
            centered_difference_step=step,
            max_absolute_divergence=float(np.max(np.abs(div))),
            max_relative_divergence=float(np.max(np.abs(div) / np.maximum(scale, 1e-15))),
        ))

    z = np.linspace(0, 4.1, 2001)
    bessel = np.ones_like(z)
    arg = np.sqrt(2 * z[1:])
    bessel[1:] = 2 * jv(1, arg) / arg
    series_checks = {}
    for terms in [8, 12, 24]:
        series_checks[str(terms)] = float(np.max(np.abs(f0_series(z, terms) - bessel)))
    # Independent equation check by exact differentiation of polynomial terms.
    coeff = [1.]
    for n in range(1, 24):
        coeff.append(coeff[-1] * (-.5) / (n * (n + 1)))
    poly = np.polynomial.Polynomial(coeff)
    residual_ode = 2 * (z * poly.deriv(2)(z) + 2 * poly.deriv(1)(z)) + poly(z)

    eta_sample = np.r_[np.linspace(-.5, .5, 25), m.eta_peak]
    direct = np.exp([m.settings.Lambda * quad(
        m.zeta, m.eta_peak, value, epsabs=1e-13, epsrel=1e-12
    )[0] for value in eta_sample]) / m.settings.amplitude_margin
    axis_factor_error = float(np.max(np.abs(m.angular_axis_factor(eta_sample) - direct)))

    scaling_errors = []
    reference_points = m.points_from_similarity(X[:40], eta[:40], theta[:40], .8)
    reference_fields = m.scalar_fields(reference_points, .8)
    for t2 in [.96, .99, .999]:
        tau_ratio = (1 - t2) / .2
        points2 = m.points_from_similarity(X[:40], eta[:40], theta[:40], t2)
        fields2 = m.scalar_fields(points2, t2)
        scaling_errors.append(dict(
            t=t2,
            radial=float(np.max(np.abs(points2[:, :2] - reference_points[:, :2] * tau_ratio ** .5))),
            axial=float(np.max(np.abs(points2[:, 2] - reference_points[:, 2] * tau_ratio ** m.D))),
            angular_rotation_relative=float(np.max(np.abs(
                fields2['omega'] / reference_fields['omega'] * tau_ratio ** (1 + m.settings.h) - 1))),
        ))

    axis_points = m.points_from_similarity(np.zeros(20), np.linspace(-.45, .45, 20), 0)
    axis_velocity = m.velocity(axis_points)
    checks = dict(
        scope="Numerical implementation checks of the local comparison only, not Navier–Stokes validation",
        coordinate_roundtrip=coordinate_checks,
        finite_difference_divergence=divergence_checks,
        f0_series_vs_independent_bessel_max_absolute_errors=series_checks,
        f0_minimum_on_0_4_1=float(f0_series(z).min()),
        f0_scaled_ode_max_absolute_residual=float(np.max(np.abs(residual_ode))),
        axis_factor_vs_independent_quad_absolute_error=axis_factor_error,
        exact_axis_transverse_velocity_max=float(np.max(np.abs(axis_velocity[:, :2]))),
        all_axis_velocities_finite=bool(np.isfinite(axis_velocity).all()),
        similarity_scaling_errors=scaling_errors,
        nonlinear_profile_error="Unknown: thresholds and asymptotic constants not evaluated",
        navier_stokes_momentum_residual="Not asserted zero; this comparison is not a Navier–Stokes solution",
    )
    assert coordinate_checks['relative_q_residual'] < 1e-12
    assert coordinate_checks['max_X_roundtrip_error'] < 1e-12
    assert coordinate_checks['max_eta_roundtrip_error'] < 1e-12
    assert divergence_checks[-1]['max_relative_divergence'] < 1e-7
    assert divergence_checks[-1]['max_relative_divergence'] < divergence_checks[0]['max_relative_divergence'] / 8
    assert series_checks['24'] < 2e-14
    assert np.max(np.abs(residual_ode)) < 2e-13
    assert axis_factor_error < 1e-8
    assert np.isfinite(axis_velocity).all()
    assert np.max(np.abs(axis_velocity[:, :2])) == 0
    checks['passed'] = True
    return m, checks


if __name__ == '__main__':
    model, result = run_checks()
    out = Path(__file__).resolve().parent
    (out / 'verification.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    (out / 'parameters.json').write_text(json.dumps(model.metadata(), indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(result, indent=2, ensure_ascii=False))
