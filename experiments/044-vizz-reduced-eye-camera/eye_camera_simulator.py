"""Reduced-eye / camera model for VIZZ.

This is the corrected first optical layer before binocular rendering.  A
screen point is treated as a luminous source.  Several rays from that point
pass through a finite pupil and an equivalent thin lens before reaching a
fixed retinal plane.  The application renders both the ray bundles and the
resulting inverted retinal grid.

It intentionally models the cornea + crystalline lens as one equivalent
paraxial lens.  That is a declared reduced-eye approximation, not a clinical
eye model.
"""

from __future__ import annotations

import math
import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk


@dataclass(frozen=True)
class Point3:
    x: float
    y: float
    z: float


@dataclass(frozen=True)
class ScreenPose:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.72
    width: float = 0.72
    height: float = 0.42


@dataclass(frozen=True)
class EyeOptics:
    name: str
    focal_x: float
    focal_y: float
    retina: float
    color: str
    description: str


def normal_focal_length(screen_distance: float, retina_distance: float) -> float:
    return 1.0 / (1.0 / screen_distance + 1.0 / retina_distance)


DEFAULT_RETINA = 0.017
DEFAULT_DISTANCE = 0.72
NORMAL_FOCAL = normal_focal_length(DEFAULT_DISTANCE, DEFAULT_RETINA)

EYE_PRESETS: tuple[EyeOptics, ...] = (
    EyeOptics("Normal reducido", NORMAL_FOCAL, NORMAL_FOCAL, DEFAULT_RETINA, "#60a5fa", "foco sobre la retina en 72 cm"),
    EyeOptics("Miopía conceptual", 0.01505, 0.01505, DEFAULT_RETINA, "#ff6b6b", "foco delante de la retina"),
    EyeOptics("Hipermetropía conceptual", 0.01811, 0.01811, DEFAULT_RETINA, "#ffd166", "foco detrás de la retina"),
    EyeOptics("Astigmatismo conceptual", 0.01505, 0.01811, DEFAULT_RETINA, "#c77dff", "dos focos lineales en meridianos distintos"),
)


@dataclass(frozen=True)
class PupilSample:
    x: float
    y: float


@dataclass(frozen=True)
class RetinalTrace:
    source: Point3
    hits: tuple[Point3, ...]
    centroid: Point3
    blur_rms: float
    focus_x: float
    focus_y: float
    image_center_x: float
    image_center_y: float


@dataclass(frozen=True)
class MeridianRay:
    aperture_height: float
    incoming_slope: float
    outgoing_slope: float
    retina_height: float
    focus_height: float


@dataclass(frozen=True)
class MeridianTrace:
    object_height: float
    object_distance: float
    focal_length: float
    retina_distance: float
    image_distance: float
    focus_height: float
    rays: tuple[MeridianRay, ...]


LENS_Z = 0.0
PUPIL_SAMPLE_TEMPLATE: tuple[tuple[float, float], ...] = (
    (0.0, 0.0),
    (-1.0, 0.0),
    (1.0, 0.0),
    (0.0, -1.0),
    (0.0, 1.0),
)
GRID_U: tuple[float, ...] = (-0.75, -0.25, 0.25, 0.75)
GRID_V: tuple[float, ...] = (-0.70, -0.23, 0.23, 0.70)


def pupil_samples(radius: float) -> tuple[PupilSample, ...]:
    return tuple(PupilSample(radius * x, radius * y) for x, y in PUPIL_SAMPLE_TEMPLATE)


def screen_point(pose: ScreenPose, u: float, v: float) -> Point3:
    return Point3(pose.x + u * pose.width / 2.0, pose.y + v * pose.height / 2.0, pose.z)


def image_distance(focal_length: float, object_distance: float) -> float:
    """Gaussian thin-lens equation: 1/f = 1/u + 1/v."""

    if focal_length <= 0 or object_distance <= focal_length:
        raise ValueError("object must be farther than focal length")
    return focal_length * object_distance / (object_distance - focal_length)


