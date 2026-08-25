"""Interactive paraxial ray-tracing sketch for VIZZ.

The application has two views of the same model:

* a spatial view with one movable screen and three conceptual eye models;
* a ray diagram showing an actual bundle of paraxial rays for each meridian.

Light travels from the screen to the lens.  At the thin lens, the slope of a
ray changes by ``-height / focal_length``.  The rays are then propagated to a
fixed retinal plane.  The image distance is calculated from the thin-lens
equation, so the diagram can show focus before, on, or behind the retina.

This is an educational optical model, not a clinical eye model.  It does not
use the camera, a gaze mapper, or a human subject.
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
    """Center and dimensions of a flat screen in metres."""

    x: float = 0.0
    y: float = 0.0
    z: float = 0.72
    width: float = 0.72
    height: float = 0.42


@dataclass(frozen=True)
class EyeModel:
    """Conceptual optical power in two meridians.

    ``retina`` is measured from the thin lens toward the back of the eye.
    The focal lengths are illustrative parameters chosen to make the three
    focus cases visible at the default screen distance.  They are not a
    prescription and must not be interpreted as one.
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
        focal_x=0.01505,
        focal_y=0.01505,
        retina=0.01700,
        color="#ff6b6b",
        description="el haz converge antes de la retina",
    ),
    EyeModel(
        "Hipermetropía",
        focal_x=0.01811,
        focal_y=0.01811,
        retina=0.01700,
        color="#ffd166",
        description="el haz convergería detrás de la retina",
    ),
    EyeModel(
        "Astigmatismo",
        focal_x=0.01505,
        focal_y=0.01811,
        retina=0.01700,
        color="#c77dff",
        description="los meridianos tienen focos distintos",
    ),
)


@dataclass(frozen=True)
class ParaxialRay:
    """One ray in a 2D meridian, measured from the optical axis."""

    lens_height: float
    incoming_slope: float
    outgoing_slope: float
    retina_height: float
    focus_height: float


@dataclass(frozen=True)
class ParaxialTrace:
    object_height: float
    object_distance: float
    focal_length: float
    image_distance: float
    focus_height: float
    retina_heights: tuple[float, ...]
    rays: tuple[ParaxialRay, ...]


@dataclass(frozen=True)
class SpatialTrace:
    source: Point3
    eye: Point3
    distance: float


SCREEN_SAMPLES: tuple[tuple[float, float], ...] = ((0.0, 0.0), (-0.58, 0.35), (0.58, -0.35))
LENS_Z = 0.04
APERTURE_RADIUS = 0.003
APERTURE_SAMPLES: tuple[float, ...] = (-APERTURE_RADIUS, 0.0, APERTURE_RADIUS)


def screen_point(pose: ScreenPose, u: float, v: float) -> Point3:
    """Map normalized screen coordinates ``[-1, 1]`` into world metres."""

    return Point3(
        pose.x + u * pose.width / 2.0,
        pose.y + v * pose.height / 2.0,
        pose.z,
    )


def eye_position(index: int) -> Point3:
    """Place the three conceptual optical models in the spatial view."""

    return Point3((-0.26, 0.0, 0.26)[index], 0.0, 0.0)


def thin_lens_image_distance(focal_length: float, object_distance: float) -> float:
    """Return ``v`` from ``1/f = 1/u + 1/v`` for a converging lens."""

    if focal_length <= 0 or object_distance <= focal_length:
        raise ValueError("the object must be farther than the focal length")
    return focal_length * object_distance / (object_distance - focal_length)


