"""Reproducible immersive rendering of the explicitly illustrative vortex.

Run with Blender, for example::

    .runtime/Blender.app/Contents/MacOS/Blender --background \
      --python-exit-code 1 --python rendering/immersive_blender.py -- \
      --input output/immersive/flow_data.json --outdir output/immersive \
      --frames 240 --fps 24 --encode

Colours follow the supplied illustrative omega values. White moving dashes are
direction cues; their animation does not integrate fluid particles or time.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import time

import bpy
from mathutils import Vector
import numpy as np


def arguments():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, default=Path("output/immersive/flow_data.json"))
    p.add_argument("--outdir", type=Path, default=Path("output/immersive"))
    p.add_argument("--width", type=int, default=1920)
    p.add_argument("--height", type=int, default=1080)
    p.add_argument("--frames", type=int, default=240)
    p.add_argument("--fps", type=int, default=24)
    p.add_argument("--samples", type=int, default=32)
    p.add_argument("--frame-samples", type=int, default=12)
    p.add_argument("--video-width", type=int, default=1280)
    p.add_argument("--video-height", type=int, default=720)
    p.add_argument("--engine", choices=("CYCLES", "BLENDER_EEVEE_NEXT"), default="CYCLES")
    p.add_argument("--tube-radius", type=float, default=0.003)
    p.add_argument("--encode", action="store_true")
    p.add_argument("--skip-hero", action="store_true")
    p.add_argument("--build-only", action="store_true")
    p.add_argument("--frames-only", action="store_true")
    args = p.parse_args(sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else [])
    if not args.input.is_file():
        p.error(f"Missing source JSON: {args.input}")
    if args.frames < 0 or min(args.width,args.height,args.fps,args.samples,args.frame_samples,args.video_width,args.video_height) <= 0:
        p.error("Dimensions, rates, and samples must be positive; frames nonnegative")
    return args


def reset(args):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version = 0
    scene = bpy.context.scene
    scene.render.engine = args.engine
    scene.render.resolution_x = args.width
    scene.render.resolution_y = args.height
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    scene.render.fps = args.fps
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 0.15
    if args.engine == "CYCLES":
        scene.cycles.device = "CPU"
        scene.cycles.samples = args.samples
        scene.cycles.use_denoising = True
        scene.cycles.use_adaptive_sampling = True
        scene.cycles.adaptive_threshold = 0.045
        scene.cycles.max_bounces = 4
        scene.cycles.diffuse_bounces = 2
        scene.cycles.glossy_bounces = 2
    elif hasattr(scene,"eevee"):
        scene.eevee.taa_render_samples = args.samples
    world = bpy.data.worlds.new("Nuit")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.006,0.015,0.035,1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.28
    scene.world = world
    scene["scientific_scope"] = "Illustration 3D · profils simplifiés"
    scene["moving_white_marks"] = "Graphical direction cues only, not physical particle integration"
    scene["animation"] = "Fixed illustrative geometry with moving direction cues and a 30-degree camera orbit"
    scene.use_nodes = True
    nodes = scene.node_tree.nodes
    nodes.clear()
    source = nodes.new("CompositorNodeRLayers")
    glare = nodes.new("CompositorNodeGlare")
    glare.glare_type = "FOG_GLOW"
    glare.quality = "HIGH"
    glare.threshold = 1.8
    glare.size = 7
    glare.mix = -0.9
    output = nodes.new("CompositorNodeComposite")
    scene.node_tree.links.new(source.outputs["Image"],glare.inputs["Image"])
    scene.node_tree.links.new(glare.outputs["Image"],output.inputs["Image"])
    return scene


def srgb_linear(rgb):
    rgb = np.asarray(rgb)
    return np.where(rgb <= .04045, rgb / 12.92, ((rgb + .055) / 1.055) ** 2.4)


def colour_map(omega, lower, upper):
    # Exact normalized cyan/pale-cyan/gold palette used by the companion viewer.
    normalized = np.clip((omega-lower)/max(upper-lower,1e-12),0,1)
    cyan=np.array([59,197,212])/255
    pale=np.array([151,227,230])/255
    gold=np.array([229,182,119])/255
    first=np.minimum(normalized/.8,1)[:,None]
    second=(np.maximum((normalized-.8)/.2,0)**.75)[:,None]
    rgb=np.where((normalized<=.8)[:,None],cyan+(pale-cyan)*first,pale+(gold-pale)*second)
    return srgb_linear(rgb)


def tube_mesh(curves, omegas, args):
    sides = 6
    all_points=[]; all_faces=[]; all_colours=[]
    lower = 0.
    upper = max(float(np.max(o)) for o in omegas)
    angle = np.arange(sides)*2*np.pi/sides
    offset = 0
    for xyz, omega in zip(curves,omegas):
        n = len(xyz)
        tangent = np.gradient(xyz,axis=0)
        tangent /= np.linalg.norm(tangent,axis=1)[:,None]
        radial = np.c_[xyz[:,0],xyz[:,1],np.zeros(n)]
        radial /= np.maximum(np.linalg.norm(radial,axis=1)[:,None],1e-12)
        normal = radial - np.sum(radial*tangent,axis=1)[:,None]*tangent
        weak = np.linalg.norm(normal,axis=1)<1e-4
        normal[weak] = np.cross(tangent[weak],np.array([0,0,1]))
        weak = np.linalg.norm(normal,axis=1)<1e-4
        normal[weak] = np.cross(tangent[weak],np.array([1,0,0]))
        normal /= np.linalg.norm(normal,axis=1)[:,None]
        binormal = np.cross(tangent,normal)
        # Slight graphical taper at the ends prevents blunt cylinders.
        taper = np.minimum(np.minimum(np.arange(n)/10,(n-1-np.arange(n))/10),1)
        radius = args.tube_radius*(.22+.78*taper)
        tube = xyz[:,None,:] + radius[:,None,None]*(np.cos(angle)[None,:,None]*normal[:,None,:]+np.sin(angle)[None,:,None]*binormal[:,None,:])
        all_points.append(tube.reshape(-1,3))
        all_colours.append(np.repeat(colour_map(omega,lower,upper),sides,axis=0))
        row=np.arange(n-1)[:,None]*sides + np.arange(sides)[None,:]
        nxt=np.arange(n-1)[:,None]*sides+(np.arange(sides)[None,:]+1)%sides
        all_faces.append(np.stack([row,nxt,nxt+sides,row+sides],axis=-1).reshape(-1,4)+offset)
        offset += n*sides
    points=np.concatenate(all_points)
    faces=np.concatenate(all_faces)
    colours=np.concatenate(all_colours)
    mesh=bpy.data.meshes.new("Tubes fins — couleur Ω illustrative")
    mesh.vertices.add(len(points))
    mesh.vertices.foreach_set("co",points.ravel())
    mesh.loops.add(faces.size)
    mesh.loops.foreach_set("vertex_index",faces.ravel())
    mesh.polygons.add(len(faces))
    mesh.polygons.foreach_set("loop_start",np.arange(0,faces.size,4))
    mesh.polygons.foreach_set("loop_total",np.full(len(faces),4))
    mesh.polygons.foreach_set("use_smooth",np.ones(len(faces),dtype=bool))
    mesh.update()
    attr=mesh.color_attributes.new(name="OmegaColour",type="FLOAT_COLOR",domain="POINT")
    attr.data.foreach_set("color",np.c_[colours,np.ones(len(colours))].ravel())
    obj=bpy.data.objects.new("Spirales calculées du modèle illustratif",mesh)
    bpy.context.collection.objects.link(obj)
    material=bpy.data.materials.new("Cyan → cyan pâle → or | Ω illustrative")
    material.use_nodes=True
    nodes=material.node_tree.nodes
    shader=nodes.get("Principled BSDF")
    shader.inputs["Metallic"].default_value=.65
    shader.inputs["Roughness"].default_value=.4
    shader.inputs["Coat Weight"].default_value=.06
    colour=nodes.new("ShaderNodeVertexColor")
    colour.layer_name="OmegaColour"
    material.node_tree.links.new(colour.outputs["Color"],shader.inputs["Base Color"])
    material.node_tree.links.new(colour.outputs["Color"],shader.inputs["Emission Color"])
    shader.inputs["Emission Strength"].default_value=.4
    mesh.materials.append(material)
    obj["tube_radius_graphical"]=args.tube_radius
    obj["omega_min_illustrative"]=lower
    obj["omega_max_illustrative"]=upper
    return obj,{"vertices":len(points),"faces":len(faces),"omega_min":lower,"omega_max":upper}


def luminous_material(name, colour, strength=1):
    mat=bpy.data.materials.new(name)
    mat.use_nodes=True
    nodes=mat.node_tree.nodes; nodes.clear()
    emission=nodes.new("ShaderNodeEmission")
    emission.inputs["Color"].default_value=(*colour,1)
    emission.inputs["Strength"].default_value=strength
    output=nodes.new("ShaderNodeOutputMaterial")
    mat.node_tree.links.new(emission.outputs[0],output.inputs["Surface"])
    return mat


def direction_cues(curves,args):
    group=bpy.data.collections.new("Repères blancs animés — pas des particules physiques")
    bpy.context.scene.collection.children.link(group)
    material=luminous_material("Repères — blanc froid",(.78,.93,1),2.3)
    total_frames=args.frames or 240
    for index,xyz in enumerate(curves):
        # Every curve remains available as an editable Blender spline.
        data=bpy.data.curves.new(f"Repère {index+1:03d}","CURVE")
        data.dimensions="3D"
        data.resolution_u=1
        data.bevel_depth=max(args.tube_radius*1.6,.0065)
        data.bevel_resolution=1
        data.use_fill_caps=True
        spline=data.splines.new("POLY")
        spline.points.add(len(xyz)-1)
        spline.points.foreach_set("co",np.c_[xyz,np.ones(len(xyz))].ravel())
        obj=bpy.data.objects.new(data.name,data)
        group.objects.link(obj)
        data.materials.append(material)
        # Irrational phase distributes marks without aligning neighbouring lines.
        phase=(index*.6180339887498949)%1
        width=.008+.004*((index*.41421356237)%1)
        cycles=.65+.15*((index*.2718281828)%1)
        for frame in range(1,total_frames+1):
            start=(phase+(frame-1)/total_frames*cycles)%(1-width)
            data.bevel_factor_start=start
            data.bevel_factor_end=start+width
            data.keyframe_insert(data_path="bevel_factor_start",frame=frame)
            data.keyframe_insert(data_path="bevel_factor_end",frame=frame)
        if hasattr(obj,"visible_shadow"):
            obj.visible_shadow=False
        obj["animation_semantics"]="Index increases in flow direction; dash speed is graphical"
    return len(curves)


def light(name,location,energy,size,colour):
    data=bpy.data.lights.new(name,"AREA")
    data.energy=energy; data.shape="DISK"; data.size=size; data.color=colour
    obj=bpy.data.objects.new(name,data); bpy.context.collection.objects.link(obj)
    obj.location=location
    obj.rotation_euler=(-obj.location).to_track_quat("-Z","Y").to_euler()


def camera_position(camera,angle,distance):
    elevation=math.radians(29)
    camera.location=(distance*math.cos(elevation)*math.cos(angle),distance*math.cos(elevation)*math.sin(angle),distance*math.sin(elevation))
    camera.rotation_euler=(-camera.location).to_track_quat("-Z","Y").to_euler()


def camera_and_titles(scene,curves,args):
    data=bpy.data.cameras.new("Caméra — 70 mm")
    camera=bpy.data.objects.new("Caméra — rotation douce",data)
    bpy.context.collection.objects.link(camera); scene.camera=camera
    data.lens=70; data.sensor_width=36; data.sensor_fit="HORIZONTAL"
    data.clip_start=.01; data.clip_end=1000
    points=np.concatenate([c[::4] for c in curves])
    tan_x=data.sensor_width/(2*data.lens)
    tan_y=tan_x*args.height/args.width
    distance=0
    for degrees in np.linspace(-65,-35,20):
        camera_position(camera,math.radians(degrees),1)
        orientation=np.array(camera.rotation_euler.to_matrix())
        local=points @ orientation
        distance=max(distance,float(np.max(local[:,2]+np.abs(local[:,0])/(tan_x*.91))),float(np.max(local[:,2]+np.abs(local[:,1])/(tan_y*.80))))
    animation_frames=args.frames or 240
    for frame in range(1,animation_frames+1):
        angle=math.radians(-65+30*(frame-1)/max(animation_frames-1,1))
        camera_position(camera,angle,distance)
        camera.keyframe_insert(data_path="location",frame=frame)
        camera.keyframe_insert(data_path="rotation_euler",frame=frame)
    camera_position(camera,math.radians(-58),distance)
    half_x=2.5*tan_x; half_y=2.5*tan_y
    font_path=Path("/System/Library/Fonts/Supplemental/Arial.ttf")
    font=bpy.data.fonts.load(str(font_path)) if font_path.is_file() else None
    bright=luminous_material("Texte — ivoire",(.65,.79,.86))
    dim=luminous_material("Texte — gris bleu",(.24,.37,.48))
    labels=[
        ("Spirale entrante · évacuation axiale",-.92*half_x,.88*half_y,.052*half_y,bright),
        ("Illustration 3D · profils simplifiés",-.92*half_x,-.90*half_y,.045*half_y,bright),
        ("Repères de direction animés · vitesse graphique",-.92*half_x,-.956*half_y,.032*half_y,dim),
    ]
    for name,x,y,size,material in labels:
        text=bpy.data.curves.new(name,"FONT")
        text.body=name; text.size=size; text.align_y="BOTTOM_BASELINE"
        if font: text.font=font
        obj=bpy.data.objects.new(name,text); bpy.context.collection.objects.link(obj)
        obj.parent=camera; obj.location=(x,y,-2.5); obj.data.materials.append(material)
        if hasattr(obj,"visible_shadow"): obj.visible_shadow=False
    return camera,distance


def encode(args):
    ffmpeg=shutil.which("ffmpeg") or "/usr/local/bin/ffmpeg"
    output=args.outdir/"animation_immersive.mp4"
    subprocess.run([ffmpeg,"-hide_banner","-loglevel","error","-y","-framerate",str(args.fps),"-start_number","1","-i",str(args.outdir/"frames"/"frame_%04d.png"),"-c:v","libx264","-crf","18","-preset","medium","-pix_fmt","yuv420p","-movflags","+faststart",str(output)],check=True)
    return output


def main():
    args=arguments(); args.outdir.mkdir(parents=True,exist_ok=True)
    start=time.time()
    payload=json.loads(args.input.read_text())
    curves=[np.asarray(c,dtype=float).reshape(-1,3) for c in payload["positions"]]
    omegas=[np.asarray(o,dtype=float).reshape(-1) for o in payload["omega"]]
    if len(curves)!=len(omegas) or not curves:
        raise ValueError("Positions/omega counts do not match")
    for c,o in zip(curves,omegas):
        if len(c)!=len(o) or len(c)<3 or not np.isfinite(c).all() or not np.isfinite(o).all():
            raise ValueError("Invalid illustrative curve data")
    scene=reset(args)
    obj,stats=tube_mesh(curves,omegas,args)
    marker_count=direction_cues(curves,args)
    light("Key — studio",(6,-8,9),800,8,(.88,.95,1))
    light("Fill — contours",(-7,-3,4),525,7,(.65,.88,1))
    light("Rim — haut",(2,6,8),900,6,(1,.86,.66))
    light("Rim — bas",(-3,3,-7),550,5,(.83,.94,1))
    camera,distance=camera_and_titles(scene,curves,args)
    scene.frame_start=1; scene.frame_end=args.frames or 240
    scene.frame_set(1)
    bpy.context.view_layer.objects.active=obj
    bpy.ops.object.select_all(action="DESELECT"); obj.select_set(True)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=="VIEW_3D":
                area.spaces.active.region_3d.view_perspective="CAMERA"
                area.spaces.active.shading.color_type="VERTEX"
    bpy.ops.file.pack_all()
    scene.render.filepath=str((args.outdir/"apercu_immersif.png").resolve())
    bpy.ops.wm.save_as_mainfile(filepath=str((args.outdir/"vortex_immersif.blend").resolve()))
    record={
        "scope":"Illustration 3D · profils simplifiés",
        "source_json":str(args.input.resolve()),
        "source_sha256":hashlib.sha256(args.input.read_bytes()).hexdigest(),
        "blender_version":bpy.app.version_string,
        "engine":args.engine,
        "hero_samples":args.samples,
        "frame_samples":args.frame_samples,
        "curves":len(curves),
        "curve_points":sum(len(c) for c in curves),
        "mesh":stats,
        "tube_radius_graphical":args.tube_radius,
        "coordinate_transform":"none; physical proportions of illustrative JSON preserved",
        "source_is_full_navier_stokes_solution":False,
        "colour_quantity":"omega from the illustrative source JSON, linear range",
        "colour_palette":{"cyan":"#3bc5d4","pale_cyan":"#97e3e6","gold":"#e5b677","pale_cyan_stop":.8,"gold_interpolation_exponent":.75},
        "white_marks_are_particles":False,
        "white_marks_meaning":"direction cues, constant illustrative progression in curve parameter",
        "white_mark_count":marker_count,
        "camera_orbit_degrees":30,
        "camera_elevation_degrees":29,
        "camera_distance":distance,
        "still_resolution":[args.width,args.height],
        "video_resolution":[args.video_width,args.video_height],
        "frames":args.frames,"fps":args.fps,
        "source_metadata":payload.get("metadata",{}),
    }
    if not args.build_only:
        if not args.skip_hero and not args.frames_only:
            print("Rendering immersive still",flush=True)
            bpy.ops.render.render(write_still=True)
        if args.frames:
            frames=args.outdir/"frames"; frames.mkdir(exist_ok=True)
            scene.render.resolution_x=args.video_width; scene.render.resolution_y=args.video_height
            if args.engine=="CYCLES": scene.cycles.samples=args.frame_samples
            elif hasattr(scene,"eevee"): scene.eevee.taa_render_samples=args.frame_samples
            for frame in range(1,args.frames+1):
                scene.frame_set(frame)
                scene.render.filepath=str((frames/f"frame_{frame:04d}.png").resolve())
                print(f"Immersive frame {frame}/{args.frames}",flush=True)
                bpy.ops.render.render(write_still=True)
            if args.encode: encode(args)
    record["elapsed_seconds"]=time.time()-start
    (args.outdir/"reprocheck.json").write_text(json.dumps(record,indent=2,ensure_ascii=False)+"\n")
    print(f"Immersive render finished in {time.time()-start:.1f} seconds",flush=True)


if __name__=="__main__":
    main()