def trace_screen_point(
    optics: EyeOptics,
    source: Point3,
    pupil_radius: float,
    samples: tuple[PupilSample, ...] | None = None,
) -> RetinalTrace:
    """Trace one screen point through a finite pupil to the retina.

    Coordinates use the eye's optical axis as +z toward the screen.  Light
    travels from the screen at z=u toward the lens at z=0 and then to the
    retina at z=-retina.  At the equivalent thin lens, the paraxial slopes
    change by ``-aperture_height/f`` in each meridian.
    """

    samples = samples or pupil_samples(pupil_radius)
    object_distance = source.z - LENS_Z
    if object_distance <= max(optics.focal_x, optics.focal_y):
        raise ValueError("screen is inside the focal distance")
    hits: list[Point3] = []
    for aperture in samples:
        incoming_x = (aperture.x - source.x) / object_distance
        incoming_y = (aperture.y - source.y) / object_distance
        outgoing_x = incoming_x - aperture.x / optics.focal_x
        outgoing_y = incoming_y - aperture.y / optics.focal_y
        hits.append(
            Point3(
                aperture.x + optics.retina * outgoing_x,
                aperture.y + optics.retina * outgoing_y,
                -optics.retina,
            )
        )
    centroid_x = sum(hit.x for hit in hits) / len(hits)
    centroid_y = sum(hit.y for hit in hits) / len(hits)
    blur_rms = math.sqrt(
        sum((hit.x - centroid_x) ** 2 + (hit.y - centroid_y) ** 2 for hit in hits) / len(hits)
    )
    return RetinalTrace(
        source=source,
        hits=tuple(hits),
        centroid=Point3(centroid_x, centroid_y, -optics.retina),
        blur_rms=blur_rms,
        focus_x=image_distance(optics.focal_x, object_distance),
        focus_y=image_distance(optics.focal_y, object_distance),
        image_center_x=-optics.retina * source.x / object_distance,
        image_center_y=-optics.retina * source.y / object_distance,
    )


def trace_meridian(
    object_height: float,
    object_distance: float,
    focal_length: float,
    retina_distance: float,
    aperture_radius: float,
) -> MeridianTrace:
    """Trace a 2D finite-aperture bundle for a side-view diagram."""

    v = image_distance(focal_length, object_distance)
    rays: list[MeridianRay] = []
    for aperture_height in (-aperture_radius, 0.0, aperture_radius):
        incoming = (aperture_height - object_height) / object_distance
        outgoing = incoming - aperture_height / focal_length
        retina_height = aperture_height + retina_distance * outgoing
        focus_height = aperture_height + v * outgoing
        rays.append(MeridianRay(aperture_height, incoming, outgoing, retina_height, focus_height))
    return MeridianTrace(object_height, object_distance, focal_length, retina_distance, v, -(v / object_distance) * object_height, tuple(rays))


def focus_state(focus_distance: float, retina_distance: float) -> str:
    if focus_distance < retina_distance - 1e-6:
        return "antes de retina"
    if focus_distance > retina_distance + 1e-6:
        return "detrás de retina"
    return "sobre retina"


def retinal_grid(optics: EyeOptics, pose: ScreenPose, pupil_radius: float) -> tuple[RetinalTrace, ...]:
    return tuple(
        trace_screen_point(optics, screen_point(pose, u, v), pupil_radius)
        for v in GRID_V
        for u in GRID_U
    )


