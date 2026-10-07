"""Render a numerically generated, vertex-coloured PLY with Blender 4.5+.

Usage (run with Blender's Python, not the system interpreter)::

    blender --background --python rendering/blender_scene.py -- \
        --input output/render3d/vortex.ply --outdir output/render3d \
        --frames 72 --width 1400 --height 1100 --samples 48

The PLY geometry is translated and *uniformly* scaled for display. Its source
coordinates and every display transform are retained as custom properties.
The turntable changes the camera only: it is not a time-dependent fluid flow.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    parser.add_argument("--title", default="Structure locale d’un vortex")
    parser.add_argument(
        "--subtitle", default="Approximation locale — pas la solution complète"
    )
    parser.add_argument("--frames", type=int, default=0)
    parser.add_argument("--fps", type=int, default=24)
    parser.add_argument("--width", type=int, default=1400)
    parser.add_argument("--height", type=int, default=1100)
    parser.add_argument("--samples", type=int, default=48)
    parser.add_argument("--frame-samples", type=int, default=24)
    parser.add_argument("--engine", choices=("CYCLES", "BLENDER_EEVEE_NEXT"), default="CYCLES")
    parser.add_argument("--skip-hero", action="store_true")
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    args = parser.parse_args(argv)
    if min(args.width, args.height, args.samples, args.frame_samples, args.fps) <= 0:
        parser.error("Image size, samples and fps must be positive")
    if args.frames < 0:
        parser.error("Frame count must be nonnegative")
    if not args.input.is_file():
        parser.error(f"PLY not found: {args.input}")
    return args


def reset_scene(args):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = args.engine
    scene.render.resolution_x = args.width
    scene.render.resolution_y = args.height
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = False
    scene.render.fps = args.fps
    scene.render.use_file_extension = True
    scene.render.threads_mode = "AUTO"
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 0
    if args.engine == "CYCLES":
        scene.cycles.device = "CPU"
        scene.cycles.samples = args.samples
        scene.cycles.use_denoising = True
        scene.cycles.use_adaptive_sampling = True
        scene.cycles.adaptive_threshold = 0.025
        scene.cycles.max_bounces = 6
        scene.cycles.diffuse_bounces = 3
        scene.cycles.glossy_bounces = 3
        scene.cycles.transmission_bounces = 2
    world = bpy.data.worlds.new("Fond bleu encre")
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.015, 0.028, 0.053, 1)
    background.inputs["Strength"].default_value = 0.32
    scene.world = world
    scene["scientific_scope"] = args.subtitle
    scene["source_ply"] = str(args.input.resolve())
    scene["animation_kind"] = "Camera turntable at fixed model time; not fluid evolution"
    scene["tube_width"] = "Graphical thickness only; supplied by geometry generator"
    return scene


def import_geometry(args):
    bpy.ops.wm.ply_import(filepath=str(args.input.resolve()))
    meshes = [obj for obj in bpy.context.selected_objects if obj.type == "MESH"]
    if not meshes:
        raise RuntimeError("The PLY contains no mesh")
    # Joining is safe here: all imported geometry shares the PLY frame.
    bpy.context.view_layer.objects.active = meshes[0]
    if len(meshes) > 1:
        bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    obj.name = "Vortex — géométrie calculée"
    obj.data.name = "PLY source — tubes graphiques"
    if len(obj.data.vertices) == 0 or len(obj.data.polygons) == 0:
        raise RuntimeError("The PLY must contain a nonempty triangulated surface")
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    lower = Vector(tuple(min(p[k] for p in corners) for k in range(3)))
    upper = Vector(tuple(max(p[k] for p in corners) for k in range(3)))
    extent = upper - lower
    if max(extent) <= 0:
        raise RuntimeError("Degenerate PLY bounds")
    centre = (lower + upper) / 2
    factor = 6.4 / max(extent)
    obj.location = -centre * factor
    obj.scale = (factor, factor, factor)
    obj["source_bounds_min"] = list(lower)
    obj["source_bounds_max"] = list(upper)
    obj["display_uniform_scale"] = factor
    obj["display_translation"] = list(obj.location)
    obj["scientific_scope"] = args.subtitle
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    bpy.context.view_layer.update()
    bounds = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]

    attributes = obj.data.color_attributes
    if len(attributes) == 0:
        raise RuntimeError("PLY has no vertex RGB attribute; refusing an invented colour map")
    colour_attribute = attributes.active_color or attributes[0]
    obj["source_colour_attribute"] = colour_attribute.name
    material = bpy.data.materials.new("Couleurs numériques du PLY")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    shader = nodes.get("Principled BSDF")
    shader.inputs["Metallic"].default_value = 0.22
    shader.inputs["Roughness"].default_value = 0.3
    shader.inputs["Coat Weight"].default_value = 0.2
    shader.inputs["Coat Roughness"].default_value = 0.28
    attribute = nodes.new("ShaderNodeVertexColor")
    attribute.layer_name = colour_attribute.name
    attribute.label = "RGB exporté par le calcul"
    attribute.location = (-320, 50)
    material.node_tree.links.new(attribute.outputs["Color"], shader.inputs["Base Color"])
    material.node_tree.links.new(attribute.outputs["Color"], shader.inputs["Emission Color"])
    shader.inputs["Emission Strength"].default_value = 0.07
    obj.data.materials.clear()
    obj.data.materials.append(material)
    return obj, bounds, {
        "source_min": list(lower),
        "source_max": list(upper),
        "uniform_scale": factor,
        "translation": list(obj.location),
        "colour_attribute": colour_attribute.name,
        "vertices": len(obj.data.vertices),
        "faces": len(obj.data.polygons),
    }


def area_light(name, location, energy, size, colour):
    data = bpy.data.lights.new(name, type="AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = colour
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (-obj.location).to_track_quat("-Z", "Y").to_euler()
    return obj


def studio():
    area_light("Key — grande boîte douce", (6, -7, 8), 1600, 7, (0.93, 0.96, 1))
    area_light("Fill — lecture des courbes", (-7, -3, 2), 900, 6, (0.81, 0.91, 1))
    area_light("Rim — contour haut", (3, 5, 7), 1800, 5, (1, 0.9, 0.8))
    area_light("Rim — contour bas", (-4, 3, -5), 850, 5, (0.69, 0.89, 1))


def position_camera(camera, angle, distance):
    elevation = math.radians(12)
    camera.location = Vector((
        distance * math.cos(elevation) * math.cos(angle),
        distance * math.cos(elevation) * math.sin(angle),
        distance * math.sin(elevation),
    ))
    camera.rotation_euler = (-camera.location).to_track_quat("-Z", "Y").to_euler()


def make_camera(scene, bounds):
    data = bpy.data.cameras.new("Caméra scientifique — perspective 70 mm")
    camera = bpy.data.objects.new("Caméra", data)
    bpy.context.collection.objects.link(camera)
    scene.camera = camera
    data.type = "PERSP"
    data.lens = 70
    data.sensor_fit = "HORIZONTAL"
    data.sensor_width = 36
    data.clip_start = 0.01
    data.clip_end = 1000
    data.dof.use_dof = False
    # Bounds are tested over a full revolution; the geometry cannot be clipped
    # halfway through a turntable. Extra head/foot room protects the captions.
    aspect = scene.render.resolution_x / scene.render.resolution_y
    tan_half_x = data.sensor_width / (2 * data.lens)
    tan_half_y = tan_half_x / aspect
    distance = 0.0
    for i in range(72):
        angle = 2 * math.pi * i / 72
        position_camera(camera, angle, 1)
        orientation = camera.rotation_euler.to_matrix()
        right = orientation @ Vector((1, 0, 0))
        up = orientation @ Vector((0, 1, 0))
        towards_camera = orientation @ Vector((0, 0, 1))
        for p in bounds:
            depth = p.dot(towards_camera)
            distance = max(
                distance,
                depth + abs(p.dot(right)) / (tan_half_x * 0.86),
                depth + abs(p.dot(up)) / (tan_half_y * 0.71),
            )
    distance = max(distance, 8)
    position_camera(camera, math.radians(-58), distance)
    return camera, distance


def font_file(bold=False):
    candidates = (
        ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
        if bold else
        ["/System/Library/Fonts/Supplemental/Arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    )
    for candidate in candidates:
        if Path(candidate).is_file():
            return bpy.data.fonts.load(candidate)
    return None


def emission_material(name, colour):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    emission.inputs["Color"].default_value = (*colour, 1)
    emission.inputs["Strength"].default_value = 1
    material.node_tree.links.new(emission.outputs[0], output.inputs["Surface"])
    return material


def caption(camera, scene, name, text, x, y, size, material, font=None):
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = text
    curve.size = size
    curve.space_character = 1.04
    curve.align_x = "LEFT"
    curve.align_y = "BOTTOM_BASELINE"
    curve.resolution_u = 12
    if font:
        curve.font = font
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.parent = camera
    obj.location = (x, y, -2.5)
    obj.data.materials.append(material)
    if hasattr(obj, "visible_shadow"):
        obj.visible_shadow = False
    bpy.context.view_layer.update()
    # Keep long French subtitles inside the frame without manually truncating.
    half_width = 2.5 * camera.data.sensor_width / (2 * camera.data.lens)
    max_width = half_width * 1.8
    if obj.dimensions.x > max_width:
        obj.scale *= max_width / obj.dimensions.x
    return obj


def captions(args, scene, camera):
    half_width = 2.5 * camera.data.sensor_width / (2 * camera.data.lens)
    half_height = half_width * args.height / args.width
    x = -0.9 * half_width
    title_material = emission_material("Typographie — ivoire", (0.81, 0.89, 0.98))
    sub_material = emission_material("Typographie — bleu gris", (0.45, 0.61, 0.74))
    caption(camera, scene, "Titre", args.title, x, 0.86 * half_height,
            0.076 * half_height, title_material, font_file(True))
    caption(camera, scene, "Portée scientifique", args.subtitle, x, -0.855 * half_height,
            0.058 * half_height, title_material, font_file(False))
    caption(camera, scene, "Note de lecture", "Tubes d’épaisseur graphique · Instant figé · Vue 3D",
            x, -0.926 * half_height, 0.043 * half_height, sub_material, font_file(False))


def main():
    args = arguments()
    args.outdir.mkdir(parents=True, exist_ok=True)
    scene = reset_scene(args)
    obj, bounds, transform = import_geometry(args)
    studio()
    camera, distance = make_camera(scene, bounds)
    captions(args, scene, camera)
    scene.frame_start = 1
    scene.frame_end = max(1, args.frames)

    # Keyframed cameras make the saved .blend independently inspectable.
    if args.frames > 0:
        for index in range(args.frames + 1):
            frame = index + 1
            angle = math.radians(-58) + 2 * math.pi * index / args.frames
            position_camera(camera, angle, distance)
            camera.keyframe_insert(data_path="location", frame=frame)
            camera.keyframe_insert(data_path="rotation_euler", frame=frame)
        if camera.animation_data and camera.animation_data.action:
            # Blender 4.5's layered actions expose channels through slots.
            action = camera.animation_data.action
            try:
                for fcurve in action.fcurves:
                    for point in fcurve.keyframe_points:
                        point.interpolation = "LINEAR"
            except AttributeError:
                pass
    scene.frame_set(1)
    position_camera(camera, math.radians(-58), distance)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.spaces.active.region_3d.view_perspective = "CAMERA"

    manifest = {
        "input": str(args.input.resolve()),
        "scope": args.subtitle,
        "title": args.title,
        "display_transform": transform,
        "blender_version": bpy.app.version_string,
        "engine": args.engine,
        "image_size": [args.width, args.height],
        "camera_turntable_frames": args.frames,
        "camera_turntable_fps": args.fps,
        "camera_only_animation": True,
        "physical_time_changes": False,
        "camera_distance_display_units": distance,
        "note": "Uniform scale and translation preserve geometry proportions. Lighting changes display colours; original RGB and scalar data remain in source files.",
    }
    (args.outdir / "blender_render.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    scene.render.filepath = str((args.outdir / "hero.png").resolve())
    # Pack fonts so the blend is portable and its scope annotation stays intact.
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str((args.outdir / "vortex.blend").resolve()))
    if not args.skip_hero:
        print("Rendering hero image", flush=True)
        bpy.ops.render.render(write_still=True)
    if args.frames > 0:
        frames_path = args.outdir / "turntable"
        frames_path.mkdir(exist_ok=True)
        if args.engine == "CYCLES":
            scene.cycles.samples = args.frame_samples
        for index in range(args.frames):
            scene.frame_set(index + 1)
            # Explicit placement also handles Euler wrap at +/- pi exactly.
            angle = math.radians(-58) + 2 * math.pi * index / args.frames
            position_camera(camera, angle, distance)
            scene.render.filepath = str((frames_path / f"frame_{index + 1:04d}.png").resolve())
            print(f"Rendering camera frame {index + 1}/{args.frames}", flush=True)
            bpy.ops.render.render(write_still=True)
        scene.frame_set(1)
        position_camera(camera, math.radians(-58), distance)
    print(f"Finished: {args.outdir.resolve()}", flush=True)


if __name__ == "__main__":
    main()
