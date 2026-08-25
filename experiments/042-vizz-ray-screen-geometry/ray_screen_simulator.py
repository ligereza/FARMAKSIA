"""Interactive optical geometry sketch for VIZZ.

This is an educational, deterministic ray sketch.  It renders one shared
screen and three optical models (myopia, hyperopia and astigmatism).  Moving
the screen recomputes the ray bundle for every model; it does not use the
camera, a gaze mapper or any medical inference.

The geometry is intentionally small and explicit so it can later be replaced
by a calibrated eye model without changing the interaction contract.
"""

from __future__ import annotations

import math
import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk
from typing import Iterable


@dataclass(frozen=True)
class Point3:
    x: float
    y: float
    z: float

    def __add__(self, other: "Point3") -> "Point3":
        return Point3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: "Point3") -> "Point3":
        return Point3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> "Point3":
        return Point3(self.x * scalar, self.y * scalar, self.z * scalar)


@dataclass(frozen=True)
class ScreenPose:
    """Center and size of a flat screen in metres in the sketch world."""

    x: float = 0.0
    y: float = 0.0
    z: float = 0.72
    width: float = 0.72
    height: float = 0.42


@dataclass(frozen=True)
class EyeModel:
    """Thin-lens approximation for one conceptual optical model.

    ``retina`` is the distance from the lens to the retina.  ``focal_x`` and
    ``focal_y`` allow astigmatism to be shown as two meridians.  Values are
    illustrative, not a prescription and not a physiological measurement.
    """

    name: str
    focal_x: float
    focal_y: float
    retina: float
    color: str
    description: str


EYE_MODELS: tuple[EyeModel, ...] = (
    EyeModel(
        "Miopía",
        focal_x=0.0154,
        focal_y=0.0154,
        retina=0.0170,
        color="#ff6b6b",
        description="el foco cae antes de la retina",
    ),
    EyeModel(
        "Hipermetropía",
        focal_x=0.0186,
        focal_y=0.0186,
        retina=0.0170,
        color="#ffd166",
        description="el foco queda detrás de la retina",
    ),
    EyeModel(
        "Astigmatismo",
        focal_x=0.0154,
        focal_y=0.0186,
        retina=0.0170,
        color="#c77dff",
        description="los meridianos enfocan a distancias distintas",
    ),
)


@dataclass(frozen=True)
class RayTrace:
    source: Point3
    lens: Point3
    focus_x: Point3
    focus_y: Point3
    retina_x: Point3
    retina_y: Point3
    object_distance: float


SCREEN_SAMPLES: tuple[tuple[float, float], ...] = (
    (-0.68, -0.30),
    (0.0, 0.0),
    (0.68, 0.30),
)


def screen_point(pose: ScreenPose, u: float, v: float) -> Point3:
    """Return a point on the shared screen using normalized coordinates."""

    return Point3(
        pose.x + u * pose.width / 2.0,
        pose.y + v * pose.height / 2.0,
        pose.z,
    )


def eye_position(index: int) -> Point3:
    """Place three conceptual optical models around the common optical axis."""

    return Point3((-0.26, 0.0, 0.26)[index], 0.0, 0.0)


def _focus_point(
    eye: Point3,
    lens: Point3,
    source: Point3,
    focal_length: float,
    object_distance: float,
    axis: str,
) -> Point3:
    image_distance = focal_length * object_distance / (object_distance - focal_length)
    if axis == "x":
        lateral = eye.x - (image_distance / object_distance) * (source.x - eye.x)
        return Point3(lateral, eye.y, lens.z - image_distance)
    lateral = eye.y - (image_distance / object_distance) * (source.y - eye.y)
    return Point3(eye.x, lateral, lens.z - image_distance)


def _ray_at_retina(lens: Point3, focus: Point3, retina_distance: float) -> Point3:
    """Continue a refracted ray until it meets the fixed retinal plane."""

    focus_distance = lens.z - focus.z
    if abs(focus_distance) < 1e-12:
        return Point3(lens.x, lens.y, lens.z - retina_distance)
    t = retina_distance / focus_distance
    return lens + (focus - lens) * t


def trace_eye(model: EyeModel, eye: Point3, pose: ScreenPose, uv: tuple[float, float]) -> RayTrace:
    """Trace one screen sample through a thin lens in two meridians."""

    source = screen_point(pose, *uv)
    lens = Point3(eye.x, eye.y, 0.04)
    object_distance = source.z - lens.z
    if object_distance <= max(model.focal_x, model.focal_y):
        raise ValueError("screen must remain beyond the focal length")
    focus_x = _focus_point(eye, lens, source, model.focal_x, object_distance, "x")
    focus_y = _focus_point(eye, lens, source, model.focal_y, object_distance, "y")
    retina_x = _ray_at_retina(lens, focus_x, model.retina)
    retina_y = _ray_at_retina(lens, focus_y, model.retina)
    return RayTrace(source, lens, focus_x, focus_y, retina_x, retina_y, object_distance)