def trace_paraxial(
    object_height: float,
    object_distance: float,
    focal_length: float,
    retina_distance: float,
    aperture_samples: tuple[float, ...] = APERTURE_SAMPLES,
) -> ParaxialTrace:
    """Trace a finite aperture bundle through a thin converging lens.

    Coordinate convention: light travels left-to-right in this local diagram.
    The object is at ``x=0``, the lens at ``x=u`` and the retina at ``x=u+r``.
    A ray entering the lens at height ``a`` has incoming slope
    ``(a-h_object)/u``.  The thin lens changes it to
    ``incoming_slope - a/f``.  This is the paraxial form of refraction by a
    thin lens and makes the ray family visibly converge or diverge.
    """

    image_distance = thin_lens_image_distance(focal_length, object_distance)
    focus_height = -(image_distance / object_distance) * object_height
    rays: list[ParaxialRay] = []
    retina_heights: list[float] = []
    for lens_height in aperture_samples:
        incoming_slope = (lens_height - object_height) / object_distance
        outgoing_slope = incoming_slope - lens_height / focal_length
        retina_height = lens_height + retina_distance * outgoing_slope
        focus_at_ray = lens_height + image_distance * outgoing_slope
        rays.append(
            ParaxialRay(
                lens_height=lens_height,
                incoming_slope=incoming_slope,
                outgoing_slope=outgoing_slope,
                retina_height=retina_height,
                focus_height=focus_at_ray,
            )
        )
        retina_heights.append(retina_height)
    return ParaxialTrace(
        object_height=object_height,
        object_distance=object_distance,
        focal_length=focal_length,
        image_distance=image_distance,
        focus_height=focus_height,
        retina_heights=tuple(retina_heights),
        rays=tuple(rays),
    )


def focus_state(image_distance: float, retina_distance: float) -> str:
    if image_distance < retina_distance - 1e-6:
        return "antes de retina"
    if image_distance > retina_distance + 1e-6:
        return "detrás de retina"
    return "sobre retina"


def eye_meridian_trace(
    model: EyeModel,
    eye: Point3,
    pose: ScreenPose,
    meridian: str,
) -> ParaxialTrace:
    """Trace the screen centre in one eye meridian.

    Horizontal movement changes the horizontal meridian height; vertical
    movement changes the vertical meridian height.  The same screen centre is
    used so every eye sees the same physical source while having a different
    transverse offset.
    """

    source = screen_point(pose, 0.0, 0.0)
    object_height = source.x - eye.x if meridian == "horizontal" else source.y - eye.y
    focal_length = model.focal_x if meridian == "horizontal" else model.focal_y
    object_distance = source.z - LENS_Z
    return trace_paraxial(object_height, object_distance, focal_length, model.retina)


def spatial_trace(pose: ScreenPose, eye: Point3, uv: tuple[float, float]) -> SpatialTrace:
    source = screen_point(pose, *uv)
    delta = Point3(source.x - eye.x, source.y - eye.y, source.z - eye.z)
    distance = math.sqrt(delta.x * delta.x + delta.y * delta.y + delta.z * delta.z)
    return SpatialTrace(source, eye, distance)


def classify_screen_motion(before: ScreenPose, after: ScreenPose) -> tuple[float, float, float]:
    return after.x - before.x, after.y - before.y, after.z - before.z


