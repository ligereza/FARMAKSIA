"""The only visible VIZZ surface: a fullscreen, one-shot calibration."""

from __future__ import annotations

import time
import tkinter as tk
from collections.abc import Callable

from calibration_capture import CaptureConfig, CaptureResult, StableCapture
from gpu_tracker import GazeSample


CALIBRATION_POINTS: tuple[tuple[float, float], ...] = (
    (0.08, 0.08),
    (0.50, 0.08),
    (0.92, 0.08),
    (0.08, 0.33),
    (0.50, 0.33),
    (0.92, 0.33),
    (0.08, 0.67),
    (0.50, 0.67),
    (0.92, 0.67),
    (0.08, 0.92),
    (0.50, 0.92),
    (0.92, 0.92),
)
CAPTURE_CONFIG = CaptureConfig(
    settle_seconds=0.30,
    window_seconds=0.90,
    min_valid_samples=12,
    min_quality=0.50,
    max_feature_mad=0.08,
    require_pose=True,
)
SAMPLES_PER_POINT = CAPTURE_CONFIG.min_valid_samples
CLICK_TARGET_RADIUS_PX = 100
CALIBRATION_CONDITIONS: tuple[tuple[str, str], ...] = (
    ("with_glasses", "con lentes"),
    ("without_glasses", "sin lentes"),
)


class CalibrationAborted(RuntimeError):
    pass


