"""Generate faithful streamlines of the explicit local comparison model.

This is not an implementation of the full blowup solution. See parameters.json.
The special comparison uz(z) permits an exact meridional first integral r² uz.
Only the angular equation is integrated numerically. Source velocities are kept.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pyvista as pv
from scipy.integrate import cumulative_simpson
from matplotlib.colors import LinearSegmentedColormap
from model import ComparisonModel


def streamlines(model, t, resolution=900):
    """Both branches of u_z, sampled densely near their separating plane."""
    p = model.settings
    eta0 = -p.j/4
    records=[]
    offsets=(1e-5, 1e-4, .001, .006)
    for side in (-1,1):
        for family, delta in enumerate(offsets):
            eta = eta0 + side*np.geomspace(delta, p.eta_limit-side*eta0, resolution)
            q = (1-t)/(1-eta**2)
            uz = q**(-model.A)*(4*eta+p.j)
            # A curve enters the displayed region near its radial rim.
            for ring,X_start in enumerate((.029, .044, .059)):
                r_start=np.sqrt(2*X_start*q[0])
                r=r_start*np.sqrt(uz[0]/uz)
                z=eta*q**model.D
                X=r*r/(2*q)
                omega=q**(-1-p.h)*model.angular_axis_factor(eta)*model.profiles(X,eta)[2]
                dz_deta=q**model.D*model.L(eta)/(1-eta**2)
                # eta decreases on the lower branch: integrate in a rising path parameter.
                angle_integrand=omega/uz*dz_deta*side
                theta=cumulative_simpson(angle_integrand,x=side*eta,initial=0)
                # Rotate copies around the axis, retaining actual z/r geometry.
                for azimuth in range(4):
                    phase=2*np.pi*azimuth/4 + .31*family + .15*ring
                    xyz=np.column_stack((r*np.cos(theta+phase),r*np.sin(theta+phase),z))
                    records.append(dict(points=xyz,omega=omega,theta=theta,eta=eta,X=X,
                                        family=family,side=side,ring=ring))
    return records


def create_polydata(model, records, t):
    points=np.concatenate([r['points'] for r in records])
    cells=[]; offset=0
    for r in records:
        n=len(r['points']); cells.extend((n,*range(offset,offset+n))); offset+=n
    mesh=pv.PolyData(points,lines=np.asarray(cells))
    f=model.scalar_fields(points,t)
    for name in ('omega','speed','ur','uz','utheta','X','eta'):
        mesh[name]=f[name]
    mesh['velocity']=model.velocity(points,t)
    return mesh


def scientific_preview(tubes, records, out, t, upper):
    cmap=LinearSegmentedColormap.from_list('copper_ice',['#24b6c8','#2684af','#506bc6','#d6a064','#f4c68b'])
    plot=pv.Plotter(off_screen=True,window_size=(1400,1100))
    plot.set_background('#0a1423')
    plot.add_mesh(tubes,scalars='omega',cmap=cmap,clim=(0,upper),smooth_shading=True,
                  scalar_bar_args={'title':'Rotation angulaire (sans dimension)', 'color':'#dce6f0',
                                   'vertical':False,'position_x':.25,'position_y':.04,'width':.5,'height':.07,
                                   'title_font_size':14,'label_font_size':12,'n_labels':3})
    plot.add_text('VORTEX | COMPARAISON LOCALE',position=(28,1040),font_size=18,color='#eaf0f7')
    plot.add_text(f't = {t:.2f} | Parametres exploratoires | Solution complete non reconstruite',
                  position=(28,1005),font_size=11,color='#a9bdd0')
    plot.add_axes(line_width=2,labels_off=False,color='#dce6f0')
    plot.camera_position=[(.42,-.64,.24),(0,0,0),(0,0,1)]
    plot.camera.zoom(1.14)
    plot.screenshot(str(out/'apercu_scientifique.png'))
    try:
        plot.trame.export_html(str(out/'vortex_interactif.html'))
        html_status='created'
    except Exception as exc:
        html_status=str(exc)
    plot.close()
    return html_status


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--outdir',type=Path,default=Path('output/render3d'))
    ap.add_argument('--preview',action='store_true')
    args=ap.parse_args(); out=args.outdir; out.mkdir(parents=True,exist_ok=True)
    model=ComparisonModel(); t=model.settings.time
    records=streamlines(model,t)
    mesh=create_polydata(model,records,t)
    extent=np.ptp(mesh.points,axis=0).max()
    radius=extent*.00115
    display_records=[]
    for record in records:
        index=np.unique(np.r_[np.arange(0,len(record['points']),4),len(record['points'])-1])
        display_records.append({'points':record['points'][index]})
    display_mesh=create_polydata(model,display_records,t)
    tubes=display_mesh.tube(radius=radius,n_sides=8,capping=True).triangulate()
    upper=float(np.max(mesh['omega']))
    cmap=LinearSegmentedColormap.from_list('copper_ice',['#24b6c8','#2684af','#506bc6','#d6a064','#f4c68b'])
    tubes['RGB']=(cmap(np.clip(tubes['omega']/upper,0,1))[:,:3]*255).round().astype(np.uint8)
    tubes.save(out/'vortex.ply',texture='RGB')
    tubes.save(out/'vortex_tubes.vtp')
    mesh.save(out/'lignes_de_courant.vtp')
    # Small enough for desktop inspection; axisymmetric sample reconstructed in 3D.
    X,eta,theta=np.meshgrid(np.linspace(0,model.X_limit,25),np.linspace(-.5,.5,81),np.linspace(0,2*np.pi,49),indexing='ij')
    points=model.points_from_similarity(X,eta,theta,t)
    grid=pv.StructuredGrid(points[...,0],points[...,1],points[...,2])
    gp=np.reshape(points,(-1,3),order='F')
    grid['velocity']=model.velocity(gp,t)
    fields=model.scalar_fields(gp,t)
    grid['omega']=fields['omega']; grid['speed']=fields['speed']
    grid.save(out/'champ_comparaison.vts')
    np.savez_compressed(out/'donnees_comparaison.npz',positions=gp,velocity=grid['velocity'],
                        omega=grid['omega'],speed=grid['speed'],curve_positions=mesh.points,
                        curve_velocity=mesh['velocity'],curve_omega=mesh['omega'])
    metadata=model.metadata()
    metadata['render']={'time':t,'curve_count':len(records),'points_per_curve':len(records[0]['points']),
                        'tube_radius_graphical':radius,'display_subsampling':4,'color_quantity':'angular velocity omega',
                        'color_scale':'linear','color_min':0,'color_max':upper,
                        'scope_label':'Comparaison locale — paramètres exploratoires, pas la solution complète'}
    metadata['sampled_grid']={'shape':[25,81,49],
                              'purpose':'grille d’aperçu ; zone étroite de rotation peu résolue axialement ; interpolations et gradients non certifiés',
                              'streamlines_independent_of_grid':True}
    # Meaningful checks: first integral, ODE tangency and independent quadrature refinement.
    flux_errors=[]; alignment=[]; max_outside=0
    for r in records:
        v=model.velocity(r['points'],t)
        rr=np.hypot(r['points'][:,0],r['points'][:,1])
        flux=rr**2*v[:,2]
        flux_errors.append(float(np.max(np.abs(flux/flux[0]-1))))
        tangent=np.gradient(r['points'],r['eta'],axis=0)*r['side']
        cosine=np.sum(tangent*v,axis=1)/(np.linalg.norm(tangent,axis=1)*np.linalg.norm(v,axis=1))
        alignment.extend(np.sqrt(np.maximum(0,1-cosine[3:-3]**2)))
        max_outside+=int(np.count_nonzero(~model.scalar_fields(r['points'],t)['inside']))
    finer=streamlines(model,t,resolution=1800)
    enddiff=max(abs(a['theta'][-1]-b['theta'][-1]) for a,b in zip(records,finer))
    checks={'flux_invariant_max_relative_error':max(flux_errors),
            'streamline_direction_error_sine_p99':float(np.quantile(alignment,.99)),
            'points_outside_comparison_domain':max_outside,
            'angle_change_doubling_resolution_radians':float(enddiff),
            'all_values_finite':bool(np.isfinite(mesh.points).all() and np.isfinite(mesh['velocity']).all()),
            'model_error_for_true_solution':'not bounded; omitted nonlinear and pressure corrections'}
    assert checks['all_values_finite'] and max_outside==0
    assert max(flux_errors)<1e-10 and enddiff<1e-4
    (out/'parameters.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
    (out/'streamline_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
    if args.preview:
        metadata['html_export']=scientific_preview(tubes,records,out,t,upper)
        (out/'parameters.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'curves':len(records),'vertices':tubes.n_points,'checks':checks,'preview':args.preview},indent=2))


if __name__=='__main__':main()