class EyeCameraSimulator:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("VIZZ 044 · cámara reducida: luz, foco y retina")
        self.root.geometry("1320x900")
        self.root.minsize(1120, 780)
        self.screen_x = tk.DoubleVar(value=0.0)
        self.screen_y = tk.DoubleVar(value=0.0)
        self.screen_z = tk.DoubleVar(value=DEFAULT_DISTANCE)
        self.pupil_radius = tk.DoubleVar(value=0.0025)
        self.model_name = tk.StringVar(value=EYE_PRESETS[0].name)
        self.show_rays = tk.BooleanVar(value=True)
        self.readout = tk.StringVar()
        self.status = tk.StringVar(value="La luz viaja pantalla → pupila → lente equivalente → retina.")

        self.canvas = tk.Canvas(root, background="#07111f", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.panel = tk.Frame(root, width=300, background="#111827")
        self.panel.pack(side=tk.RIGHT, fill=tk.Y)
        self.panel.pack_propagate(False)
        self._build_panel()

        for key, axis, delta in (
            ("<Left>", "x", -0.01),
            ("<Right>", "x", 0.01),
            ("<Up>", "y", 0.01),
            ("<Down>", "y", -0.01),
            ("<Prior>", "z", -0.02),
            ("<Next>", "z", 0.02),
        ):
            root.bind(key, lambda _event, a=axis, d=delta: self._nudge(a, d))
        root.bind("<KeyPress-r>", lambda _event: self._reset())
        root.bind("<KeyPress-space>", lambda _event: self._toggle_rays())
        root.bind("<Configure>", lambda _event: self.draw())
        self.draw()

    def _build_panel(self) -> None:
        tk.Label(
            self.panel,
            text="VIZZ 044\nOJO · CÁMARA · RETINA",
            font=("Segoe UI", 15, "bold"),
            foreground="#f9fafb",
            background="#111827",
            justify=tk.LEFT,
            anchor="w",
        ).pack(fill=tk.X, padx=18, pady=(20, 8))
        tk.Label(
            self.panel,
            text="Primero validamos una sola proyección óptica.\nLa retina se dibuja como plano de recepción\ny la imagen invertida se compara con la pantalla.",
            font=("Segoe UI", 9),
            foreground="#cbd5e1",
            background="#111827",
            justify=tk.LEFT,
            anchor="w",
        ).pack(fill=tk.X, padx=18, pady=(0, 14))

        tk.Label(self.panel, text="Modelo reducido", foreground="#e5e7eb", background="#111827", anchor="w").pack(fill=tk.X, padx=18, pady=(4, 0))
        model_box = ttk.Combobox(
            self.panel,
            textvariable=self.model_name,
            values=[item.name for item in EYE_PRESETS],
            state="readonly",
        )
        model_box.pack(fill=tk.X, padx=18, pady=(2, 8))
        model_box.bind("<<ComboboxSelected>>", lambda _event: self.draw())
        self._add_scale("Pantalla izquierda ↔ derecha", self.screen_x, -0.25, 0.25, 0.01)
        self._add_scale("Pantalla abajo ↔ arriba", self.screen_y, -0.18, 0.18, 0.01)
        self._add_scale("Distancia pantalla ↔ lente", self.screen_z, 0.38, 1.20, 0.01)
        self._add_scale("Radio de pupila", self.pupil_radius, 0.0012, 0.0040, 0.0001)
        ttk.Separator(self.panel).pack(fill=tk.X, padx=18, pady=12)
        tk.Label(self.panel, textvariable=self.readout, font=("Consolas", 8), foreground="#93c5fd", background="#111827", justify=tk.LEFT, anchor="w").pack(fill=tk.X, padx=18, pady=(0, 12))
        for label, command in (("Restablecer (R)", self._reset), ("Mostrar/ocultar rayos (Espacio)", self._toggle_rays)):
            tk.Button(self.panel, text=label, command=command, relief=tk.FLAT, background="#1f2937", foreground="#e5e7eb", activebackground="#334155", activeforeground="#ffffff", padx=8, pady=6).pack(fill=tk.X, padx=18, pady=3)
        tk.Label(self.panel, textvariable=self.status, font=("Segoe UI", 9), foreground="#a7f3d0", background="#111827", justify=tk.LEFT, wraplength=260, anchor="w").pack(fill=tk.X, padx=18, pady=(18, 8))
        tk.Label(self.panel, text="Teclas:\n← → ↑ ↓ mover pantalla\nPageUp/PageDown distancia\nR reinicia · Espacio rayos", font=("Segoe UI", 8), foreground="#94a3b8", background="#111827", justify=tk.LEFT, anchor="w").pack(fill=tk.X, padx=18, pady=(0, 12))

    def _add_scale(self, label: str, variable: tk.DoubleVar, minimum: float, maximum: float, resolution: float) -> None:
        tk.Label(self.panel, text=label, font=("Segoe UI", 9), foreground="#e5e7eb", background="#111827", anchor="w").pack(fill=tk.X, padx=18, pady=(4, 0))
        tk.Scale(self.panel, variable=variable, from_=minimum, to=maximum, resolution=resolution, orient=tk.HORIZONTAL, showvalue=False, command=lambda _value: self.draw(), background="#111827", foreground="#cbd5e1", troughcolor="#334155", highlightthickness=0, activebackground="#60a5fa").pack(fill=tk.X, padx=14, pady=(0, 4))

    def _selected_model(self) -> EyeOptics:
        return next(item for item in EYE_PRESETS if item.name == self.model_name.get())

    def _pose(self) -> ScreenPose:
        return ScreenPose(self.screen_x.get(), self.screen_y.get(), self.screen_z.get())

    def _nudge(self, axis: str, delta: float) -> None:
        variable = {"x": self.screen_x, "y": self.screen_y, "z": self.screen_z}[axis]
        limits = {"x": (-0.25, 0.25), "y": (-0.18, 0.18), "z": (0.38, 1.20)}[axis]
        variable.set(max(limits[0], min(limits[1], variable.get() + delta)))
        self.draw()

    def _reset(self) -> None:
        self.screen_x.set(0.0)
        self.screen_y.set(0.0)
        self.screen_z.set(DEFAULT_DISTANCE)
        self.pupil_radius.set(0.0025)
        self.model_name.set(EYE_PRESETS[0].name)
        self.status.set("Modelo reducido normal: el foco coincide con la retina a 72 cm.")
        self.draw()

    def _toggle_rays(self) -> None:
        self.show_rays.set(not self.show_rays.get())
        self.status.set("Rayos visibles." if self.show_rays.get() else "Rayos ocultos; la proyección sigue calculándose.")
        self.draw()

    def _project_xz(
        self,
        z: float,
        transverse: float,
        bounds: tuple[float, float, float, float],
        screen_distance: float,
    ) -> tuple[float, float]:
        """Project an optical cut with separate scene and eye scales.

        The screen-to-eye distance and the lens-to-retina distance differ by
        roughly two orders of magnitude.  A single metric canvas scale makes
        the retina disappear beside the lens, so this view is deliberately a
        schematic: screen, lens and retina keep their order while each ray
        segment is drawn in its own readable interval.
        """

        left, top, width, height = bounds
        screen_x = left + width * 0.14
        lens_x = left + width * 0.50
        retina_x = left + width * 0.86
        if z >= 0.0:
            scene_fraction = min(1.0, max(0.0, z / max(screen_distance, 1e-9)))
            px = lens_x + scene_fraction * (screen_x - lens_x)
        else:
            eye_fraction = -z / DEFAULT_RETINA
            px = lens_x + eye_fraction * (retina_x - lens_x)
        py = top + height * 0.55 - transverse * min(170.0, (height - 70.0) / 0.28)
        return px, py

    def _draw_meridian(self, bounds: tuple[float, float, float, float], optics: EyeOptics, pose: ScreenPose, meridian: str) -> MeridianTrace:
        left, top, width, height = bounds
        source = screen_point(pose, 0.58, 0.0) if meridian == "horizontal" else screen_point(pose, 0.0, 0.58)
        object_height = source.x if meridian == "horizontal" else source.y
        focal = optics.focal_x if meridian == "horizontal" else optics.focal_y
        trace = trace_meridian(object_height, pose.z, focal, optics.retina, self.pupil_radius.get())
        axis_y = top + height * 0.55
        self.canvas.create_rectangle(left, top, left + width, top + height, outline="#1e3a5f")
        self.canvas.create_text(left + 8, top + 8, text=f"{meridian.upper()} · luz → retina", fill="#e2e8f0", anchor="nw", font=("Segoe UI", 9, "bold"))
        self.canvas.create_line(left + 10, axis_y, left + width - 10, axis_y, fill="#334155", dash=(2, 4))
        screen_x, _ = self._project_xz(pose.z, 0.0, bounds, pose.z)
        lens_x, _ = self._project_xz(0.0, 0.0, bounds, pose.z)
        retina_x, _ = self._project_xz(-optics.retina, 0.0, bounds, pose.z)
        self.canvas.create_oval(lens_x - 16, top + 48, retina_x + 18, top + height - 34, outline="#334155", dash=(5, 3))
        self.canvas.create_arc(lens_x - 15, axis_y - 28, lens_x + 7, axis_y + 28, start=270, extent=180, outline="#cbd5e1", width=2)
        self.canvas.create_line(screen_x, top + 35, screen_x, top + height - 18, fill="#60a5fa", width=2)
        self.canvas.create_line(lens_x, top + 35, lens_x, top + height - 18, fill="#f8fafc", width=2)
        self.canvas.create_oval(lens_x - 7, axis_y - 25, lens_x + 7, axis_y + 25, outline="#f8fafc", width=2)
        self.canvas.create_line(retina_x, top + 35, retina_x, top + height - 18, fill="#f87171", width=2)
        self.canvas.create_text(screen_x, top + height - 3, text="pantalla", fill="#93c5fd", anchor="s", font=("Segoe UI", 7))
        self.canvas.create_text(lens_x, top + height - 3, text="pupila + lente", fill="#e2e8f0", anchor="s", font=("Segoe UI", 7))
        self.canvas.create_text(retina_x, top + height - 3, text="retina", fill="#fca5a5", anchor="s", font=("Segoe UI", 7))
        self.canvas.create_text(lens_x + 10, top + 44, text="ojo reducido", fill="#94a3b8", anchor="sw", font=("Segoe UI", 7))

        source_y = axis_y - object_height * min(170.0, (height - 70.0) / 0.28)
        self.canvas.create_oval(screen_x - 5, source_y - 5, screen_x + 5, source_y + 5, fill="#ffffff", outline="#60a5fa")
        self.canvas.create_text(screen_x, source_y - 10, text="S", fill="#f8fafc", font=("Segoe UI", 8))
        focus_z = trace.image_distance
        focus_x, focus_y = self._project_xz(-focus_z, trace.focus_height, bounds, pose.z)
        if self.show_rays.get():
            for ray in trace.rays:
                aperture_y = axis_y - ray.aperture_height * min(170.0, (height - 70.0) / 0.28)
                retina_y = axis_y - ray.retina_height * min(170.0, (height - 70.0) / 0.28)
                focus_ray_y = axis_y - ray.focus_height * min(170.0, (height - 70.0) / 0.28)
                self.canvas.create_line(screen_x, source_y, lens_x, aperture_y, fill="#7dd3fc", width=1, arrow=tk.LAST)
                self.canvas.create_line(lens_x, aperture_y, retina_x, retina_y, fill=optics.color, width=2, arrow=tk.LAST)
                if focus_z > optics.retina + 1e-9:
                    self.canvas.create_line(retina_x, retina_y, focus_x, focus_ray_y, fill=optics.color, width=1, dash=(3, 3))
        self.canvas.create_oval(focus_x - 5, focus_y - 5, focus_x + 5, focus_y + 5, fill=optics.color, outline="#ffffff")
        self.canvas.create_text(focus_x, top + 8, text=f"foco {focus_z * 1000:.2f} mm", fill=optics.color, anchor="ne", font=("Consolas", 7))
        self.canvas.create_text(left + width - 8, top + 8, text=focus_state(focus_z, optics.retina), fill=optics.color, anchor="ne", font=("Segoe UI", 8, "bold"))
        return trace

    def _draw_front_plane(self, bounds: tuple[float, float, float, float], optics: EyeOptics, pose: ScreenPose, retinal: bool) -> None:
        left, top, width, height = bounds
        side = min(width - 30, height - 38)
        cx = left + width * 0.5
        cy = top + height * 0.56
        scale = side / pose.width if not retinal else side / pose.width * pose.z / optics.retina
        self.canvas.create_rectangle(cx - side / 2, cy - side * pose.height / pose.width / 2, cx + side / 2, cy + side * pose.height / pose.width / 2, outline="#93c5fd" if not retinal else "#f87171", width=2)
        self.canvas.create_text(left + 8, top + 8, text="RETINA · imagen invertida" if retinal else "PANTALLA · imagen original", fill="#fca5a5" if retinal else "#bfdbfe", anchor="nw", font=("Segoe UI", 9, "bold"))
        grid = retinal_grid(optics, pose, self.pupil_radius.get()) if retinal else None
        for v in GRID_V:
            y = cy - v * side * pose.height / pose.width / 2
            self.canvas.create_line(cx - side / 2, y, cx + side / 2, y, fill="#28547a", width=1)
        for u in GRID_U:
            x = cx + u * side / 2
            self.canvas.create_line(x, cy - side * pose.height / pose.width / 2, x, cy + side * pose.height / pose.width / 2, fill="#28547a", width=1)
        if not retinal:
            self.canvas.create_line(cx, cy + 25, cx, cy - 25, fill="#f8fafc", width=2, arrow=tk.LAST)
        else:
            assert grid is not None
            for trace in grid:
                for hit in trace.hits:
                    x = cx + hit.x * scale
                    y = cy - hit.y * scale
                    self.canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill=optics.color, outline="")
                x = cx + trace.centroid.x * scale
                y = cy - trace.centroid.y * scale
                self.canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill="#ffffff", outline=optics.color)
            self.canvas.create_line(cx, cy - 25, cx, cy + 25, fill="#f8fafc", width=2, arrow=tk.LAST)
        marker_u, marker_v = -0.55, 0.55
        marker_x = cx + marker_u * side / 2.0
        marker_y = cy - marker_v * side * pose.height / pose.width / 2.0
        if retinal:
            marker_trace = trace_screen_point(
                optics,
                screen_point(pose, marker_u, marker_v),
                self.pupil_radius.get(),
            )
            marker_x = cx + marker_trace.centroid.x * scale
            marker_y = cy - marker_trace.centroid.y * scale
        self.canvas.create_oval(marker_x - 12, marker_y - 12, marker_x + 12, marker_y + 12, outline="#f8fafc", width=2)
        self.canvas.create_text(marker_x, marker_y, text="A", fill="#f8fafc", font=("Segoe UI", 13, "bold"))
        self.canvas.create_text(cx, top + height - 4, text="↑ arriba en pantalla" if not retinal else "↓ orientación óptica retinal", fill="#cbd5e1", anchor="s", font=("Segoe UI", 7))

    def draw(self) -> None:
        self.canvas.delete("all")
        width = max(100, self.canvas.winfo_width())
        height = max(100, self.canvas.winfo_height())
        pose = self._pose()
        optics = self._selected_model()
        self.canvas.create_text(20, 10, text="VIZZ 044 · FORMACIÓN DE IMAGEN EN UN OJO REDUCIDO", fill="#e2e8f0", anchor="nw", font=("Segoe UI", 12, "bold"))
        self.canvas.create_text(20, 34, text="La pantalla emite luz; la pupila selecciona un cono; la lente cambia su dirección; la retina recibe la proyección.", fill="#94a3b8", anchor="nw", font=("Segoe UI", 8))
        top = 58.0
        side_width = (width - 36.0) / 2.0
        side_height = min(285.0, height * 0.36)
        self._draw_meridian((12.0, top, side_width, side_height), optics, pose, "horizontal")
        self._draw_meridian((24.0 + side_width, top, side_width, side_height), optics, pose, "vertical")
        bottom = top + side_height + 16.0
        front_width = (width - 36.0) / 2.0
        front_height = max(200.0, height - bottom - 22.0)
        self._draw_front_plane((12.0, bottom, front_width, front_height), optics, pose, False)
        self._draw_front_plane((24.0 + front_width, bottom, front_width, front_height), optics, pose, True)

        sample = trace_screen_point(optics, screen_point(pose, 0.58, 0.58), self.pupil_radius.get())
        fx_state = focus_state(sample.focus_x, optics.retina)
        fy_state = focus_state(sample.focus_y, optics.retina)
        self.readout.set(
            f"modelo: {optics.name}\n"
            f"f_x/f_y: {optics.focal_x * 1000:.2f} / {optics.focal_y * 1000:.2f} mm\n"
            f"retina: {optics.retina * 1000:.2f} mm\n"
            f"foco X/Y: {sample.focus_x * 1000:.2f} / {sample.focus_y * 1000:.2f} mm\n"
            f"estado X/Y: {fx_state} / {fy_state}\n"
            f"desenfoque muestra: {sample.blur_rms * 1000:.3f} mm\n"
            f"pupila: {self.pupil_radius.get() * 1000:.2f} mm\n"
            f"pantalla: ({pose.x:+.3f}, {pose.y:+.3f}, {pose.z:.3f}) m"
        )
        self.canvas.create_text(20, height - 8, text="Modelo reducido: córnea + cristalino equivalentes. No es una receta ni una medición clínica.", fill="#64748b", anchor="sw", font=("Segoe UI", 8))


def main() -> None:
    root = tk.Tk()
    EyeCameraSimulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
