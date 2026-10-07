"""Deterministic, incompressible ILLUSTRATIVE vortex for WebGL and Blender.

This independent kinematic field is not a reconstruction of the paper's profiles,
and is not asserted to solve its Navier–Stokes problem. The swirl parameters are
chosen to make inward spirals and two central axial jets visible.

JSON schema:
    positions: list[curve][x0,y0,z0,x1,y1,z1,...]
    omega: list[curve][Omega0,Omega1,...], angular velocity (not curl(u))
    curve_metadata: one entry per curve, in the same order
    metadata: scope, formulae, parameters, colors and presentation-only scaling

Run: .venv/bin/python rendering/illustrative_model.py
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path

import numpy as np
from scipy.integrate import cumulative_simpson


@dataclass(frozen=True)
class Settings:
    a: float = .65
    K: float = 24.0
    rc: float = 2.2
    zc: float = 2.5
    z_end: float = 3.5
    point_count: int = 513
    azimuth_count: int = 12
    h_presentation: float = .0005
    tau_min_presentation: float = 1e-4
    tau_max_presentation: float = 1.


class IllustrativeVortex:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings()

    def angular_velocity(self, points):
        p = self.settings
        points = np.asarray(points, dtype=float)
        r2 = points[..., 0] ** 2 + points[..., 1] ** 2
        radial_factor = np.full_like(r2, 1 / p.rc ** 2)
        np.divide(-np.expm1(-r2 / p.rc ** 2), r2,
                  out=radial_factor, where=r2 > 0)
        return p.K * radial_factor * np.exp(-(points[..., 2] / p.zc) ** 2)

    def velocity(self, points):
        points = np.asarray(points, dtype=float)
        omega = self.angular_velocity(points)
        x, y, z = points[..., 0], points[..., 1], points[..., 2]
        a = self.settings.a
        return np.stack((-.5 * a * x - omega * y,
                         -.5 * a * y + omega * x,
                         a * z), axis=-1)

    def presentation_scales(self, tau):
        """Finite display deformation. This is not a physical time integrator."""
        p = self.settings
        tau = float(np.clip(tau, p.tau_min_presentation, p.tau_max_presentation))
        return tau, np.array([np.sqrt(tau), np.sqrt(tau), tau ** (.5 - p.h_presentation)])

    def presentation_velocity(self, points, tau):
        """Pushforward preserving the displayed instantaneous streamlines.

        u_tau(x)=tau^(-1-h)*D_tau*u_0(D_tau^-1*x). The axial amplitude therefore
        scales as tau^(-.5-2h), not as the theorem's q^(-.5-h) profile.
        """
        tau, scale = self.presentation_scales(tau)
        return tau ** (-1 - self.settings.h_presentation) * scale * self.velocity(np.asarray(points) / scale)

    def curves(self, point_count=None):
        p = self.settings
        count = point_count or p.point_count
        initial_radii = np.linspace(2.95, 4., 6)
        initial_heights = np.array([.00045, .00075, .0011, .0017, .0026, .0039])
        curves = []
        for branch in (1, -1):
            for family, (r0, z_abs0) in enumerate(zip(initial_radii, initial_heights)):
                s_end = np.log(p.z_end / z_abs0) / p.a
                s = np.linspace(0, s_end, count)
                r = r0 * np.exp(-p.a * s / 2)
                z = branch * z_abs0 * np.exp(p.a * s)
                omega = self.angular_velocity(np.stack((r, np.zeros_like(r), z), axis=-1))
                angle = cumulative_simpson(omega, x=s, initial=0)
                for azimuth in range(p.azimuth_count):
                    # Uniformly rotated copies, staggered between radial families.
                    phase = 2 * np.pi * azimuth / p.azimuth_count + family * .21
                    if branch < 0:
                        phase += np.pi / p.azimuth_count
                    theta = phase + angle
                    points = np.stack((r * np.cos(theta), r * np.sin(theta), z), axis=-1)
                    curves.append({
                        "points": points, "omega": omega, "theta": theta, "s": s,
                        "description": {
                            "branch": branch,
                            "family": family,
                            "azimuth_index": azimuth,
                            "initial_phase_radians": float(phase),
                            "r0": float(r0),
                            "z0": float(branch * z_abs0),
                            "z_end": float(branch * p.z_end),
                            "turns": float(angle[-1] / (2 * np.pi)),
                            "turns_before_radius_one": float(np.interp(2 * np.log(r0) / p.a, s, angle) / (2 * np.pi)),
                            "integration_parameter_max": float(s_end),
                        },
                    })
        return curves


def verify(model, curves):
    """Check geometry against its own analytic field, not against Navier–Stokes."""
    rng = np.random.default_rng(902105)
    points = rng.uniform((-4, -4, -3.5), (4, 4, 3.5), (1200, 3))
    points[:400, :2] *= .12
    divergence = []
    for step in [2e-4, 1e-4, 5e-5]:
        diagonal = []
        for axis in range(3):
            offset = np.zeros(3)
            offset[axis] = step
            diagonal.append((model.velocity(points + offset)[:, axis] -
                             model.velocity(points - offset)[:, axis]) / (2 * step))
        diagonal = np.array(diagonal)
        relative = np.abs(diagonal.sum(axis=0)) / np.maximum(np.abs(diagonal).sum(axis=0), 1)
        divergence.append({
            "finite_difference_step": step,
            "max_absolute": float(np.max(np.abs(diagonal.sum(axis=0)))),
            "max_relative": float(np.max(relative)),
        })

    finer = model.curves(point_count=2 * model.settings.point_count - 1)
    angular_error = 0.
    position_error = 0.
    invariant_error = 0.
    tangent_sines = []
    direction_cosines = []
    tangent_sines_fine = []
    for coarse, fine in zip(curves, finer):
        angular_error = max(angular_error, float(np.max(np.abs(coarse['theta'] - fine['theta'][::2]))))
        position_error = max(position_error, float(np.max(np.linalg.norm(coarse['points'] - fine['points'][::2], axis=1))))
        xyz = coarse['points']
        invariant = (xyz[:, 0] ** 2 + xyz[:, 1] ** 2) * xyz[:, 2]
        invariant_error = max(invariant_error, float(np.max(np.abs(invariant / invariant[0] - 1))))
        for record, sine_list in ((coarse, tangent_sines), (fine, tangent_sines_fine)):
            tangent = np.gradient(record['points'], record['s'], axis=0, edge_order=2)[2:-2]
            field = model.velocity(record['points'])[2:-2]
            cosines = np.sum(tangent * field, axis=1) / (np.linalg.norm(tangent, axis=1) * np.linalg.norm(field, axis=1))
            sine_list.extend(np.linalg.norm(np.cross(tangent, field), axis=1) /
                             (np.linalg.norm(tangent, axis=1) * np.linalg.norm(field, axis=1)))
            if record is coarse:
                direction_cosines.extend(cosines)

    origin = np.zeros((1, 3))
    axis_limit = model.settings.K / model.settings.rc ** 2
    checks = {
        "scope": "Checks of the independent illustrative kinematic field only, not of the paper's solution",
        "analytic_divergence": "(-a/2)+(-a/2)+a=0; the axisymmetric azimuthal part has zero divergence",
        "finite_difference_divergence": divergence,
        "max_relative_meridional_invariant_error_r_squared_z": invariant_error,
        "angular_quadrature_max_change_on_doubling_intervals_radians": angular_error,
        "curve_position_max_change_on_doubling_intervals": position_error,
        "tangent_direction_sine_p99": float(np.quantile(tangent_sines, .99)),
        "tangent_direction_sine_p99_refined": float(np.quantile(tangent_sines_fine, .99)),
        "minimum_direction_cosine": float(np.min(direction_cosines)),
        "axis_omega_limit": axis_limit,
        "axis_omega_computed": float(model.angular_velocity(origin)[0]),
        "axis_origin_velocity": model.velocity(origin)[0].tolist(),
        "all_values_finite": bool(all(np.isfinite(c['points']).all() and np.isfinite(c['omega']).all() for c in curves)),
        "navier_stokes_momentum_equation": "Not checked or claimed; this is an illustrative prescribed velocity field",
    }
    # At each fixed display scale, a constant diagonal pushforward preserves
    # divergence and maps the old tangent to the new tangent exactly.
    tau, scale = model.presentation_scales(.013)
    c = tau ** (-1 - model.settings.h_presentation)
    pushed = model.presentation_velocity(points * scale, tau)
    expected = c * scale * model.velocity(points)
    checks['pushforward_velocity_max_relative_error'] = float(np.max(
        np.linalg.norm(pushed - expected, axis=1) / np.maximum(np.linalg.norm(expected, axis=1), 1e-15)))
    assert divergence[-1]['max_relative'] < 1e-7
    assert divergence[-1]['max_relative'] < divergence[0]['max_relative'] / 8
    assert invariant_error < 1e-12
    assert angular_error < 1e-5
    assert position_error < 1e-5
    assert checks['tangent_direction_sine_p99'] < .01
    assert checks['tangent_direction_sine_p99_refined'] < checks['tangent_direction_sine_p99'] / 3
    assert checks['minimum_direction_cosine'] > .999
    assert checks['all_values_finite']
    assert abs(checks['axis_omega_computed'] - axis_limit) < 1e-14
    assert checks['pushforward_velocity_max_relative_error'] < 1e-12
    checks['passed'] = True
    return checks


def metadata(model, curves, checks):
    p = model.settings
    omegas = np.concatenate([c['omega'] for c in curves])
    positions = np.concatenate([c['points'] for c in curves])
    return {
        "title": "Spirales entrantes et jets axiaux — modèle pédagogique indépendant",
        "status": "illustration cinématique incompressible; profils choisis pour la lisibilité",
        "not_a_reconstruction_of_the_paper": True,
        "not_claimed_to_solve_navier_stokes": True,
        "independent_of_previous_appendix_B_comparison": True,
        "units": "unités illustratives arbitraires, sans calibration physique",
        "parameters": asdict(p),
        "formula_cylindrical": {
            "u_r": "-a*r/2",
            "u_z": "a*z",
            "Omega": "K*(1-exp(-r*r/(rc*rc)))/(r*r)*exp(-(z/zc)^2)",
            "Omega_on_axis": "(K/(rc*rc))*exp(-(z/zc)^2)",
            "u_theta": "r*Omega",
            "streamline": "r=r0*exp(-a*s/2); z=z0*exp(a*s); theta=theta0+integral(Omega ds)",
        },
        "schema": {
            "positions": "list[curve][x0,y0,z0,x1,y1,z1,...]; Cartesian coordinates in the reference geometry",
            "omega": "list[curve][Omega0,Omega1,...]; same indexing as positions, angular velocity, not vorticity",
            "curve_metadata": "list[curve] containing seeds, branch, angular phase, number of turns and maximum s",
        },
        "curve_count": len(curves),
        "points_per_curve": p.point_count,
        "curve_direction": "Increasing vertex index follows the field: inward radially, upward on positive branch, downward on negative branch",
        "turns_min": min(c['description']['turns'] for c in curves),
        "turns_max": max(c['description']['turns'] for c in curves),
        "turns_before_radius_one_min": min(c['description']['turns_before_radius_one'] for c in curves),
        "turns_before_radius_one_max": max(c['description']['turns_before_radius_one'] for c in curves),
        "swirl_design": "rc=2.2 and K=24 distribute about two turns across the visible disk before r=1, with fewer than ten turns in each full branch",
        "bounding_box": {"min": positions.min(axis=0).tolist(), "max": positions.max(axis=0).tolist()},
        "color": {
            "quantity": "angular velocity Omega = u_theta/r; NOT total speed and NOT curl(u)",
            "scale": "linear",
            "min": 0.,
            "max": p.K / p.rc ** 2,
            "sampled_min": float(omegas.min()),
            "sampled_max": float(omegas.max()),
            "low_hex": "#27c6d0",
            "middle_hex": "#3268bd",
            "high_hex": "#efb66d",
            "time_rule": "Use Omega_reference for fixed normalized colors. For an absolute displayed value multiply by tau^(-1-h) and label that factor.",
        },
        "presentation_scaling": {
            "h": p.h_presentation,
            "tau_min": p.tau_min_presentation,
            "tau_max": p.tau_max_presentation,
            "radial_scale": "sqrt(tau)",
            "axial_scale": "tau^(0.5-h)",
            "angular_velocity_scale": "tau^(-1-h)",
            "instantaneous_field_pushforward": "u_tau(x)=tau^(-1-h)*D_tau*u_0(D_tau^-1*x), D_tau=diag(sqrt(tau),sqrt(tau),tau^(.5-h))",
            "radial_and_azimuthal_velocity_scale": "tau^(-.5-h)",
            "axial_velocity_scale": "tau^(-.5-2h); specific to this illustrative pushforward, not the paper's axial profile",
            "why_pushforward": "At each fixed tau, it preserves exact tangency to the transformed curves and incompressibility. It does not solve a time-dependent momentum equation.",
            "clock": "logarithmic in tau, tau clamped strictly above zero",
            "not_a_dynamical_simulation": True,
            "explanation": "Scales applied to a fixed reference geometry to illustrate concentration. These are not particle trajectories in the time-dependent theorem solution.",
            "zoom": "Any magnification must be labelled; zoom changes apparent size, not physical coordinates.",
        },
        "rendering_conventions": {
            "tubes_or_ribbons": "graphic thickness only; curves are not solid material layers",
            "moving_streaks": "direction markers with a presentation clock; no physical-particle interpretation is supplied",
            "singular_time": "never evaluated; all shapes, lengths, colors and displayed values remain finite",
        },
        "export_precision": "positions and Omega rounded to 7 decimal places; numeric checks use the unrounded reference arrays",
        "checks_passed": checks['passed'],
        "reproduction": ".venv/bin/python rendering/illustrative_model.py",
        "provenance": "Explicit independent field chosen for this educational rendering; no image-derived coordinates and no reconstructed theorem profiles",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=Path('output/immersive'))
    args = parser.parse_args()
    model = IllustrativeVortex()
    curves = model.curves()
    checks = verify(model, curves)
    info = metadata(model, curves, checks)
    output = {
        "positions": [np.round(c['points'], 7).ravel().tolist() for c in curves],
        "omega": [np.round(c['omega'], 7).tolist() for c in curves],
        "curve_metadata": [c['description'] for c in curves],
        "metadata": info,
    }
    # Control serialization too: the exported points still lie on the intended curves.
    max_rounding = max(float(np.max(np.linalg.norm(
        np.asarray(flat).reshape(-1, 3) - record['points'], axis=1)))
        for flat, record in zip(output['positions'], curves))
    checks['max_export_position_rounding_error'] = max_rounding
    assert max_rounding < 9e-8
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / 'flow_data.json').write_text(json.dumps(output, separators=(',', ':'), ensure_ascii=False) + '\n')
    (args.output / 'illustrative_metadata.json').write_text(json.dumps(info, indent=2, ensure_ascii=False) + '\n')
    (args.output / 'illustrative_checks.json').write_text(json.dumps(checks, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({"curves": len(curves), "points_per_curve": model.settings.point_count,
                      "turns_range": [info['turns_min'], info['turns_max']],
                      "omega_range": [info['color']['sampled_min'], info['color']['sampled_max']],
                      "checks": checks}, indent=2))


if __name__ == '__main__':
    main()
