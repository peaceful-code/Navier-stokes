"""A local comparison field, NOT the reconstructed Navier–Stokes solution.

Source: local paper, equations (3.2), (B.1), (B.3), (B.11)–(B.13).
The implemented angular profile is the explicit comparison in (B.13).
The axial profile keeps only U_*; its pressure-dependent correction is omitted.
Our finite parameters are exploratory, not certified admissible for the theorem.
"""

from dataclasses import asdict, dataclass

import numpy as np
from scipy.integrate import quad, solve_ivp
from scipy.optimize import brentq


@dataclass(frozen=True)
class ModelSettings:
    h: float = 0.0005
    j: float = 0.0005
    Lambda: float = 64.0
    sigma: float = 0.1
    amplitude_margin: float = 1.05
    eta_limit: float = 0.5
    Y_limit: float = 4.0
    time: float = 0.96
    series_terms: int = 24


def f0_series(z, terms=24):
    """Sum (-z/2)^n / (n! (n+1)!), with the removable value f0(0)=1."""
    z = np.asarray(z, dtype=float)
    term = np.ones_like(z)
    total = term.copy()
    for n in range(1, terms):
        term *= (-z / 2) / (n * (n + 1))
        total += term
    return total


class ComparisonModel:
    """Coordinate geometry plus a divergence-free *comparison* velocity.

    All lengths, times and velocities use nondimensional paper coordinates.
    There is no conversion to metres, seconds, or a laboratory experiment.
    """

    def __init__(self, settings=None):
        self.settings = settings or ModelSettings()
        p = self.settings
        if not (0 < p.h <= .001 and 0 < p.j <= .001):
            raise ValueError("Use the small real ranges verified in NaturalAxisData.lean.")
        if not (p.Lambda >= 1 and p.sigma > 0 and 0 < p.eta_limit < 1):
            raise ValueError("Invalid exploratory parameters.")
        if not (0 < p.Y_limit <= 4.1 and p.series_terms >= 4):
            raise ValueError("The comparison is restricted to 0 <= Y <= 4.1.")
        if p.amplitude_margin <= 1:
            raise ValueError("Keep a margin above the maximum on the real interval.")
        self.A, self.D = .5 + p.h, .5 - p.h
        self.eta_peak = brentq(self.H, -p.j / 4, -p.j / 5, xtol=1e-15)
        # The integral from the maximum eliminates overflow in phi_*/C.
        # C=amplitude_margin*max_{[-1,1]} phi_* is a real normalization.
        # The complex neighborhood and C0(Lambda) are not numerically known.
        self.log_C_real = p.Lambda * quad(
            self.zeta, 0., self.eta_peak, epsabs=1e-13, epsrel=1e-13
        )[0]
        options = dict(rtol=2e-12, atol=1e-13, dense_output=True, max_step=.002)
        self._integral_left = solve_ivp(
            lambda eta, _: [p.Lambda * self.zeta(eta)],
            (self.eta_peak, -1.), [0.], **options
        ).sol
        self._integral_right = solve_ivp(
            lambda eta, _: [p.Lambda * self.zeta(eta)],
            (self.eta_peak, 1.), [0.], **options
        ).sol

    @property
    def X_limit(self):
        return self.settings.Y_limit / self.settings.Lambda

    def L(self, eta):
        return 1 - 2 * self.settings.h * np.asarray(eta) ** 2

    def H(self, eta):
        eta = np.asarray(eta)
        return self.D * eta + (1 - eta ** 2) * (4 * eta + self.settings.j)

    def chi(self, eta):
        H = self.H(eta)
        return H * H / (H * H + self.settings.sigma ** 2)

    def zeta(self, eta):
        H = self.H(eta)
        return -self.L(eta) * H / (H * H + self.settings.sigma ** 2)

    def angular_axis_factor(self, eta):
        """g=phi_*/C; maximum is 1/amplitude_margin on the real interval."""
        eta = np.asarray(eta, dtype=float)
        flat = eta.ravel()
        log_g = np.empty_like(flat)
        left = flat < self.eta_peak
        if left.any():
            log_g[left] = self._integral_left(flat[left])[0]
        if (~left).any():
            log_g[~left] = self._integral_right(flat[~left])[0]
        return np.exp(log_g.reshape(eta.shape)) / self.settings.amplitude_margin

    def _time(self, t):
        t = self.settings.time if t is None else float(t)
        if not np.isfinite(t) or not 0 <= t < 1:
            raise ValueError("The geometry is defined only before t=1, with 0 <= t < 1.")
        return t, 1 - t

    def q_from_z(self, z, t=None):
        """Positive root of q - z^2 q^(2h) = 1-t, by safeguarded Newton."""
        _, tau = self._time(t)
        z = np.asarray(z, dtype=float)
        height_scale = np.abs(z) ** (1 / self.D)
        lo = np.maximum(tau, height_scale)
        hi = 2 * (tau + height_scale)
        q = hi.copy()
        for _ in range(14):
            term = z * z * q ** (2 * self.settings.h)
            residual = q - term - tau
            lo = np.where(residual < 0, q, lo)
            hi = np.where(residual > 0, q, hi)
            candidate = q - residual / (1 - 2 * self.settings.h * term / q)
            q = np.where((candidate >= lo) & (candidate <= hi), candidate, (lo + hi) / 2)
        return q

    def points_from_similarity(self, X, eta, theta, t=None):
        """Exact (X,eta,theta)->Cartesian map, broadcasting all input arrays."""
        _, tau = self._time(t)
        X, eta, theta = np.broadcast_arrays(X, eta, theta)
        if np.any(X < 0) or np.any(np.abs(eta) >= 1):
            raise ValueError("Require X >= 0 and |eta| < 1.")
        q = tau / (1 - eta * eta)
        r = np.sqrt(2 * X * q)
        return np.stack((r * np.cos(theta), r * np.sin(theta), eta * q ** self.D), axis=-1)

    def similarity(self, points, t=None):
        points = np.asarray(points, dtype=float)
        q = self.q_from_z(points[..., 2], t)
        r2 = points[..., 0] ** 2 + points[..., 1] ** 2
        return r2 / (2 * q), points[..., 2] / q ** self.D, q

    def profiles(self, X, eta):
        X, eta = np.broadcast_arrays(X, eta)
        Y = self.settings.Lambda * X
        Phi = f0_series(Y * self.chi(eta), self.settings.series_terms)
        E = np.sqrt(2 * X) * self.angular_axis_factor(eta) * Phi
        U = 4 * eta + self.settings.j
        return E, U, Phi

    def scalar_fields(self, points, t=None):
        """Return rotation Ω=u_theta/r, speed, and coordinate diagnostics."""
        points = np.asarray(points, dtype=float)
        X, eta, q = self.similarity(points, t)
        E, U, Phi = self.profiles(X, eta)
        omega = q ** (-1 - self.settings.h) * self.angular_axis_factor(eta) * Phi
        # Exact derivative of q^(-A) U_*(eta), since A+D=1.
        axial_strain = (4 * (1 - eta ** 2) - 2 * self.A * eta * U) / (q * self.L(eta))
        uz = q ** (-self.A) * U
        r = np.hypot(points[..., 0], points[..., 1])
        ur = -.5 * r * axial_strain
        utheta = r * omega
        inside = (X <= self.X_limit * (1 + 1e-10)) & (np.abs(eta) <= self.settings.eta_limit * (1 + 1e-10))
        return dict(X=X, Y=self.settings.Lambda * X, eta=eta, q=q, E=E, U=U,
                    Phi=Phi, omega=omega, rotation_angular=omega,
                    axial_strain=axial_strain, ur=ur, utheta=utheta, uz=uz,
                    speed=np.sqrt(ur * ur + utheta * utheta + uz * uz), inside=inside)

    def velocity(self, points, t=None):
        """Cartesian comparison velocity; smooth on the axis, no division by r.

        The caller must stop displayed curves outside scalar_fields()['inside'].
        This function permits nearby out-of-domain stages of an ODE integrator.
        """
        points = np.asarray(points, dtype=float)
        f = self.scalar_fields(points, t)
        x, y = points[..., 0], points[..., 1]
        contraction = -.5 * f['axial_strain']
        return np.stack((contraction * x - f['omega'] * y,
                         contraction * y + f['omega'] * x, f['uz']), axis=-1)

    def angular_velocity(self, points, t=None):
        """Angular rotation Ω; this is NOT the vorticity vector curl(u)."""
        return self.scalar_fields(points, t)['omega']

    def metadata(self):
        return {
            "status": "comparaison asymptotique locale, paramètres exploratoires non certifiés pour le théorème",
            "not_a_navier_stokes_solution": True,
            "settings": asdict(self.settings),
            "X_limit": self.X_limit,
            "eta_peak": self.eta_peak,
            "C_real": float(np.exp(self.log_C_real)),
            "C": float(self.settings.amplitude_margin * np.exp(self.log_C_real)),
            "normalization": "C=1.05 fois le max réel de phi_* par défaut; le voisinage complexe B.16 et C0(Lambda) ne sont pas calculés",
            "velocity": "U=U_*; Phi=f0(Y chi); E=sqrt(2X) phi_*/C Phi; ur par incompressibilité exacte",
            "units": "coordonnées sans dimension; aucune calibration en mètres ou secondes",
            "rotation_legend": "omega=u_theta/r, vitesse angulaire (ce n'est pas curl(u))",
            "omissions": [
                "correction axiale -Y Z_*/(2 Lambda L), faute de pression globale calculée",
                "point fixe non linéaire de la proposition B.2",
                "raccordements, profil extérieur, perturbations oscillatoires, localisation, force",
                "certification des seuils Lambda0, C0, condition B.2 sur sigma et constantes d'erreur",
            ],
            "errors": "erreurs numériques testées séparément; erreur de modèle non bornée numériquement",
            "source": "sources/navier-stokes.pdf, pp. 7–8 et 144–148, équations (3.2), (B.1), (B.3), (B.11)–(B.13)",
        }