def focus_state(model: EyeModel, trace: RayTrace) -> str:
    """Classify focus relative to the retina for the status panel."""

    fx = trace.lens.z - trace.focus_x.z
    fy = trace.lens.z - trace.focus_y.z
    if abs(fx - fy) > 1e-6:
        return "dos focos"
    if fx < model.retina - 1e-6:
        return "antes de retina"
    if fx > model.retina + 1e-6:
        return "detrás de retina"
    return "sobre retina"


def classify_screen_motion(before: ScreenPose, after: ScreenPose) -> tuple[float, float, float]:
    """Return the explicit screen displacement used by the contract test."""

    return after.x - before.x, after.y - before.y, after.z - before.z


class RayScreenSimulator:
    """Tk canvas renderer with keyboard and slider control."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("VIZZ 042 · Ojos, pantalla y trazos de luz")
        self.root.geometry("1280x800")
        self.root.minsize(1060, 680)
        self.show_rays = True
        self.show_focus = True
        self.screen_x = tk.DoubleVar(value=0.0)
        self.screen_y = tk.DoubleVar(value=0.0)
        self.screen_z = tk.DoubleVar(value=0.72)
        self.status = tk.StringVar(value="La pantalla comparte sus rayos con los tres modelos ópticos.")
        self.readout = tk.StringVar()

        self.canvas = tk.Canvas(root, background="#09111f", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.panel = tk.Frame(root, width=295, background="#111827")
        self.panel.pack(side=tk.RIGHT, fill=tk.Y)
        self.panel.pack_propagate(False)
        self._build_panel()

        root.bind("<Left>", lambda _event: self._nudge("x", -0.01))
        root.bind("<Right>", lambda _event: self._nudge("x", 0.01))
        root.bind("<Up>", lambda _event: self._nudge("y", 0.01))
        root.bind("<Down>", lambda _event: self._nudge("y", -0.01))
        root.bind("<Prior>", lambda _event: self._nudge("z", -0.02))
        root.bind("<Next>", lambda _event: self._nudge("z", 0.02))
        root.bind("<KeyPress-r>", lambda _event: self._reset())
        root.bind("<KeyPress-space>", lambda _event: self._toggle_rays())
        root.bind("<KeyPress-f>", lambda _event: self._toggle_focus())
        root.bind("<Configure>", lambda _event: self.draw())
        self.draw()

    def _build_panel(self) -> None:
        title = tk.Label(
            self.panel,
            text="VIZZ 042\nTRAZADO ÓPTICO",
            font=("Segoe UI", 16, "bold"),
            foreground="#f9fafb",
            background="#111827",
            justify=tk.LEFT,
            anchor="w",
        )
        title.pack(fill=tk.X, padx=18, pady=(20, 8))
        tk.Label(
            self.panel,
            text="Una pantalla · tres modelos de ojo\nLa retina recibe una imagen invertida;\nel cerebro reconstruye la orientación.",
            font=("Segoe UI", 9),
            foreground="#cbd5e1",
            background="#111827",
            justify=tk.LEFT,
            anchor="w",
        ).pack(fill=tk.X, padx=18, pady=(0, 14))

        self._add_scale("Pantalla izquierda ↔ derecha", self.screen_x, -0.35, 0.35, 0.01)
        self._add_scale("Pantalla abajo ↔ arriba", self.screen_y, -0.28, 0.28, 0.01)
        self._add_scale("Distancia pantalla ↔ ojos", self.screen_z, 0.38, 1.25, 0.01)

        ttk.Separator(self.panel).pack(fill=tk.X, padx=18, pady=12)
        tk.Label(
            self.panel,
            textvariable=self.readout,
            font=("Consolas", 9),
            foreground="#93c5fd",
            background="#111827",
            justify=tk.LEFT,
            anchor="w",
        ).pack(fill=tk.X, padx=18, pady=(0, 12))

        for label, command in (
            ("Restablecer (R)", self._reset),
            ("Mostrar/ocultar rayos (Espacio)", self._toggle_rays),
            ("Mostrar/ocultar focos (F)", self._toggle_focus),
        ):
            tk.Button(
                self.panel,
                text=label,
                command=command,
                relief=tk.FLAT,
                background="#1f2937",
                foreground="#e5e7eb",
                activebackground="#334155",
                activeforeground="#ffffff",
                padx=8,
                pady=6,
            ).pack(fill=tk.X, padx=18, pady=3)

        tk.Label(
            self.panel,
            textvariable=self.status,
            font=("Segoe UI", 9),
            foreground="#a7f3d0",
            background="#111827",
            justify=tk.LEFT,
            wraplength=255,
            anchor="w",
        ).pack(fill=tk.X, padx=18, pady=(18, 8))
        tk.Label(
            self.panel,
            text="Teclas: ← → ↑ ↓ mueven la pantalla\nPageUp/PageDown cambia distancia\nR reinicia · Espacio rayos · F focos",
            font=("Segoe UI", 8),
            foreground="#94a3b8",
            background="#111827",
            justify=tk.LEFT,
            anchor="w",
        ).pack(fill=tk.X, padx=18, pady=(0, 12))

    def _add_scale(
        self,
        label: str,
        variable: tk.DoubleVar,
        minimum: float,
        maximum: float,
        resolution: float,
    ) -> None:
        tk.Label(
            self.panel,
            text=label,
            font=("Segoe UI", 9),
            foreground="#e5e7eb",
            background="#111827",
            anchor="w",
        ).pack(fill=tk.X, padx=18, pady=(5, 0))
        tk.Scale(
            self.panel,
            variable=variable,
            from_=minimum,
            to=maximum,
            resolution=resolution,
            orient=tk.HORIZONTAL,
            showvalue=False,
            command=lambda _value: self.draw(),
            background="#111827",
            foreground="#cbd5e1",
            troughcolor="#334155",
            highlightthickness=0,
            activebackground="#60a5fa",
        ).pack(fill=tk.X, padx=14, pady=(0, 4))

    def _nudge(self, axis: str, delta: float) -> None:
        variable = {"x": self.screen_x, "y": self.screen_y, "z": self.screen_z}[axis]
        value = variable.get() + delta
        limits = {"x": (-0.35, 0.35), "y": (-0.28, 0.28), "z": (0.38, 1.25)}[axis]
        variable.set(max(limits[0], min(limits[1], value)))
        self.draw()

    def _reset(self) -> None:
        self.screen_x.set(0.0)
        self.screen_y.set(0.0)
        self.screen_z.set(0.72)
        self.status.set("Pantalla centrada: todos los trazos se recalcularon.")
        self.draw()

    def _toggle_rays(self) -> None:
        self.show_rays = not self.show_rays
        self.status.set("Rayos visibles." if self.show_rays else "Rayos ocultos; la geometría sigue activa.")
        self.draw()

    def _toggle_focus(self) -> None:
        self.show_focus = not self.show_focus
        self.status.set("Puntos de foco visibles." if self.show_focus else "Puntos de foco ocultos.")
        self.draw()

    def _screen_pose(self) -> ScreenPose:
        return ScreenPose(self.screen_x.get(), self.screen_y.get(), self.screen_z.get())

    def _project(self, point: Point3, width: float, height: float) -> tuple[float, float]:
        camera_z = -1.18
        focal = 900.0
        depth = max(0.12, point.z - camera_z)
        return (
            width * 0.48 + focal * point.x / depth,
            height * 0.51 - focal * point.y / depth,
        )

    def _line3d(self, a: Point3, b: Point3, **kwargs: object) -> None:
        width = max(100, self.canvas.winfo_width())
        height = max(100, self.canvas.winfo_height())
        ax, ay = self._project(a, width, height)
        bx, by = self._project(b, width, height)
        self.canvas.create_line(ax, ay, bx, by, **kwargs)

    def _dot3d(self, point: Point3, radius: float, fill: str, outline: str = "") -> None:
        width = max(100, self.canvas.winfo_width())
        height = max(100, self.canvas.winfo_height())
        x, y = self._project(point, width, height)
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=fill, outline=outline)

    def _text3d(self, point: Point3, text: str, **kwargs: object) -> None:
        width = max(100, self.canvas.winfo_width())
        height = max(100, self.canvas.winfo_height())
        x, y = self._project(point, width, height)
        self.canvas.create_text(x, y, text=text, **kwargs)

    def _draw_screen(self, pose: ScreenPose) -> None:
        width = max(100, self.canvas.winfo_width())
        height = max(100, self.canvas.winfo_height())
        corners = [
            screen_point(pose, -1, 1),
            screen_point(pose, 1, 1),
            screen_point(pose, 1, -1),
            screen_point(pose, -1, -1),
        ]
        projected = [self._project(point, width, height) for point in corners]
        flattened = [value for pair in projected for value in pair]
        self.canvas.create_polygon(*flattened, fill="#123052", outline="#93c5fd", width=3)

        for u in (-0.5, 0.0, 0.5):
            self._line3d(screen_point(pose, u, -1), screen_point(pose, u, 1), fill="#28547a", width=1)
        for v in (-0.5, 0.0, 0.5):
            self._line3d(screen_point(pose, -1, v), screen_point(pose, 1, v), fill="#28547a", width=1)
        for uv in SCREEN_SAMPLES:
            self._dot3d(screen_point(pose, *uv), 5, "#f8fafc", "#60a5fa")
        self._text3d(
            Point3(pose.x, pose.y + pose.height / 2 + 0.055, pose.z),
            "PANTALLA COMPARTIDA",
            fill="#bfdbfe",
            font=("Segoe UI", 11, "bold"),
        )
        self._text3d(
            screen_point(pose, -0.88, 0.65),
            "↑ escena upright",
            fill="#f8fafc",
            font=("Segoe UI", 9),
        )

    def _draw_eye(self, index: int, model: EyeModel, pose: ScreenPose) -> list[RayTrace]:
        eye = eye_position(index)
        traces = [trace_eye(model, eye, pose, uv) for uv in SCREEN_SAMPLES]
        width = max(100, self.canvas.winfo_width())
        height = max(100, self.canvas.winfo_height())
        ex, ey = self._project(eye, width, height)
        eye_radius = 34
        self.canvas.create_oval(
            ex - eye_radius,
            ey - eye_radius * 0.63,
            ex + eye_radius,
            ey + eye_radius * 0.63,
            outline=model.color,
            width=2,
        )
        self._dot3d(eye, 5, model.color)
        self._dot3d(traces[1].lens, 4, "#ffffff")

        retina = Point3(eye.x, eye.y, traces[1].lens.z - model.retina)
        self._line3d(
            Point3(eye.x, eye.y - 0.032, retina.z),
            Point3(eye.x, eye.y + 0.032, retina.z),
            fill=model.color,
            width=2,
        )

        for trace in traces:
            if self.show_rays:
                self._line3d(trace.source, trace.lens, fill="#7dd3fc", width=1, dash=(3, 3))
                self._line3d(trace.lens, trace.retina_x, fill=model.color, width=1)
                if abs(trace.retina_y.x - trace.retina_x.x) > 1e-6 or abs(trace.retina_y.y - trace.retina_x.y) > 1e-6:
                    self._line3d(trace.lens, trace.retina_y, fill="#f0abfc", width=1)
            if self.show_focus:
                self._dot3d(trace.focus_x, 4, model.color, "#f8fafc")
                if abs(trace.focus_y.z - trace.focus_x.z) > 1e-6:
                    self._dot3d(trace.focus_y, 4, "#f0abfc", "#f8fafc")

        self._text3d(
            Point3(eye.x, eye.y - 0.075, eye.z),
            model.name,
            fill=model.color,
            font=("Segoe UI", 10, "bold"),
        )
        self._text3d(
            Point3(eye.x, eye.y - 0.115, eye.z),
            f"retina: imagen ↓  |  cerebro: ↑",
            fill="#cbd5e1",
            font=("Segoe UI", 8),
        )
        if self.show_rays:
            self._text3d(
                Point3(eye.x, eye.y + 0.075, eye.z),
                focus_state(model, traces[1]),
                fill=model.color,
                font=("Segoe UI", 8),
            )
        return traces

    def draw(self) -> None:
        self.canvas.delete("all")
        pose = self._screen_pose()
        width = max(100, self.canvas.winfo_width())
        height = max(100, self.canvas.winfo_height())
        self.canvas.create_text(
            28,
            24,
            text="MODELO CONCEPTUAL · LA PANTALLA SE MUEVE, LOS TRES TRAZOS SE RECALCULAN",
            fill="#e2e8f0",
            anchor="w",
            font=("Segoe UI", 11, "bold"),
        )
        self.canvas.create_text(
            28,
            48,
            text="Los puntos blancos nacen en la pantalla; los colores muestran el foco relativo a cada retina.",
            fill="#94a3b8",
            anchor="w",
            font=("Segoe UI", 9),
        )

        self._draw_screen(pose)
        all_traces: list[RayTrace] = []
        for index, model in enumerate(EYE_MODELS):
            all_traces.extend(self._draw_eye(index, model, pose))

        center_distance = math.sqrt(pose.x * pose.x + pose.y * pose.y + (pose.z - 0.04) ** 2)
        self.readout.set(
            f"pantalla x: {pose.x:+.3f} m\n"
            f"pantalla y: {pose.y:+.3f} m\n"
            f"distancia central: {center_distance:.3f} m\n"
            f"rayos recalculados: {len(all_traces)}\n"
            f"estado: {'VISIBLES' if self.show_rays else 'OCULTOS'}"
        )
        self.canvas.create_text(
            28,
            height - 28,
            text="Esquema educativo: no es una receta ni una medición clínica.",
            fill="#64748b",
            anchor="w",
            font=("Segoe UI", 8),
        )


def main() -> None:
    root = tk.Tk()
    RayScreenSimulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