class RayScreenSimulator:
    """Interactive renderer with one shared screen and three eye models."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("VIZZ 042 · luz, foco y retina")
        self.root.geometry("1280x900")
        self.root.minsize(1100, 760)
        self.show_rays = True
        self.show_focus = True
        self.screen_x = tk.DoubleVar(value=0.0)
        self.screen_y = tk.DoubleVar(value=0.0)
        self.screen_z = tk.DoubleVar(value=0.72)
        self.readout = tk.StringVar()
        self.status = tk.StringVar(value="La pantalla emite un haz hacia cada abertura; la lente cambia su dirección.")

        self.canvas = tk.Canvas(root, background="#07111f", highlightthickness=0)
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
        tk.Label(
            self.panel,
            text="VIZZ 042\nLUZ · LENTE · FOCO",
            font=("Segoe UI", 16, "bold"),
            foreground="#f9fafb",
            background="#111827",
            justify=tk.LEFT,
            anchor="w",
        ).pack(fill=tk.X, padx=18, pady=(20, 8))
        tk.Label(
            self.panel,
            text=(
                "La luz sale de la pantalla, atraviesa\n"
                "una abertura finita y se refracta.\n"
                "La retina queda fija detrás de la lente."
            ),
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
            text=(
                "Teclas:\n"
                "← → ↑ ↓ mover pantalla\n"
                "PageUp/PageDown distancia\n"
                "R reinicia · Espacio rayos\n"
                "F focos"
            ),
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
        limits = {"x": (-0.35, 0.35), "y": (-0.28, 0.28), "z": (0.38, 1.25)}[axis]
        variable.set(max(limits[0], min(limits[1], variable.get() + delta)))
        self.draw()

    def _reset(self) -> None:
        self.screen_x.set(0.0)
        self.screen_y.set(0.0)
        self.screen_z.set(0.72)
        self.status.set("Pantalla centrada: los haces vuelven a calcularse.")
        self.draw()

    def _toggle_rays(self) -> None:
        self.show_rays = not self.show_rays
        self.status.set("Rayos visibles." if self.show_rays else "Rayos ocultos; la física sigue calculándose.")
        self.draw()

    def _toggle_focus(self) -> None:
        self.show_focus = not self.show_focus
        self.status.set("Focos visibles." if self.show_focus else "Focos ocultos; la retina sigue dibujada.")
        self.draw()

    def _pose(self) -> ScreenPose:
        return ScreenPose(self.screen_x.get(), self.screen_y.get(), self.screen_z.get())

    def _project(self, point: Point3, viewport: tuple[float, float, float, float]) -> tuple[float, float]:
        left, top, width, height = viewport
        camera_z = -1.18
        focal = 790.0
        depth = max(0.12, point.z - camera_z)
        return (
            left + width * 0.48 + focal * point.x / depth,
            top + height * 0.53 - focal * point.y / depth,
        )

    def _line3d(self, a: Point3, b: Point3, viewport: tuple[float, float, float, float], **kwargs: object) -> None:
        ax, ay = self._project(a, viewport)
        bx, by = self._project(b, viewport)
        self.canvas.create_line(ax, ay, bx, by, **kwargs)

    def _dot3d(
        self,
        point: Point3,
        viewport: tuple[float, float, float, float],
        radius: float,
        fill: str,
        outline: str = "",
    ) -> None:
        x, y = self._project(point, viewport)
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=fill, outline=outline)

    def _text3d(self, point: Point3, viewport: tuple[float, float, float, float], text: str, **kwargs: object) -> None:
        x, y = self._project(point, viewport)
        self.canvas.create_text(x, y, text=text, **kwargs)

    def _draw_spatial_view(self, pose: ScreenPose, viewport: tuple[float, float, float, float]) -> None:
        left, top, width, height = viewport
        self.canvas.create_rectangle(left, top, left + width, top + height, outline="#1e3a5f")
        self.canvas.create_text(
            left + 16,
            top + 14,
            text="VISTA ESPACIAL · una pantalla / tres aperturas",
            fill="#e2e8f0",
            anchor="nw",
            font=("Segoe UI", 10, "bold"),
        )
        corners = [
            screen_point(pose, -1, 1),
            screen_point(pose, 1, 1),
            screen_point(pose, 1, -1),
            screen_point(pose, -1, -1),
        ]
        polygon = [coord for point in corners for coord in self._project(point, viewport)]
        self.canvas.create_polygon(*polygon, fill="#123052", outline="#93c5fd", width=2)
        for u in (-0.5, 0.0, 0.5):
            self._line3d(screen_point(pose, u, -1), screen_point(pose, u, 1), viewport, fill="#28547a", width=1)
        for v in (-0.5, 0.0, 0.5):
            self._line3d(screen_point(pose, -1, v), screen_point(pose, 1, v), viewport, fill="#28547a", width=1)
        self._text3d(
            Point3(pose.x, pose.y + pose.height / 2 + 0.045, pose.z),
            viewport,
            "PANTALLA EMISORA",
            fill="#bfdbfe",
            font=("Segoe UI", 9, "bold"),
        )

        for index, model in enumerate(EYE_MODELS):
            eye = eye_position(index)
            eye_screen = self._project(eye, viewport)
            self.canvas.create_oval(
                eye_screen[0] - 20,
                eye_screen[1] - 13,
                eye_screen[0] + 20,
                eye_screen[1] + 13,
                outline=model.color,
                width=2,
            )
            self._dot3d(eye, viewport, 4, model.color)
            self._text3d(
                Point3(eye.x, eye.y - 0.065, eye.z),
                viewport,
                model.name,
                fill=model.color,
                font=("Segoe UI", 8, "bold"),
            )
            for uv in SCREEN_SAMPLES:
                trace = spatial_trace(pose, eye, uv)
                self._line3d(trace.source, trace.eye, viewport, fill="#4b6680", width=1, dash=(3, 4))
                self._dot3d(trace.source, viewport, 3, "#f8fafc")

        self.canvas.create_text(
            left + 16,
            top + height - 14,
            text="Líneas punteadas: camino espacial hacia cada ojo. Diagramas inferiores: trazado óptico refractado.",
            fill="#94a3b8",
            anchor="sw",
            font=("Segoe UI", 8),
        )

    def _draw_ray_line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        color: str,
        width: int = 1,
        dash: tuple[int, ...] | None = None,
        arrow: str = tk.NONE,
    ) -> None:
        kwargs: dict[str, object] = {"fill": color, "width": width, "arrow": arrow}
        if dash:
            kwargs["dash"] = dash
        self.canvas.create_line(x1, y1, x2, y2, **kwargs)

    def _draw_meridian(
        self,
        bounds: tuple[float, float, float, float],
        model: EyeModel,
        trace: ParaxialTrace,
        label: str,
        color: str,
    ) -> None:
        left, top, width, height = bounds
        axis_y = top + height * 0.57
        object_x = left + 28
        lens_x = left + width * 0.49
        optical_x_scale = 64 / model.retina
        retina_x = lens_x + model.retina * optical_x_scale
        focus_x = lens_x + trace.image_distance * optical_x_scale
        height_scale = 125.0

        self.canvas.create_text(
            left + 8,
            top + 8,
            text=label,
            fill="#cbd5e1",
            anchor="nw",
            font=("Segoe UI", 8, "bold"),
        )
        self.canvas.create_text(
            left + 8,
            top + 25,
            text="luz →",
            fill="#94a3b8",
            anchor="nw",
            font=("Segoe UI", 7),
        )
        self.canvas.create_line(object_x, top + 30, object_x, top + height - 8, fill="#60a5fa", width=2)
        self.canvas.create_line(lens_x, top + 30, lens_x, top + height - 8, fill="#f8fafc", width=2)
        self.canvas.create_oval(lens_x - 7, axis_y - 25, lens_x + 7, axis_y + 25, outline="#f8fafc", width=2)
        self.canvas.create_line(retina_x, top + 30, retina_x, top + height - 8, fill="#f87171", width=2)
        self.canvas.create_text(object_x, top + height - 2, text="pantalla", fill="#93c5fd", anchor="s", font=("Segoe UI", 7))
        self.canvas.create_text(lens_x, top + height - 2, text="lente", fill="#e2e8f0", anchor="s", font=("Segoe UI", 7))
        self.canvas.create_text(retina_x, top + height - 2, text="retina", fill="#fca5a5", anchor="s", font=("Segoe UI", 7))
        self.canvas.create_line(left + 12, axis_y, left + width - 10, axis_y, fill="#334155", dash=(2, 4))

        # An upright source arrow becomes an inverted image on the retina.
        source_y = axis_y - max(-height * 0.28, min(height * 0.28, trace.object_height * height_scale))
        self._draw_ray_line(object_x, axis_y, object_x, source_y, "#f8fafc", width=2, arrow=tk.LAST)

        focus_screen_y = axis_y - trace.focus_height * height_scale
        if self.show_focus:
            self.canvas.create_oval(focus_x - 5, focus_screen_y - 5, focus_x + 5, focus_screen_y + 5, fill=color, outline="#ffffff")
            self.canvas.create_text(
                focus_x,
                top + 27,
                text=f"foco {trace.image_distance * 1000:.1f} mm",
                fill=color,
                anchor="n",
                font=("Consolas", 7),
            )

        for ray in trace.rays:
            lens_y = axis_y - ray.lens_height * height_scale
            retina_y = axis_y - ray.retina_height * height_scale
            focus_ray_y = axis_y - ray.focus_height * height_scale
            # Before the lens: straight propagation from source to aperture.
            self._draw_ray_line(object_x, source_y, lens_x, lens_y, "#7dd3fc", width=1, arrow=tk.LAST)
            # After the lens: changed slope. This is the refracted leg.
            self._draw_ray_line(lens_x, lens_y, retina_x, retina_y, color, width=2)
            # Continue the same post-lens ray to its calculated focus.
            self._draw_ray_line(retina_x, retina_y, focus_x, focus_ray_y, color, width=1, dash=(3, 3))

        state = focus_state(trace.image_distance, model.retina)
        self.canvas.create_text(
            left + width - 8,
            top + 8,
            text=state,
            fill=color,
            anchor="ne",
            font=("Segoe UI", 8, "bold"),
        )

    def _draw_eye_card(self, index: int, pose: ScreenPose, bounds: tuple[float, float, float, float]) -> None:
        left, top, width, height = bounds
        model = EYE_MODELS[index]
        self.canvas.create_rectangle(left, top, left + width, top + height, fill="#0c1b2e", outline=model.color, width=2)
        self.canvas.create_text(
            left + 12,
            top + 10,
            text=f"OJO MODELO {index + 1}: {model.name.upper()}",
            fill=model.color,
            anchor="nw",
            font=("Segoe UI", 10, "bold"),
        )
        self.canvas.create_text(
            left + 12,
            top + 30,
            text="↑ pantalla → haz → ↓ retina → ↑ cerebro",
            fill="#cbd5e1",
            anchor="nw",
            font=("Segoe UI", 7),
        )

        inner_top = top + 52
        sub_height = max(90.0, (height - 62) / 2.0)
        eye = eye_position(index)
        vertical = eye_meridian_trace(model, eye, pose, "vertical")
        horizontal = eye_meridian_trace(model, eye, pose, "horizontal")
        self._draw_meridian((left + 8, inner_top, width - 16, sub_height - 7), model, vertical, "meridiano vertical · pantalla arriba/abajo", "#60a5fa")
        self._draw_meridian((left + 8, inner_top + sub_height, width - 16, sub_height - 7), model, horizontal, "meridiano horizontal · pantalla izquierda/derecha", model.color)

    def draw(self) -> None:
        self.canvas.delete("all")
        width = max(100, self.canvas.winfo_width())
        height = max(100, self.canvas.winfo_height())
        pose = ScreenPose(self.screen_x.get(), self.screen_y.get(), self.screen_z.get())
        scene_height = max(245.0, min(315.0, height * 0.34))
        self.canvas.create_text(
            22,
            10,
            text="MODELO DE LUZ · la pantalla se mueve y el haz se recalcula desde una abertura finita",
            fill="#e2e8f0",
            anchor="nw",
            font=("Segoe UI", 11, "bold"),
        )
        self.canvas.create_text(
            22,
            31,
            text="No es un rayo único: cada punto produce varios rayos; la lente cambia su pendiente y la retina intercepta el haz.",
            fill="#94a3b8",
            anchor="nw",
            font=("Segoe UI", 8),
        )

        spatial_view = (12.0, 52.0, width - 24.0, scene_height)
        self._draw_spatial_view(pose, spatial_view)

        cards_top = 62.0 + scene_height + 14.0
        card_height = max(250.0, height - cards_top - 12.0)
        card_width = (width - 36.0) / 3.0
        for index in range(3):
            self._draw_eye_card(index, pose, (12.0 + index * (card_width + 6.0), cards_top, card_width, card_height))

        center = screen_point(pose, 0.0, 0.0)
        exact_distances = [spatial_trace(pose, eye_position(i), (0.0, 0.0)).distance for i in range(3)]
        states = []
        for model, index in zip(EYE_MODELS, range(3)):
            vertical = eye_meridian_trace(model, eye_position(index), pose, "vertical")
            horizontal = eye_meridian_trace(model, eye_position(index), pose, "horizontal")
            states.append(f"{model.name}: V {focus_state(vertical.image_distance, model.retina)} / H {focus_state(horizontal.image_distance, model.retina)}")
        self.readout.set(
            f"pantalla x: {pose.x:+.3f} m\n"
            f"pantalla y: {pose.y:+.3f} m\n"
            f"distancias exactas a centros: {', '.join(f'{d:.3f}' for d in exact_distances)} m\n"
            f"retina: 17.0 mm · centro: ({center.x:+.3f}, {center.y:+.3f}, {center.z:.3f})\n"
            + "\n".join(states)
        )
        self.canvas.create_text(
            22,
            height - 8,
            text="Esquema educativo: la retina no es una pantalla plana ideal y estos parámetros no diagnostican la vista.",
            fill="#64748b",
            anchor="sw",
            font=("Segoe UI", 8),
        )


def main() -> None:
    root = tk.Tk()
    RayScreenSimulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