class CalibrationWindow:
    def __init__(
        self,
        sample_provider: Callable[[], GazeSample | None],
        on_complete: Callable[[list[dict[str, object]], tuple[int, int]], None],
        conditions: tuple[tuple[str, str], ...] = CALIBRATION_CONDITIONS,
    ) -> None:
        if not conditions:
            raise ValueError("at least one calibration condition is required")
        self.sample_provider = sample_provider
        self.on_complete = on_complete
        self.conditions = conditions
        self.root = tk.Tk()
        self.root.title("FARMAKSIA — calibración")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="black")
        self.root.protocol("WM_DELETE_WINDOW", self.abort)
        self.root.bind("<Escape>", lambda _event: self.abort())
        self.canvas = tk.Canvas(self.root, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._on_resize)
        self.width = max(1, self.root.winfo_screenwidth())
        self.height = max(1, self.root.winfo_screenheight())
        self.point_index = 0
        self.condition_index = 0
        self.samples: list[dict[str, object]] = []
        self.capture: StableCapture | None = None
        self.dot_id: int | None = None
        self.status_id: int | None = None
        self.started = False
        self.point_state = "idle"
        self.start_window: int | None = None
        self.condition_window: int | None = None
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self._draw_landing()

    def run(self) -> None:
        self.root.mainloop()

    def abort(self) -> None:
        self.root.destroy()
        raise CalibrationAborted("calibration cancelled")

    def _on_resize(self, _event: tk.Event[tk.Misc]) -> None:
        self.width = max(1, self.canvas.winfo_width())
        self.height = max(1, self.canvas.winfo_height())
        if not self.started and self.start_window is not None:
            self.canvas.coords(self.start_window, self.width // 2, self.height // 2)
        if self.condition_window is not None:
            self.canvas.coords(self.condition_window, self.width // 2, self.height // 2 + 100)

    def _draw_landing(self) -> None:
        self.canvas.delete("all")
        self.canvas.create_text(
            self.width // 2,
            self.height // 2 - 100,
            text="VIZZ está listo para calibrar",
            fill="#ffffff",
            font=("Segoe UI", 24, "bold"),
        )
        self.canvas.create_text(
            self.width // 2,
            self.height // 2 - 52,
            text="Se calibrarán las dos condiciones y se guardarán en un único perfil.",
            fill="#c8c8c8",
            font=("Segoe UI", 14),
        )
        button = tk.Button(
            self.root,
            text="Iniciar calibración",
            command=self._start,
            bg="#d62027",
            fg="#ffffff",
            activebackground="#f04045",
            activeforeground="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=28,
            pady=14,
            font=("Segoe UI", 15, "bold"),
        )
        self.start_window = self.canvas.create_window(self.width // 2, self.height // 2, window=button)

    def _start(self) -> None:
        if self.started:
            return
        self.started = True
        if self.start_window is not None:
            self.canvas.delete(self.start_window)
            self.start_window = None
        self.root.after(300, self._begin_condition)

    def _begin_condition(self) -> None:
        if not self.started:
            return
        if self.condition_index >= len(self.conditions):
            self._finish()
            return
        self.point_index = 0
        self.capture = None
        self.point_state = "waiting_for_click"
        self._draw_point(show_status=True)
        self.root.after(50, self._tick)

    def _draw_point(self, *, show_status: bool) -> None:
        self.canvas.delete("all")
        self.status_id = None
        target_x, target_y = CALIBRATION_POINTS[self.point_index]
        x = int(round(target_x * self.width))
        y = int(round(target_y * self.height))
        self.canvas.create_oval(x - 18, y - 18, x + 18, y + 18, fill="#d62027", outline="#ffffff", width=2)
        self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="#ffffff", outline="")
        if show_status:
            condition_label = self.conditions[self.condition_index][1]
            self.status_id = self.canvas.create_text(
                18,
                18,
                anchor="nw",
                text=f"{condition_label}: mira el punto, lleva el cursor sobre él y haz clic · {self.point_index + 1}/{len(CALIBRATION_POINTS)} · Esc cancela",
                fill="#d0d0d0",
                font=("Segoe UI", 12),
            )

    def _set_status(self, message: str) -> None:
        if self.status_id is None:
            self.status_id = self.canvas.create_text(
                18,
                18,
                anchor="nw",
                text=message,
                fill="#d0d0d0",
                font=("Segoe UI", 12),
            )
        else:
            self.canvas.itemconfig(self.status_id, text=message)

    def _tick(self) -> None:
        if not self.root.winfo_exists() or self.point_state == "idle":
            return
        if self.point_state == "capturing" and self.capture is not None:
            sample = self.sample_provider()
            result = self.capture.push(time.monotonic(), sample)
            if result is None and self.capture.deadline is not None and time.monotonic() >= self.capture.deadline:
                result = self.capture.finish()
            if result is not None:
                self._handle_capture_result(result)
        self.root.after(50, self._tick)

    def _on_canvas_click(self, event: tk.Event[tk.Misc]) -> None:
        if not self.started or self.point_state != "waiting_for_click":
            return
        target_x, target_y = CALIBRATION_POINTS[self.point_index]
        target_px = target_x * self.width
        target_py = target_y * self.height
        distance = ((event.x - target_px) ** 2 + (event.y - target_py) ** 2) ** 0.5
        if distance > CLICK_TARGET_RADIUS_PX:
            self._set_status("Lleva el cursor sobre el punto rojo y haz clic para iniciar la captura")
            return
        # The mouse is only a scheduler. It arms a fixed window; it is never
        # stored as a gaze label and samples are not collected before this
        # event. The status text is removed before camera sampling begins.
        self.capture = StableCapture(CAPTURE_CONFIG)
        self.capture.arm(time.monotonic())
        self.point_state = "capturing"
        self._draw_point(show_status=False)

    def _handle_capture_result(self, result: CaptureResult) -> None:
        if not result.accepted or result.features is None:
            self.point_state = "waiting_for_click"
            self.capture = None
            messages = {
                "insufficient_valid_samples": "No hubo suficientes muestras válidas. Mira el punto y vuelve a hacer clic.",
                "insufficient_pose_samples": "No se pudo medir la pose. Mantén el rostro visible y vuelve a intentarlo.",
                "unstable_feature_window": "La mirada se movió durante la captura. Mira el punto y vuelve a hacer clic.",
            }
            self._draw_point(show_status=True)
            self._set_status(messages.get(result.reason, "Captura rechazada. Vuelve a intentarlo."))
            return
        target_x, target_y = CALIBRATION_POINTS[self.point_index]
        condition_key, _condition_label = self.conditions[self.condition_index]
        self.samples.append(
            {
                "features": list(result.features),
                "pose": list(result.pose) if result.pose is not None else None,
                "target": [target_x, target_y],
                "phase": "static",
                "condition": condition_key,
                "capture": {
                    "method": "stable_fixed_window",
                    "valid_count": result.valid_count,
                    "quality_mean": result.quality_mean,
                    "max_feature_mad": result.max_feature_mad,
                    "max_pose_mad": result.max_pose_mad,
                    "settle_seconds": CAPTURE_CONFIG.settle_seconds,
                    "window_seconds": CAPTURE_CONFIG.window_seconds,
                },
            }
        )
        self.point_state = "complete"
        self.capture = None
        self.point_index += 1
        if self.point_index < len(CALIBRATION_POINTS):
            self.root.after(220, self._begin_condition_point)
        else:
            self.root.after(220, self._show_condition_transition)

    def _begin_condition_point(self) -> None:
        if not self.started:
            return
        self.point_state = "waiting_for_click"
        self._draw_point(show_status=True)

    def _show_condition_transition(self) -> None:
        if self.condition_index + 1 >= len(self.conditions):
            self._finish()
            return
        self.point_state = "between_conditions"
        self.canvas.delete("all")
        self.status_id = None
        next_label = self.conditions[self.condition_index + 1][1]
        self.canvas.create_text(
            self.width // 2,
            self.height // 2 - 100,
            text=f"Primera condición completada. Ahora prepara la condición {next_label}.",
            fill="#ffffff",
            font=("Segoe UI", 24, "bold"),
        )
        self.canvas.create_text(
            self.width // 2,
            self.height // 2 - 48,
            text="Cuando estés listo, continúa. Se usará el mismo perfil para ambas condiciones.",
            fill="#c8c8c8",
            font=("Segoe UI", 14),
        )
        button = tk.Button(
            self.root,
            text=f"Continuar {next_label}",
            command=self._start_next_condition,
            bg="#d62027",
            fg="#ffffff",
            activebackground="#f04045",
            activeforeground="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=28,
            pady=14,
            font=("Segoe UI", 15, "bold"),
        )
        self.condition_window = self.canvas.create_window(self.width // 2, self.height // 2 + 100, window=button)

    def _start_next_condition(self) -> None:
        if self.condition_window is not None:
            self.canvas.delete(self.condition_window)
            self.condition_window = None
        self.condition_index += 1
        self.root.after(300, self._begin_condition)

    def _finish(self) -> None:
        expected_samples = len(CALIBRATION_POINTS) * len(self.conditions)
        if len(self.samples) < expected_samples:
            self.root.destroy()
            raise CalibrationAborted("calibration did not obtain a valid sample for every point")
        screen_size = (self.width, self.height)
        self.root.destroy()
        self.on_complete(self.samples, screen_size)
