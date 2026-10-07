#!/usr/bin/env python3
"""Exact similarity-coordinate geometry, separate from any velocity model.

Run: .venv/bin/python rendering/coordinate_geometry.py --outdir output/render3d/geometry
The chosen coordinate box is illustrative and is not a certified core domain.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "navier-render-mpl"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import MaxNLocator
import numpy as np
from scipy.integrate import quad
import pyvista as pv

BG = "#07131f"
PANEL = "#0b1d2c"
TEXT = "#e6f3f4"
MUTED = "#9ab1bd"
CYAN = "#42d3d6"
COPPER = "#eda76e"
GRID = "#294250"
H = 0.0005
XC = 0.2
ETAC = 0.6
D = 0.5 - H
CMAP = LinearSegmentedColormap.from_list("geometry_height", [CYAN, "#3980a1", COPPER])


def mapping(X, eta, theta, tau, h=H):
    X, eta, theta = np.broadcast_arrays(X, eta, theta)
    q = tau / (1 - eta * eta)
    r = np.sqrt(2 * X * q)
    z = eta * q ** (0.5 - h)
    return np.stack((r * np.cos(theta), r * np.sin(theta), z), axis=-1), q


def mesh(tau, n_eta=128, n_theta=192):
    """Closed, outward-oriented triangulation, including the two plane caps."""
    eta, theta = np.meshgrid(np.linspace(-ETAC, ETAC, n_eta + 1),
                             np.linspace(0, 2 * np.pi, n_theta, endpoint=False), indexing="ij")
    points, q = mapping(XC, eta, theta, tau)
    points = points.reshape(-1, 3)
    top_center, _ = mapping(0, ETAC, 0, tau)
    bottom_center, _ = mapping(0, -ETAC, 0, tau)
    n = len(points)
    points = np.vstack((points, bottom_center, top_center))
    faces = []
    for j in range(n_eta):
        for k in range(n_theta):
            a, b = j * n_theta + k, j * n_theta + (k + 1) % n_theta
            c, d = (j + 1) * n_theta + k, (j + 1) * n_theta + (k + 1) % n_theta
            faces.extend(((a, b, d), (a, d, c)))
    for k in range(n_theta):
        faces.append((n, (k + 1) % n_theta, k))
        a = n_eta * n_theta + k
        b = n_eta * n_theta + (k + 1) % n_theta
        faces.append((n + 1, a, b))
    triangles = np.asarray(faces, dtype=np.int32)
    poly = pv.PolyData(points, np.column_stack((np.full(len(triangles), 3), triangles)).ravel())
    eta_points = np.r_[eta.ravel(), -ETAC, ETAC]
    poly.point_data["eta_coordinate"] = eta_points
    poly.point_data["X_coordinate"] = np.r_[np.full(n, XC), 0., 0.]
    poly.point_data["q"] = tau / (1 - eta_points ** 2)
    poly.point_data["RGB"] = np.round(255 * CMAP((eta_points + ETAC) / (2 * ETAC))[:, :3]).astype(np.uint8)
    return poly, triangles


def exact_volume(tau):
    integral, err = quad(lambda eta: (1 - 2 * H * eta ** 2) / (1 - eta ** 2) ** (D + 2),
                         -ETAC, ETAC, epsabs=1e-12, epsrel=1e-12)
    return 2 * np.pi * XC * tau ** (1 + D) * integral, 2 * np.pi * XC * tau ** (1 + D) * err


def measures(tau):
    rmax = np.sqrt(2 * XC * tau / (1 - ETAC ** 2))
    zmax = ETAC * (tau / (1 - ETAC ** 2)) ** D
    return {"tau": float(tau), "t": float(1 - tau), "radius_at_equator": float(np.sqrt(2 * XC * tau)),
            "max_radius": float(rmax), "half_height": float(zmax), "height": float(2 * zmax),
            "height_over_diameter": float(zmax / rmax), "volume": float(exact_volume(tau)[0]),
            "radius_factor_vs_tau_1": float(tau ** 0.5), "height_factor_vs_tau_1": float(tau ** D),
            "aspect_factor_vs_tau_1": float(tau ** -H), "volume_factor_vs_tau_1": float(tau ** (1.5 - H))}


def style():
    plt.rcParams.update({"figure.facecolor": BG, "axes.facecolor": PANEL, "savefig.facecolor": BG,
                         "text.color": TEXT, "axes.labelcolor": MUTED, "xtick.color": MUTED,
                         "ytick.color": MUTED, "axes.edgecolor": GRID, "grid.color": GRID,
                         "font.family": "DejaVu Sans", "font.size": 11})


def draw_3d(ax, tau=1., zoom=1., ghost=False):
    ax.set_facecolor(BG)
    theta, eta = np.meshgrid(np.linspace(0, 2 * np.pi, 81), np.linspace(-ETAC, ETAC, 49))
    pts, _ = mapping(XC, eta, theta, tau)
    pts *= zoom
    color = CMAP((eta + ETAC) / (2 * ETAC))
    color[:, :, 3] = 0.57
    if ghost:
        for e in [-ETAC, 0, ETAC]:
            p, _ = mapping(XC, e, np.linspace(0, 2*np.pi, 101), 1.)
            ax.plot(*p.T, color=MUTED, alpha=.22, lw=.75)
        for th in np.linspace(0, 2*np.pi, 9)[:-1]:
            p, _ = mapping(XC, np.linspace(-ETAC, ETAC, 80), th, 1.)
            ax.plot(*p.T, color=MUTED, alpha=.16, lw=.65)
    ax.plot_surface(pts[:,:,0], pts[:,:,1], pts[:,:,2], facecolors=color,
                    rstride=2, cstride=2, linewidth=0, antialiased=True, shade=True)
    # Coordinate contours only: they are neither streamlines nor material layers.
    for e in np.linspace(-ETAC, ETAC, 9):
        p, _ = mapping(XC, e, np.linspace(0, 2*np.pi, 129), tau)
        ax.plot(*(p * zoom).T, color=CMAP((e + ETAC)/(2*ETAC)), lw=1.05, alpha=.95)
    for th in np.linspace(0, 2*np.pi, 13)[:-1]:
        p, _ = mapping(XC, np.linspace(-ETAC, ETAC, 101), th, tau)
        ax.plot(*(p * zoom).T, color=TEXT, lw=.50, alpha=.35)
    for e in [-ETAC, ETAC]:
        rt, th = np.meshgrid(np.linspace(0, 1, 8), np.linspace(0, 2*np.pi, 65))
        p, _ = mapping(XC * rt ** 2, e, th, tau)
        p *= zoom
        ax.plot_surface(p[:,:,0], p[:,:,1], p[:,:,2], color=CMAP((e+ETAC)/(2*ETAC)), alpha=.16, shade=False)
    ax.plot([0, 0], [0, 0], [-1, 1], lw=.8, color=MUTED, alpha=.8)
    ax.set(xlim=(-1, 1), ylim=(-1, 1), zlim=(-1, 1))
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=15, azim=-55)
    ax.set_axis_off()


def draw_section(ax, tau=1., zoom=1., reference=False):
    eta = np.linspace(-ETAC, ETAC, 401)
    if reference:
        p, _ = mapping(XC, eta, 0., 1.)
        for sign in [-1, 1]:
            ax.plot(sign*p[:,0], p[:,2], "--", color=MUTED, lw=1., alpha=.38)
        ax.plot([-p[0,0],p[0,0]], [p[0,2],p[0,2]], "--", color=MUTED, lw=1., alpha=.38)
        ax.plot([-p[-1,0],p[-1,0]], [p[-1,2],p[-1,2]], "--", color=MUTED, lw=1., alpha=.38)
    for X, alpha in [(XC, .16), (XC/2, .09), (XC/4, .06)]:
        p, _ = mapping(X, eta, 0., tau)
        p *= zoom
        ax.fill_betweenx(p[:,2], -p[:,0], p[:,0], color=CYAN, alpha=alpha)
        for sign in [-1, 1]:
            ax.plot(sign*p[:,0], p[:,2], color=CYAN if X == XC else "#408091", lw=1.8 if X == XC else .8)
        for idx in [0, -1]:
            ax.plot([-p[idx,0], p[idx,0]], [p[idx,2], p[idx,2]], color=CYAN if X==XC else "#408091", lw=1.)
    p,_=mapping(XC, np.array([-ETAC, 0, ETAC]),0.,tau)
    p*=zoom
    ax.plot([-p[1,0],p[1,0]],[0,0],color=COPPER,lw=1.4)
    ax.axvline(0,color=MUTED,ls=":",lw=.75)
    ax.set(xlim=(-.92,.92),ylim=(-.92,.92),xlabel="distance à l’axe (signée)",ylabel="hauteur z")
    ax.set_aspect("equal")
    ax.xaxis.set_major_locator(MaxNLocator(5))
    ax.yaxis.set_major_locator(MaxNLocator(5))
    ax.grid(alpha=.5,lw=.5)
    for s in ax.spines.values(): s.set_visible(False)


def create_still(outdir):
    fig = plt.figure(figsize=(16, 10), dpi=180)
    fig.text(.05,.938,"GÉOMÉTRIE CALCULÉE",fontsize=10,color=CYAN,weight="bold",ha="left")
    fig.text(.05,.894,"Un domaine qui se concentre vers l’axe",fontsize=26,weight="bold")
    fig.text(.05,.856,"Coordonnées de similitude • exemple illustratif • temps strictement avant la singularité",color=MUTED,fontsize=11)
    ax = fig.add_axes([.03,.275,.53,.56],projection="3d")
    draw_3d(ax)
    fig.text(.08,.79,"01  /  SURFACE 3D",fontsize=10,weight="bold",color=CYAN)
    fig.text(.075,.29,"Les anneaux et les méridiens sont une grille de coordonnées.",color=MUTED,fontsize=10)
    fig.text(.075,.269,"Couleur = hauteur normalisée η ; aucune vitesse n’est représentée.",color=MUTED,fontsize=10)
    sec = fig.add_axes([.64,.415,.275,.355])
    draw_section(sec)
    fig.text(.64,.79,"02  /  COUPE PAR L’AXE",fontsize=10,weight="bold",color=CYAN)
    sec.text(.03,.95,"X = 0,05 ; 0,10 ; 0,20",transform=sec.transAxes,va="top",fontsize=9,color=MUTED)
    fig.text(.64,.329,"Paramètres de cet exemple",fontsize=12,weight="bold")
    fig.text(.64,.298,"h = 0,0005   ·   Xc = 0,20   ·   |η| ≤ 0,60   ·   τ = 1",fontsize=10,color=MUTED)
    fig.text(.05,.209,"Quand τ passe de 1 à 0,01",fontsize=15,weight="bold")
    for xpos,value,label in [(.05,"÷ 10","rayon"),(.275,"÷ 9,977","hauteur"),(.50,"+ 0,231 %","élancement"),(.725,"÷ 997,7","volume de la région")]:
        fig.text(xpos,.151,value,fontsize=24,weight="bold",color=CYAN if xpos<.5 else COPPER)
        fig.text(xpos,.12,label,fontsize=10,color=MUTED)
    fig.text(.05,.064,"Cette surface n’est pas une frontière matérielle et n’est pas la solution complète de Navier–Stokes.",fontsize=10,color=TEXT)
    fig.text(.05,.040,"Xc et ηc sont choisis pour visualiser les coordonnées ; leur inclusion dans le domaine des profils n’est pas certifiée. Unités normalisées.",fontsize=9,color=MUTED)
    path=outdir/"geometrie_coordonnees.png"
    fig.savefig(path,dpi=180)
    plt.close(fig)
    return path


def create_animation(outdir, frames=90, fps=18):
    ffmpeg=shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required to render the contraction video")
    width,height=1600,1000
    fig=plt.figure(figsize=(16,10),dpi=100)
    fig.text(.045,.948,"CONTRACTION D’UN DOMAINE DE COORDONNÉES",fontsize=11,weight="bold",color=CYAN)
    fig.text(.045,.898,"Le rayon et la hauteur diminuent ensemble",fontsize=26,weight="bold")
    fig.text(.045,.857,"Même calcul dans les deux vues. Le panneau de droite grossit uniformément l’image.",fontsize=11,color=MUTED)
    ax=fig.add_axes([.035,.225,.47,.605],projection="3d")
    sec=fig.add_axes([.612,.318,.288,.47])
    fig.text(.055,.802,"ÉCHELLE SPATIALE FIXE",fontsize=10,color=CYAN,weight="bold")
    fig.text(.62,.802,"ZOOM ISOTROPE DE LA RÉGION",fontsize=10,color=COPPER,weight="bold")
    timer=fig.text(.055,.22,"",fontsize=15,weight="bold")
    zoomlabel=fig.text(.62,.235,"",fontsize=14,weight="bold",color=COPPER)
    stats=fig.text(.055,.158,"",fontsize=14,color=TEXT)
    fig.text(.055,.117,"Contour grisé = taille à τ = 1. L’augmentation d’élancement reste minime : + 0,231 % sur toute la séquence.",fontsize=10,color=MUTED)
    fig.text(.055,.081,"h = 0,0005 · Xc = 0,20 · |η| ≤ 0,60 · unités normalisées · τ = 1 − t",fontsize=10,color=MUTED)
    fig.text(.055,.057,"τ est échantillonné logarithmiquement : la durée du film ne représente pas le temps physique.",fontsize=10,color=MUTED)
    fig.text(.055,.033,"Région illustrative, pas frontière matérielle ; ni trajectoires de particules ni champ complet. La caméra reste immobile.",fontsize=10,color=MUTED)
    outfile=outdir/"contraction_echelle_fixe_et_zoom.mp4"
    proc=subprocess.Popen([ffmpeg,"-y","-f","rawvideo","-vcodec","rawvideo","-s",f"{width}x{height}","-pix_fmt","rgba","-r",str(fps),"-i","-","-an","-c:v","libx264","-crf","19","-preset","fast","-pix_fmt","yuv420p","-movflags","+faststart",str(outfile)],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    frame_taus=[]
    for i in range(frames):
        # Logarithmic tau sampling. Frames have equal playback duration, not equal physical Δt.
        tau=10 ** (-2*i/(frames-1))
        zoom=tau**-.5
        ax.clear();sec.clear()
        draw_3d(ax,tau=tau,ghost=True)
        draw_section(sec,tau=tau,zoom=zoom)
        sec.set_xlabel("distance à l’axe × grossissement",fontsize=10)
        sec.set_ylabel("hauteur z × grossissement",fontsize=10)
        timer.set_text(f"τ = {tau:.4f}   ·   t = {1-tau:.4f}")
        zoomlabel.set_text(f"Grossissement affiché : × {zoom:.2f}")
        stats.set_text(f"Rayon × {tau**.5:.4f}     Hauteur × {tau**D:.4f}     Élancement × {tau**-H:.6f}")
        fig.canvas.draw()
        proc.stdin.write(fig.canvas.buffer_rgba())
        if i in {0,frames//2,frames-1}:
            fig.savefig(outdir/f"contraction_instant_{i:03d}.png",dpi=100)
        frame_taus.append({"frame":i,"video_seconds":i/fps,"tau":tau,"t":1-tau,"isotropic_zoom":zoom})
    proc.stdin.close()
    stderr=proc.stderr.read().decode("utf-8",errors="replace")
    ret=proc.wait()
    plt.close(fig)
    if ret:
        raise RuntimeError(f"ffmpeg failed: {stderr[-2000:]}")
    (outdir/"animation_times.json").write_text(json.dumps({"sampling":"logarithmic in tau; constant playback frame rate is NOT physical time", "frames":frame_taus},indent=2)+"\n")
    return outfile


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir",type=Path,default=Path("output/render3d/geometry"))
    parser.add_argument("--frames",type=int,default=90)
    parser.add_argument("--no-video",action="store_true")
    args=parser.parse_args()
    if args.frames < 2:
        parser.error("--frames must be at least 2")
    outdir=args.outdir.resolve();outdir.mkdir(parents=True,exist_ok=True)
    style()
    params={"object":"boundary of illustrative coordinate region", "scope_fr":"Géométrie des coordonnées ; paramètres illustratifs ; pas frontière matérielle. Domaine des profils non certifié.","h":H,"D":D,"Xc":XC,"eta_c":ETAC,"tau_values":[1.,.1,.01],"units":"normalized",
            "mapping":{"q":"tau/(1-eta^2)","r":"sqrt(2 X q)","z":"eta q^(1/2-h)"},
            "source_local":"NavierStokesAndEuler/NavierStokes/SimilarityCoordinates.lean",
            "color":"eta coordinate, NOT speed", "rotation_or_velocity_field":"not included"}
    (outdir/"parameters.json").write_text(json.dumps(params,ensure_ascii=False,indent=2)+"\n")
    rows=[];meshes=[]
    for tau in params["tau_values"]:
        poly,triangles=mesh(tau)
        label=f"tau_{tau:g}".replace(".","p")
        poly.save(outdir/f"region_{label}.vtp")
        poly.save(outdir/f"region_{label}.ply",texture="RGB")
        np.savez_compressed(outdir/f"region_{label}.npz",points=poly.points,triangles=triangles,
                            eta=poly["eta_coordinate"],X=poly["X_coordinate"],q=poly["q"],tau=tau,h=H)
        row=measures(tau);row["mesh_volume"]=float(poly.volume);rows.append(row);meshes.append(poly)
    with (outdir/"measurements.csv").open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    (outdir/"measurements.json").write_text(json.dumps(rows,indent=2)+"\n")
    rng=np.random.default_rng(1741)
    tau=10**rng.uniform(-2,0,5000);eta=rng.uniform(-ETAC,ETAC,5000);X=rng.uniform(.00001,XC,5000)
    p,q=mapping(X,eta,rng.uniform(0,2*np.pi,5000),tau)
    identity=np.max(np.abs(q-p[:,2]**2*q**(2*H)-tau)/tau)
    Xback=(p[:,0]**2+p[:,1]**2)/(2*q)
    etaback=p[:,2]/q**D
    coarse,_=mesh(1.,32,48)
    fine=meshes[0]
    v,verr=exact_volume(1.)
    scale_expected=meshes[0].points*np.array([.1,.1,.01**D])
    scaling=np.max(np.abs(meshes[-1].points-scale_expected))
    volume_errors={"coarse_32x48":float(abs(coarse.volume/v-1)),"fine_128x192":float(abs(fine.volume/v-1))}
    verification={"mapping_relative_residual_max":float(identity),"inverse_X_absolute_error_max":float(np.max(abs(Xback-X))),
                  "inverse_eta_absolute_error_max":float(np.max(abs(etaback-eta))),"anisotropic_scaling_max_absolute_error":float(scaling),
                  "quadrature_volume_tau_1":float(v),"quadrature_absolute_error_estimate":float(verr),
                  "mesh_relative_volume_errors":volume_errors,"mesh_volume_converges_on_refinement":volume_errors["fine_128x192"]<volume_errors["coarse_32x48"],
                  "closed_mesh_boundary_edge_count":int(fine.n_open_edges),"points":int(fine.n_points),"triangles":int(fine.n_cells),
                  "aspect_increase_tau_1_to_0p01_percent":float(100*(.01**-H-1)),
                  "physical_time_sampling":"The video samples log(tau); its playback rate is not physical time.",
                  "limitations":["Coordinate geometry only; no velocity field.","Xc and eta_c are illustrative, not certified as admissible profile-domain limits.","No claim of a material boundary, exact official-image reproduction, or full PDE solution."]}
    verification["passed"]=bool(identity<1e-12 and scaling<1e-12 and fine.n_open_edges==0 and volume_errors["fine_128x192"]<1e-3 and verification["mesh_volume_converges_on_refinement"])
    (outdir/"verification.json").write_text(json.dumps(verification,indent=2)+"\n")
    assert verification["passed"],verification
    create_still(outdir)
    if not args.no_video:
        create_animation(outdir,frames=args.frames)
    print(json.dumps({"outdir":str(outdir),"verification":verification},indent=2))


if __name__ == "__main__":
    main()
