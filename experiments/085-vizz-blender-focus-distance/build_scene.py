"""Build a reproducible Cycles scene for VIZZ focus/distance experiments.

Run from Blender, for example:

    blender --background --python build_scene.py -- --output-dir output --render

The scene deliberately keeps physical display geometry, observer distance and
focus offset separate. It does not use external images or network resources.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


SCENE_SCHEMA = "farmaxia:vizz-blender-focus-distance:0.1"
SCREEN_W = 0.420
SCREEN_H = SCREEN_W * 9.0 / 16.0
SCREEN_Y = 0.0
SCREEN_Z = 0.660
NEAR_Y = -0.220
NEAR_Z = SCREEN_Z
DEFAULT_DISTANCE = 0.600
DEFAULT_LENS_MM = 48.0
DEFAULT_FSTOP = 1.4


def parse_args() -> tuple[Path, bool]:
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    output_dir = Path("output")
    render = False
    index = 0
    while index < len(args):
        item = args[index]
        if item == "--output-dir" and index + 1 < len(args):
            output_dir = Path(args[index + 1])
            index += 2
            continue
        if item == "--render":
            render = True
        index += 1
    if not output_dir.is_absolute():
        output_dir = Path.cwd() / output_dir
    return output_dir.resolve(), render


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
    ):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)


def emission_material(name: str, color: tuple[float, float, float, float], strength: float) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    emission = nodes.new("ShaderNodeEmission")
    emission.inputs["Color"].default_value = color
    emission.inputs["Strength"].default_value = strength
    output = nodes.new("ShaderNodeOutputMaterial")
    links.new(emission.outputs["Emission"], output.inputs["Surface"])
    return material


def principled_material(
    name: str,
    color: tuple[float, float, float, float],
    roughness: float = 0.4,
    metallic: float = 0.0,
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    assert bsdf is not None
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return material


def assign_material(obj: bpy.types.Object, material: bpy.types.Material) -> bpy.types.Object:
    obj.data.materials.append(material)
    return obj


def add_cube(
    name: str,
    location: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    material: bpy.types.Material,
    bevel: float = 0.0,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign_material(obj, material)
    if bevel:
        modifier = obj.modifiers.new("soft_edges", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
    return obj


def add_text(
    name: str,
    body: str,
    location: tuple[float, float, float],
    size: float,
    material: bpy.types.Material,
    align_x: str = "CENTER",
) -> bpy.types.Object:
    bpy.ops.object.text_add(location=location, rotation=(math.radians(90.0), 0.0, 0.0))
    obj = bpy.context.object
    obj.name = name
    obj.data.body = body
    obj.data.align_x = align_x
    obj.data.align_y = "CENTER"
    obj.data.size = size
    obj.data.extrude = 0.0008
    obj.data.bevel_depth = 0.00015
    assign_material(obj, material)
    return obj


def add_torus(
    name: str,
    location: tuple[float, float, float],
    major_radius: float,
    minor_radius: float,
    material: bpy.types.Material,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_radius,
        minor_radius=minor_radius,
        major_segments=64,
        minor_segments=20,
        location=location,
        rotation=(math.radians(90.0), 0.0, 0.0),
    )
    obj = bpy.context.object
    obj.name = name
    assign_material(obj, material)
    return obj


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def add_area_light(
    name: str,
    location: tuple[float, float, float],
    energy: float,
    size: float,
    target: tuple[float, float, float],
) -> bpy.types.Object:
    bpy.ops.object.light_add(type="AREA", location=location)
    light = bpy.context.object
    light.name = name
    light.data.energy = energy
    light.data.shape = "DISK"
    light.data.size = size
    look_at(light, target)
    return light


def add_driver(
    id_block: bpy.types.ID,
    data_path: str,
    expression: str,
    targets: list[tuple[str, bpy.types.ID, str]],
    index: int = -1,
) -> None:
    driver = id_block.driver_add(data_path, index).driver
    for name, target_id, target_path in targets:
        variable = driver.variables.new()
        variable.name = name
        variable.type = "SINGLE_PROP"
        variable.targets[0].id = target_id
        variable.targets[0].data_path = target_path
    driver.expression = expression


def build_scene() -> tuple[bpy.types.Scene, bpy.types.Object, bpy.types.Object]:
    clear_scene()

    scene = bpy.context.scene
    scene.name = "VIZZ_FOCUS_DISTANCE_SCENE"
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 48
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 6
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world.color = (0.004, 0.006, 0.012)
    scene.render.fps = 24
    scene.frame_start = 1
    scene.frame_end = 120

    matte_black = principled_material("MATTE_BLACK", (0.008, 0.012, 0.020, 1.0), roughness=0.62)
    monitor_black = principled_material("MONITOR_FRAME", (0.012, 0.018, 0.028, 1.0), roughness=0.26, metallic=0.2)
    screen_blue = emission_material("SCREEN_EMISSION", (0.012, 0.08, 0.22, 1.0), 1.8)
    screen_white = emission_material("SCREEN_WHITE", (0.55, 0.80, 1.0, 1.0), 3.0)
    screen_cyan = emission_material("SCREEN_CYAN", (0.0, 0.75, 1.0, 1.0), 3.5)
    near_red = principled_material("NEAR_RED", (0.82, 0.025, 0.018, 1.0), roughness=0.22, metallic=0.05)
    near_gold = principled_material("NEAR_GOLD", (0.95, 0.33, 0.025, 1.0), roughness=0.3, metallic=0.12)
    near_white = principled_material("NEAR_WHITE", (0.72, 0.88, 1.0, 1.0), roughness=0.22, metallic=0.0)

    # A physical monitor: its front surface is toward negative Y, where the camera sits.
    add_cube("MONITOR_TOP", (0.0, 0.018, SCREEN_Z + SCREEN_H / 2 + 0.020), (0.500, 0.038, 0.040), monitor_black, 0.009)
    add_cube("MONITOR_BOTTOM", (0.0, 0.018, SCREEN_Z - SCREEN_H / 2 - 0.020), (0.500, 0.038, 0.040), monitor_black, 0.009)
    add_cube("MONITOR_LEFT", (-0.230, 0.018, SCREEN_Z), (0.040, 0.038, SCREEN_H), monitor_black, 0.009)
    add_cube("MONITOR_RIGHT", (0.230, 0.018, SCREEN_Z), (0.040, 0.038, SCREEN_H), monitor_black, 0.009)
    add_cube("SCREEN_PLANE", (0.0, 0.0, SCREEN_Z), (SCREEN_W, 0.010, SCREEN_H), screen_blue, 0.002)

    # High-frequency screen content: when the camera focuses on the near plane,
    # these edges visibly lose sharpness.
    for index, x in enumerate((-0.155, -0.105, -0.055, -0.005, 0.045, 0.095, 0.145)):
        add_cube(f"SCREEN_GRID_V_{index}", (x, -0.008, SCREEN_Z), (0.0018, 0.002, SCREEN_H * 0.82), screen_cyan)
    for index, z in enumerate((SCREEN_Z - 0.082, SCREEN_Z - 0.041, SCREEN_Z, SCREEN_Z + 0.041, SCREEN_Z + 0.082)):
        add_cube(f"SCREEN_GRID_H_{index}", (0.0, -0.009, z), (SCREEN_W * 0.82, 0.002, 0.0018), screen_cyan)
    add_text("SCREEN_LABEL", "SCREEN PLANE", (0.0, -0.014, SCREEN_Z + 0.060), 0.025, screen_white)
    add_text("SCREEN_DISTANCE_LABEL", "angular size changes with distance", (0.0, -0.014, SCREEN_Z - 0.065), 0.013, screen_white)
    add_text("SCREEN_FOCUS_LABEL", "focus plane = 0.00 m offset", (0.0, -0.014, SCREEN_Z - 0.095), 0.010, screen_white)

    # Floor and a thin rear wall make the light falloff visible without introducing
    # an external image or texture dependency.
    add_cube("FLOOR", (0.0, 0.30, -0.035), (2.4, 2.4, 0.05), matte_black, 0.01)
    add_cube("BACKDROP", (0.0, 0.62, 0.72), (2.4, 0.05, 1.7), matte_black, 0.01)

    # A near focus target, 220 mm in front of the screen. It intentionally carries
    # thin edges and a label so the focus transition is unambiguous.
    add_cube("NEAR_CARD", (-0.115, NEAR_Y, NEAR_Z), (0.105, 0.012, 0.140), near_red, 0.008)
    add_torus("NEAR_RING", (0.075, NEAR_Y - 0.012, NEAR_Z + 0.010), 0.062, 0.010, near_gold)
    add_torus("NEAR_RING_INNER", (0.075, NEAR_Y - 0.015, NEAR_Z + 0.010), 0.032, 0.005, near_white)
    add_text("NEAR_LABEL", "NEAR", (0.075, NEAR_Y - 0.025, NEAR_Z - 0.080), 0.020, near_white)
    add_text("NEAR_CARD_LABEL", "FOCUS", (-0.115, NEAR_Y - 0.020, NEAR_Z), 0.018, near_white)

    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0.075, NEAR_Y, NEAR_Z + 0.010))
    near_target = bpy.context.object
    near_target.name = "FOCUS_NEAR"
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0.0, SCREEN_Y, SCREEN_Z))
    screen_target = bpy.context.object
    screen_target.name = "FOCUS_SCREEN"

    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0.0, -0.02, SCREEN_Z - 0.17))
    controller = bpy.context.object
    controller.name = "VIZZ_CONTROLLER"
    controller["observer_distance_m"] = DEFAULT_DISTANCE
    controller["focus_distance_m"] = DEFAULT_DISTANCE
    controller["focus_offset_m"] = 0.0
    controller["screen_width_m"] = SCREEN_W
    controller["screen_height_m"] = SCREEN_H
    controller["near_plane_offset_m"] = NEAR_Y
    controller["contract"] = "observer distance controls camera Y; focus distance controls DOF plane"

    bpy.ops.object.camera_add(location=(0.0, -DEFAULT_DISTANCE, SCREEN_Z))
    camera = bpy.context.object
    camera.name = "VIZZ_CAMERA"
    camera.data.name = "VIZZ_CAMERA_DATA"
    camera.data.lens = DEFAULT_LENS_MM
    camera.data.sensor_width = 36.0
    camera.data.dof.use_dof = True
    camera.data.dof.aperture_fstop = DEFAULT_FSTOP
    camera.data.dof.aperture_blades = 8
    look_at(camera, (0.0, SCREEN_Y, SCREEN_Z))
    scene.camera = camera

    add_driver(
        camera,
        "location",
        "-distance",
        [("distance", controller, '["observer_distance_m"]')],
        index=1,
    )
    add_driver(
        camera.data.dof,
        "focus_distance",
        "focus + offset",
        [
            ("focus", controller, '["focus_distance_m"]'),
            ("offset", controller, '["focus_offset_m"]'),
        ],
    )

    # These are reference markers, not keyframes. The two experimental controls
    # must remain manually writable; animating the same custom properties would
    # make Blender restore a keyframed value during evaluation.
    for frame, label in ((1, "CLOSE 0.45 m"), (40, "REFERENCE 0.60 m"), (80, "FAR 1.00 m"), (120, "NEAR FOCUS")):
        scene.timeline_markers.new(label, frame=frame)

    add_area_light("KEY_LIGHT", (-0.45, -0.50, 1.25), 420.0, 0.70, (0.0, 0.0, SCREEN_Z))
    add_area_light("RIM_LIGHT", (0.45, 0.30, 1.15), 300.0, 0.50, (0.0, 0.0, SCREEN_Z))
    add_area_light("NEAR_FILL", (0.05, -0.45, 0.40), 160.0, 0.30, (0.0, NEAR_Y, NEAR_Z))

    scene["schema"] = SCENE_SCHEMA
    scene["screen_width_m"] = SCREEN_W
    scene["screen_height_m"] = SCREEN_H
    scene["near_plane_y_m"] = NEAR_Y
    scene["default_observer_distance_m"] = DEFAULT_DISTANCE
    scene["camera_lens_mm"] = DEFAULT_LENS_MM
    scene["camera_fstop"] = DEFAULT_FSTOP
    scene["render_engine"] = "CYCLES"
    scene["network_used"] = False
    scene["external_assets_used"] = False

    scene.frame_set(40)
    return scene, camera, controller


def set_variant(controller: bpy.types.Object, distance: float, focus_offset: float) -> None:
    # Keep the scene on the reference marker, update the independent controller,
    # then explicitly tag the ID so Blender 4.5 refreshes driver dependencies in
    # batch mode as well as in the UI.
    bpy.context.scene.frame_set(40)
    controller["observer_distance_m"] = distance
    controller["focus_distance_m"] = distance
    controller["focus_offset_m"] = focus_offset
    controller.update_tag(refresh={"DATA"})
    bpy.context.view_layer.update()


def render_variant(scene: bpy.types.Scene, controller: bpy.types.Object, output_dir: Path, filename: str, distance: float, focus_offset: float) -> None:
    set_variant(controller, distance, focus_offset)
    scene.render.filepath = str(output_dir / filename)
    bpy.ops.render.render(write_still=True)


def write_manifest(scene: bpy.types.Scene, camera: bpy.types.Object, controller: bpy.types.Object, output_dir: Path) -> None:
    manifest = {
        "schema": SCENE_SCHEMA,
        "scene": scene.name,
        "engine": scene.render.engine,
        "screen": {"width_m": SCREEN_W, "height_m": SCREEN_H, "aspect": "16:9"},
        "near_plane_y_m": NEAR_Y,
        "camera": {
            "name": camera.name,
            "lens_mm": camera.data.lens,
            "sensor_width_mm": camera.data.sensor_width,
            "aperture_fstop": camera.data.dof.aperture_fstop,
            "distance_control": "VIZZ_CONTROLLER[observer_distance_m]",
            "focus_control": "VIZZ_CONTROLLER[focus_distance_m] + focus_offset_m",
        },
        "variants": [
            {"file": "focus_screen_060m.png", "distance_m": 0.60, "focus_offset_m": 0.0},
            {"file": "focus_near_060m.png", "distance_m": 0.60, "focus_offset_m": NEAR_Y},
            {"file": "focus_screen_100m.png", "distance_m": 1.00, "focus_offset_m": 0.0},
        ],
        "safety": {"network_used": False, "external_assets_used": False, "input_injected": False},
        "unknowns": [
            "Cycles camera DOF is an optical-camera simulation, not a clinical model of accommodation.",
            "A flat emissive monitor does not create true binocular depth cues.",
            "Perceived comfort and fatigue require a separate human study.",
        ],
    }
    (output_dir / "scene_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def main() -> None:
    output_dir, render = parse_args()
    output_dir.mkdir(parents=True, exist_ok=True)
    scene, camera, controller = build_scene()
    write_manifest(scene, camera, controller, output_dir)
    if render:
        render_variant(scene, controller, output_dir, "focus_screen_060m.png", 0.60, 0.0)
        render_variant(scene, controller, output_dir, "focus_near_060m.png", 0.60, NEAR_Y)
        render_variant(scene, controller, output_dir, "focus_screen_100m.png", 1.00, 0.0)
        set_variant(controller, DEFAULT_DISTANCE, 0.0)
    scene.render.filepath = str(output_dir / "last_render.png")
    bpy.ops.wm.save_as_mainfile(filepath=str(output_dir / "vizz_focus_distance.blend"))
    print(json.dumps({
        "status": "VIZZ_BLENDER_FOCUS_DISTANCE_SCENE_BUILT",
        "blend": str(output_dir / "vizz_focus_distance.blend"),
        "rendered": render,
        "screen_m": [SCREEN_W, SCREEN_H],
        "near_plane_offset_m": NEAR_Y,
    }))


if __name__ == "__main__":
    main()
