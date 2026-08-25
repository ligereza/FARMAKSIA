"""VIZZ 045: a single-eye camera model with an explicit optical scene.

This experiment is intentionally narrower than binocular VIZZ.  It makes the
three things visible in one consistent scene:

    screen object -> finite aperture + lens -> sensor/retina image

The physical model is paraxial and reduced.  The GUI is not a clinical eye
model; it is a visual contract for checking source, ray direction, image
inversion, focal plane and defocus before adding a second eye.
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


@dataclass(frozen=True)
class PupilSample:
    x: float
    y: float


@dataclass(frozen=True)
class OpticalTrace:
    source: Point3
    hits: tuple[Point3, ...]
    centroid: Point3
    blur_rms: float
    focus_x: float
    focus_y: float
    image_center_x: float
    image_center_y: float


DEFAULT_RETINA = 0.017
DEFAULT_DISTANCE = 0.72


def focal_length_for_distance(object_distance: float, retina_distance: float) -> float:
    return 1.0 / (1.0 / object_distance + 1.0 / retina_distance)


NORMAL_FOCAL = focal_length_for_distance(DEFAULT_DISTANCE, DEFAULT_RETINA)
EYE_PRESETS: tuple[EyeOptics, ...] = (
    EyeOptics("Normal reducido", NORMAL_FOCAL, NORMAL_FOCAL, DEFAULT_RETINA, "#60a5fa", "foco sobre el sensor a 72 cm"),
    EyeOptics("Miopía conceptual", 0.01505, 0.01505, DEFAULT_RETINA, "#fb7185", "foco delante del sensor"),
    EyeOptics("Hipermetropía conceptual", 0.01811, 0.01811, DEFAULT_RETINA, "#fbbf24", "foco detrás del sensor"),
    EyeOptics("Astigmatismo conceptual", 0.01505, 0.01811, DEFAULT_RETINA, "#c084fc", "dos planos focales meridionales"),
)


PUPIL_PATTERN: tuple[tuple[float, float], ...] = (
    (0.0, 0.0),
    (-1.0, 0.0),
    (1.0, 0.0),
    (0.0, -1.0),
    (0.0, 1.0),
    (-math.sqrt(0.5), -math.sqrt(0.5)),
    (math.sqrt(0.5), -math.sqrt(0.5)),
    (-math.sqrt(0.5), math.sqrt(0.5)),
    (math.sqrt(0.5), math.sqrt(0.5)),
)
GRID_U: tuple[float, ...] = (-0.75, -0.25, 0.25, 0.75)
GRID_V: tuple[float, ...] = (-0.70, -0.23, 0.23, 0.70)
MARKER_U = -0.55
MARKER_V = 0.55


def pupil_samples(radius: float) -> tuple[PupilSample, ...]:
    return tuple(PupilSample(radius * x, radius * y) for x, y in PUPIL_PATTERN)


def screen_point(pose: ScreenPose, u: float, v: float) -> Point3:
    return Point3(pose.x + u * pose.width / 2.0, pose.y + v * pose.height / 2.0, pose.z)


def image_distance(focal_length: float, object_distance: float) -> float:
    if focal_length <= 0 or object_distance <= focal_length:
        raise ValueError("object must be farther than focal length")
    return focal_length * object_distance / (object_distance - focal_length)


def trace_point(optics: EyeOptics, source: Point3, pupil_radius: float) -> OpticalTrace:
    """Trace a luminous screen point through a finite pupil and lens."""

    object_distance = source.z
    if object_distance <= max(optics.focal_x, optics.focal_y):
        raise ValueError("screen is inside the focal distance")
    hits: list[Point3] = []
    for aperture in pupil_samples(pupil_radius):
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
    centroid_x = sum(point.x for point in hits) / len(hits)
    centroid_y = sum(point.y for point in hits) / len(hits)
    blur_rms = math.sqrt(
        sum((point.x - centroid_x) ** 2 + (point.y - centroid_y) ** 2 for point in hits) / len(hits)
    )
    return OpticalTrace(
        source=source,
        hits=tuple(hits),
        centroid=Point3(centroid_x, centroid_y, -optics.retina),
        blur_rms=blur_rms,
        focus_x=image_distance(optics.focal_x, object_distance),
        focus_y=image_distance(optics.focal_y, object_distance),
        image_center_x=-optics.retina * source.x / object_distance,
        image_center_y=-optics.retina * source.y / object_distance,
    )


def focus_state(focus_distance: float, retina_distance: float) -> str:
    if focus_distance < retina_distance - 1e-6:
        return "antes del sensor"
    if focus_distance > retina_distance + 1e-6:
        return "detrás del sensor"
    return "sobre el sensor"


def retinal_grid(optics: EyeOptics, pose: ScreenPose, pupil_radius: float) -> tuple[OpticalTrace, ...]:
    return tuple(
        trace_point(optics, screen_point(pose, u, v), pupil_radius)
        for v in GRID_V
        for u in GRID_U
    )


class SingleEyeCamera:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("VIZZ 045 · cámara óptica: foco e imagen retinal")
        self.root.geometry("1420x920")
        self.root.minsize(1180, 800)
        self.canvas = tk.Canvas(root, background="#07111f", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.panel = tk.Frame(root, width=300, background="#111827")
        self.panel.pack(side=tk.RIGHT, fill=tk.Y)
        self.panel.pack_propagate(False)

        self.screen_x = tk.DoubleVar(value=0.0)
        self.screen_y = tk.DoubleVar(value=0.0)
        self.screen_z = tk.DoubleVar(value=DEFAULT_DISTANCE)
        self.pupil_radius = tk.DoubleVar(value=0.0025)
        self.selected_u = tk.DoubleVar(value=MARKER_U)
        self.selected_v = tk.DoubleVar(value=MARKER_V)
        self.model_name = tk.StringVar(value=EYE_PRESETS[0].name)
        self.show_rays = tk.BooleanVar(value=True)
        self.readout = tk.StringVar()
        self.status = tk.StringVar(value="Escena óptica: pantalla → cámara → sensor/retina.")
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
            text="VIZZ 045\nCÁMARA · FOCO · RETINA",
            font=("Segoe UI", 15, "bold"),
            foreground="#f9fafb",
            background="#111827",
            justify=tk.LEFT,
            anchor="w",
        ).pack(fill=tk.X, padx=18, pady=(20, 8))
        tk.Label(
            self.panel,
            text="Una escena única y legible.\nLa pantalla es la fuente; la cámara\nforma la imagen en el sensor.",
            font=("Segoe UI", 9),
            foreground="#cbd5e1",
            background="#111827",
            justify=tk.LEFT,
            anchor="w",
        ).pack(fill=tk.X, padx=18, pady=(0, 14))
        tk.Label(self.panel, text="Modelo óptico", foreground="#e5e7eb", background="#111827", anchor="w").pack(fill=tk.X, padx=18)
        model_box = ttk.Combobox(self.panel, textvariable=self.model_name, values=[item.name for item in EYE_PRESETS], state="readonly")
        model_box.pack(fill=tk.X, padx=18, pady=(2, 8))
        model_box.bind("<<ComboboxSelected>>", lambda _event: self.draw())
        self._add_scale("Pantalla izquierda ↔ derecha", self.screen_x, -0.25, 0.25, 0.01)
        self._add_scale("Pantalla abajo ↔ arriba", self.screen_y, -0.18, 0.18, 0.01)
        self._add_scale("Distancia pantalla ↔ lente", self.screen_z, 0.38, 1.20, 0.01)
        self._add_scale("Radio de pupila", self.pupil_radius, 0.0012, 0.0040, 0.0001)
        self._add_scale("Punto fuente X", self.selected_u, -0.85, 0.85, 0.01)
        self._add_scale("Punto fuente Y", self.selected_v, -0.85, 0.85, 0.01)
        ttk.Separator(self.panel).pack(fill=tk.X, padx=18, pady=12)
        tk.Label(self.panel, textvariable=self.readout, font=("Consolas", 8), foreground="#93c5fd", background="#111827", justify=tk.LEFT, anchor="w").pack(fill=tk.X, padx=18, pady=(0, 12))
        for label, command in (("Restablecer (R)", self._reset), ("Mostrar/ocultar rayos (Espacio)", self._toggle_rays)):
            tk.Button(self.panel, text=label, command=command, relief=tk.FLAT, background="#1f2937", foreground="#e5e7eb", activebackground="#334155", activeforeground="#ffffff", padx=8, pady=6).pack(fill=tk.X, padx=18, pady=3)
        tk.Label(self.panel, textvariable=self.status, font=("Segoe UI", 9), foreground="#a7f3d0", background="#111827", justify=tk.LEFT, wraplength=260, anchor="w").pack(fill=tk.X, padx=18, pady=(18, 8))
        tk.Label(self.panel, text="Teclas:\n← → ↑ ↓ mover pantalla\nPageUp/PageDown distancia\nR reinicia · Espacio rayos", font=("Segoe UI", 8), foreground="#94a3b8", background="#111827", justify=tk.LEFT, anchor="w").pack(fill=tk.X, padx=18, pady=(0, 12))

    def _add_scale(self, label: str, variable: tk.DoubleVar, minimum: float, maximum: float, resolution: float) -> None:
        tk.Label(self.panel, text=label, font=("Segoe UI", 9), foreground="#e5e7eb", background="#111827", anchor="w").pack(fill=tk.X, padx=18, pady=(4, 0))
        tk.Scale(self.panel, variable=variable, from_=minimum, to=maximum, resolution=resolution, orient=tk.HORIZONTAL, showvalue=False, command=lambda _value: self.draw(), background="#111827", foreground="#cbd5e1", troughcolor="#334155", highlightthickness=0, activebackground="#60a5fa").pack(fill=tk.X, padx=14, pady=(0, 4))

    def _selected_optics(self) -> EyeOptics:
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
        self.selected_u.set(MARKER_U)
        self.selected_v.set(MARKER_V)
        self.model_name.set(EYE_PRESETS[0].name)
        self.status.set("La marca A está arriba-izquierda en pantalla y abajo-derecha en retina.")
        self.draw()

    def _toggle_rays(self) -> None:
        self.show_rays.set(not self.show_rays.get())
        self.status.set("Rayos visibles." if self.show_rays.get() else "Rayos ocultos; la geometría sigue calculándose.")
        self.draw()

    def _optical_x(self, z: float, bounds: tuple[float, float, float, float], screen_distance: float, retina_distance: float) -> float:
        left, _top, width, _height = bounds
        screen_x = left + width * 0.09
        lens_x = left + width * 0.48
        retina_x = left + width * 0.83
        if z >= 0:
            fraction = min(1.0, max(0.0, z / max(screen_distance, 1e-9)))
            return lens_x + fraction * (screen_x - lens_x)
        return lens_x + (-z / retina_distance) * (retina_x - lens_x)

    def _optical_y(self, transverse: float, bounds: tuple[float, float, float, float]) -> float:
        _left, top, _width, height = bounds
        return top + height * 0.56 - transverse * min(190.0, (height - 72.0) / 0.25)

    def _draw_camera_cut(self, bounds: tuple[float, float, float, float], optics: EyeOptics, pose: ScreenPose, meridian: str) -> OpticalTrace:
        left, top, width, height = bounds
        source = screen_point(pose, self.selected_u.get(), self.selected_v.get())
        object_height = source.x if meridian == "horizontal" else source.y
        focal = optics.focal_x if meridian == "horizontal" else optics.focal_y
        trace = trace_point(optics, source, self.pupil_radius.get())
        axis_y = self._optical_y(0.0, bounds)
        screen_x = self._optical_x(pose.z, bounds, pose.z, optics.retina)
        lens_x = self._optical_x(0.0, bounds, pose.z, optics.retina)
        sensor_x = self._optical_x(-optics.retina, bounds, pose.z, optics.retina)
        camera_top = top + 48
        camera_bottom = top + height - 28
        self.canvas.create_rectangle(left, top, left + width, top + height, outline="#1e3a5f")
        self.canvas.create_text(left + 8, top + 8, text=f"{meridian.upper()} · RAYOS DE LUZ", fill="#e2e8f0", anchor="nw", font=("Segoe UI", 9, "bold"))
        self.canvas.create_line(left + 10, axis_y, left + width - 10, axis_y, fill="#334155", dash=(2, 4))
        self.canvas.create_rectangle(lens_x - 20, camera_top, sensor_x + 22, camera_bottom, outline="#64748b", width=2)
        self.canvas.create_text((lens_x + sensor_x) / 2, camera_top + 10, text="CÁMARA / OJO REDUCIDO", fill="#cbd5e1", font=("Segoe UI", 7, "bold"))
        self.canvas.create_line(screen_x, top + 36, screen_x, top + height - 18, fill="#60a5fa", width=2)
        self.canvas.create_text(screen_x, top + height - 3, text="PANTALLA · fuente", fill="#93c5fd", anchor="s", font=("Segoe UI", 7))
        self.canvas.create_oval(lens_x - 8, axis_y - 28, lens_x + 8, axis_y + 28, outline="#f8fafc", width=2)
        self.canvas.create_line(lens_x - 13, axis_y - 33, lens_x - 13, axis_y + 33, fill="#fbbf24", width=2)
        self.canvas.create_line(lens_x + 13, axis_y - 33, lens_x + 13, axis_y + 33, fill="#fbbf24", width=2)
        self.canvas.create_text(lens_x, camera_bottom - 2, text="APERTURA + LENTE", fill="#e2e8f0", anchor="s", font=("Segoe UI", 7))
        self.canvas.create_line(sensor_x, camera_top + 16, sensor_x, camera_bottom - 12, fill="#f87171", width=3)
        self.canvas.create_text(sensor_x, camera_bottom - 2, text="SENSOR / RETINA", fill="#fca5a5", anchor="s", font=("Segoe UI", 7))

        source_y = self._optical_y(object_height, bounds)
        self.canvas.create_oval(screen_x - 6, source_y - 6, screen_x + 6, source_y + 6, fill="#ffffff", outline="#60a5fa", width=2)
        self.canvas.create_text(screen_x, source_y - 12, text="S", fill="#ffffff", font=("Segoe UI", 8, "bold"))
        focus_distance = trace.focus_x if meridian == "horizontal" else trace.focus_y
        focus_height = -(focus_distance / pose.z) * object_height
        focus_x = self._optical_x(-focus_distance, bounds, pose.z, optics.retina)
        focus_y = self._optical_y(focus_height, bounds)
        if self.show_rays.get():
            for aperture in pupil_samples(self.pupil_radius.get()):
                aperture_height = aperture.x if meridian == "horizontal" else aperture.y
                incoming_slope = (aperture_height - object_height) / pose.z
                outgoing_slope = incoming_slope - aperture_height / focal
                retina_height = aperture_height + optics.retina * outgoing_slope
                aperture_y = self._optical_y(aperture_height, bounds)
                retina_y = self._optical_y(retina_height, bounds)
                self.canvas.create_line(screen_x, source_y, lens_x, aperture_y, fill="#7dd3fc", width=1, arrow=tk.LAST)
                self.canvas.create_line(lens_x, aperture_y, sensor_x, retina_y, fill=optics.color, width=2, arrow=tk.LAST)
                if focus_distance > optics.retina + 1e-9:
                    focus_ray_y = self._optical_y(aperture_height + focus_distance * outgoing_slope, bounds)
                    self.canvas.create_line(sensor_x, retina_y, focus_x, focus_ray_y, fill=optics.color, width=1, dash=(4, 3))
        self.canvas.create_line(focus_x, camera_top + 18, focus_x, camera_bottom - 10, fill="#f59e0b", width=2, dash=(5, 3))
        self.canvas.create_oval(focus_x - 7, focus_y - 7, focus_x + 7, focus_y + 7, fill=optics.color, outline="#ffffff", width=2)
        self.canvas.create_line(focus_x - 12, focus_y, focus_x + 12, focus_y, fill="#f59e0b", width=2)
        self.canvas.create_line(focus_x, focus_y - 12, focus_x, focus_y + 12, fill="#f59e0b", width=2)
        self.canvas.create_text(focus_x, camera_top + 20, text=f"PUNTO FOCAL\nv={focus_distance * 1000:.2f} mm", fill="#fbbf24", anchor="n", font=("Consolas", 7, "bold"))
        self.canvas.create_text(left + width - 8, top + 8, text=focus_state(focus_distance, optics.retina), fill="#fbbf24", anchor="ne", font=("Segoe UI", 8, "bold"))
        return trace

    def _draw_front_plane(self, bounds: tuple[float, float, float, float], optics: EyeOptics, pose: ScreenPose, retinal: bool) -> None:
        left, top, width, height = bounds
        side = min(width - 34, height - 48)
        cx = left + width * 0.5
        cy = top + height * 0.57
        scale = side / pose.width if not retinal else side / pose.width * pose.z / optics.retina
        self.canvas.create_rectangle(cx - side / 2, cy - side * pose.height / pose.width / 2, cx + side / 2, cy + side * pose.height / pose.width / 2, outline="#f87171" if retinal else "#60a5fa", width=2)
        self.canvas.create_text(left + 8, top + 8, text="RETINA · IMAGEN ÓPTICA INVERTIDA" if retinal else "PANTALLA · OBJETO ORIGINAL", fill="#fca5a5" if retinal else "#bfdbfe", anchor="nw", font=("Segoe UI", 9, "bold"))
        for v in GRID_V:
            y = cy - v * side * pose.height / pose.width / 2
            self.canvas.create_line(cx - side / 2, y, cx + side / 2, y, fill="#28547a", width=1)
        for u in GRID_U:
            x = cx + u * side / 2
            self.canvas.create_line(x, cy - side * pose.height / pose.width / 2, x, cy + side * pose.height / pose.width / 2, fill="#28547a", width=1)
        if retinal:
            for trace in retinal_grid(optics, pose, self.pupil_radius.get()):
                for hit in trace.hits:
                    self.canvas.create_oval(cx + hit.x * scale - 1.5, cy - hit.y * scale - 1.5, cx + hit.x * scale + 1.5, cy - hit.y * scale + 1.5, fill=optics.color, outline="")
            marker = trace_point(optics, screen_point(pose, MARKER_U, MARKER_V), self.pupil_radius.get()).centroid
            marker_x = cx + marker.x * scale
            marker_y = cy - marker.y * scale
            self.canvas.create_text(marker_x, marker_y, text="A", fill="#ffffff", font=("Segoe UI", 16, "bold"))
            self.canvas.create_text(cx, top + height - 5, text="la retina recibe la inversión; el cerebro no se simula", fill="#fca5a5", anchor="s", font=("Segoe UI", 7))
        else:
            marker_x = cx + MARKER_U * side / 2
            marker_y = cy - MARKER_V * side * pose.height / pose.width / 2
            self.canvas.create_text(marker_x, marker_y, text="A", fill="#ffffff", font=("Segoe UI", 16, "bold"))
            self.canvas.create_line(cx, cy + 26, cx, cy - 26, fill="#f8fafc", width=2, arrow=tk.LAST)
            self.canvas.create_text(cx, top + height - 5, text="arriba en la pantalla", fill="#bfdbfe", anchor="s", font=("Segoe UI", 7))

    def draw(self) -> None:
        self.canvas.delete("all")
        width = max(100, self.canvas.winfo_width())
        height = max(100, self.canvas.winfo_height())
        pose = self._pose()
        optics = self._selected_optics()
        self.canvas.create_text(20, 10, text="VIZZ 045 · FORMACIÓN ÓPTICA: OBJETO → LENTE → FOCO → SENSOR", fill="#e2e8f0", anchor="nw", font=("Segoe UI", 12, "bold"))
        self.canvas.create_text(20, 34, text="La flecha de cada rayo apunta desde la pantalla hacia la cámara. La marca A permite ver la inversión retinal.", fill="#94a3b8", anchor="nw", font=("Segoe UI", 8))
        top = 58.0
        cut_width = (width - 36.0) / 2.0
        cut_height = min(300.0, height * 0.38)
        trace_h = self._draw_camera_cut((12.0, top, cut_width, cut_height), optics, pose, "horizontal")
        trace_v = self._draw_camera_cut((24.0 + cut_width, top, cut_width, cut_height), optics, pose, "vertical")
        bottom = top + cut_height + 16.0
        front_width = (width - 36.0) / 2.0
        front_height = max(220.0, height - bottom - 20.0)
        self._draw_front_plane((12.0, bottom, front_width, front_height), optics, pose, False)
        self._draw_front_plane((24.0 + front_width, bottom, front_width, front_height), optics, pose, True)
        self.readout.set(
            f"modelo: {optics.name}\n"
            f"foco H/V: {trace_h.focus_x * 1000:.2f} / {trace_v.focus_y * 1000:.2f} mm\n"
            f"sensor/retina: {optics.retina * 1000:.2f} mm\n"
            f"estado H/V: {focus_state(trace_h.focus_x, optics.retina)} / {focus_state(trace_v.focus_y, optics.retina)}\n"
            f"desenfoque H/V: {trace_h.blur_rms * 1000:.3f} / {trace_v.blur_rms * 1000:.3f} mm\n"
            f"fuente seleccionada: ({self.selected_u.get():+.2f}, {self.selected_v.get():+.2f})\n"
            f"pantalla: ({pose.x:+.3f}, {pose.y:+.3f}, {pose.z:.3f}) m"
        )
        self.canvas.create_text(20, height - 8, text="Modelo paraxial reducido: no es una receta ni una medición clínica.", fill="#64748b", anchor="sw", font=("Segoe UI", 8))


def main() -> None:
    root = tk.Tk()
    SingleEyeCamera(root)
    root.mainloop()


if __name__ == "__main__":
    main()
