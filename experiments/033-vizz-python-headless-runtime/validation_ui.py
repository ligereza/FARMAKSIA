"""Visible, no-video validation protocol for pose/condition diagnostics."""

from __future__ import annotations

import random
import time
import tkinter as tk
from collections.abc import Callable

from calibration_capture import CaptureConfig, CaptureResult, StableCapture
from calibration_ui import CALIBRATION_POINTS
from gpu_tracker import GazeSample


VALIDATION_CONFIG = CaptureConfig(
    settle_seconds=0.30,
    window_seconds=0.90,
    min_valid_samples=12,
    min_quality=0.50,
    max_feature_mad=0.08,
)
VALIDATION_ORDER_SEED = 20260824
CLICK_TARGET_RADIUS_PX = 100


class ValidationAborted(RuntimeError):
    pass


class ValidationWindow:
    def __init__(
        self,
        sample_provider: Callable[[], GazeSample | None],
        on_complete: Callable[[list[dict[str, object]], tuple[int, int], list[int]], None],
        conditions: tuple[tuple[str, str], ...],
        repetitions: int = 3,
    ) -> None:
        if not conditions or repetitions < 1:
            raise ValueError("validation requires conditions and repetitions")
        self.sample_provider = sample_provider
        self.on_complete = on_complete
        self.conditions = conditions
        self.repetitions = repetitions
        self.order = list(range(len(CALIBRATION_POINTS)))
        random.Random(VALIDATION_ORDER_SEED).shuffle(self.order)
        self.root = tk.Tk()
        self.root.title("FARMAKSIA — validación VIZZ")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="black")
        self.root.protocol("WM_DELETE_WINDOW", self.abort)
        self.root.bind("<Escape>", lambda _event: self.abort())
        self.canvas = tk.Canvas(self.root, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.width = max(1, self.root.winfo_screenwidth())
        self.height = max(1, self.root.winfo_screenheight())
        self.started = False
        self.condition_index = 0
        self.repetition_index = 0
        self.order_index = 0
        self.state = "idle"
        self.capture: StableCapture | None = None
        self.records: list[dict[str, object]] = []
        self.status_id: int | None = None
        self.start_window: int | None = None
        self.transition_window: int | None = None
        self._draw_landing()

    def run(self) -> None:
        self.root.mainloop()

    def abort(self) -> None:
        self.root.destroy()
        raise ValidationAborted("validation cancelled")

    def _on_resize(self, _event: tk.Event[tk.Misc]) -> None:
        self.width = max(1, self.canvas.winfo_width())
        self.height = max(1, self.canvas.winfo_height())
        if self.start_window is not None:
            self.canvas.coords(self.start_window, self.width // 2, self.height // 2 + 80)
        if self.transition_window is not None:
            self.canvas.coords(self.transition_window, self.width // 2, self.height // 2 + 100)

    def _draw_landing(self) -> None:
        self.canvas.delete("all")
        self.canvas.create_text(
            self.width // 2,
            self.height // 2 - 120,
            text="Validación controlada VIZZ",
            fill="#ffffff",
            font=("Segoe UI", 24, "bold"),
        )
        self.canvas.create_text(
            self.width // 2,
            self.height // 2 - 58,
            text="Mantén la cámara y la pantalla fijas. Se registran pose y mirada, nunca vídeo.",
            fill="#c8c8c8",
            font=("Segoe UI", 14),
        )
        self.canvas.create_text(
            self.width // 2,
            self.height // 2 - 20,
            text=f"{len(self.conditions)} condiciones · {self.repetitions} repeticiones · orden reproducible",
            fill="#c8c8c8",
            font=("Segoe UI", 14),
        )
        button = tk.Button(
            self.root,
            text="Iniciar validación",
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
        self.start_window = self.canvas.create_window(self.width // 2, self.height // 2 + 80, window=button)

    def _start(self) -> None:
        if self.started:
            return
        self.started = True
        if self.start_window is not None:
            self.canvas.delete(self.start_window)
            self.start_window = None
        self.root.after(300, self._draw_target)

    def _current_target(self) -> tuple[int, tuple[float, float]]:
        target_index = self.order[self.order_index]
        return target_index, CALIBRATION_POINTS[target_index]

    def _draw_target(self) -> None:
        if self.condition_index >= len(self.conditions):
            self._finish()
            return
        if self.order_index >= len(self.order):
            if self.repetition_index + 1 < self.repetitions:
                self.repetition_index += 1
                self.order_index = 0
                self.root.after(220, self._draw_target)
            elif self.condition_index + 1 < len(self.conditions):
                self._show_condition_transition()
            else:
                self._finish()
            return
        self.state = "waiting_for_click"
        self.capture = None
        self.canvas.delete("all")
        self.status_id = None
        target_index, (target_x, target_y) = self._current_target()
        x = int(round(target_x * self.width))
        y = int(round(target_y * self.height))
        self.canvas.create_oval(x - 18, y - 18, x + 18, y + 18, fill="#d62027", outline="#ffffff", width=2)
        self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="#ffffff", outline="")
        condition_label = self.conditions[self.condition_index][1]
        self.status_id = self.canvas.create_text(
            18,
            18,
            anchor="nw",
            text=f"{condition_label} · repetición {self.repetition_index + 1}/{self.repetitions} · punto {target_index + 1}/{len(CALIBRATION_POINTS)} · lleva el cursor al punto y haz clic",
            fill="#d0d0d0",
            font=("Segoe UI", 12),
        )
        self.root.after(50, self._tick)

    def _tick(self) -> None:
        if not self.root.winfo_exists() or self.state == "idle":
            return
        if self.state == "capturing" and self.capture is not None:
            sample = self.sample_provider()
            result = self.capture.push(time.monotonic(), sample)
            if result is None and self.capture.deadline is not None and time.monotonic() >= self.capture.deadline:
                result = self.capture.finish()
            if result is not None:
                self._handle_capture_result(result)
        self.root.after(50, self._tick)

    def _on_canvas_click(self, event: tk.Event[tk.Misc]) -> None:
        if not self.started or self.state != "waiting_for_click":
            return
        _target_index, (target_x, target_y) = self._current_target()
        target_px = target_x * self.width
        target_py = target_y * self.height
        distance = ((event.x - target_px) ** 2 + (event.y - target_py) ** 2) ** 0.5
        if distance > CLICK_TARGET_RADIUS_PX:
            if self.status_id is not None:
                self.canvas.itemconfig(self.status_id, text="Lleva el cursor sobre el punto rojo para iniciar")
            return
        self.capture = StableCapture(VALIDATION_CONFIG)
        self.capture.arm(time.monotonic())
        self.state = "capturing"
        self.canvas.delete("all")
        self.status_id = None
        x = int(round(target_x * self.width))
        y = int(round(target_y * self.height))
        self.canvas.create_oval(x - 18, y - 18, x + 18, y + 18, fill="#d62027", outline="#ffffff", width=2)
        self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="#ffffff", outline="")

    def _handle_capture_result(self, result: CaptureResult) -> None:
        if not result.accepted or result.features is None:
            self.state = "waiting_for_click"
            self.capture = None
            if self.status_id is None:
                self.status_id = self.canvas.create_text(18, 18, anchor="nw", fill="#d0d0d0", font=("Segoe UI", 12))
            message = {
                "insufficient_valid_samples": "Muestras insuficientes; repite este punto.",
                "unstable_feature_window": "Ventana inestable; repite este punto sin mover la cabeza.",
            }.get(result.reason, "Captura rechazada; repite este punto.")
            self.canvas.itemconfig(self.status_id, text=message)
            return
        target_index, (target_x, target_y) = self._current_target()
        condition_key, _condition_label = self.conditions[self.condition_index]
        self.records.append(
            {
                "condition": condition_key,
                "repetition": self.repetition_index + 1,
                "target_index": target_index,
                "target": [target_x, target_y],
                "features": list(result.features),
                "pose": list(result.pose) if result.pose is not None else None,
                "capture": {
                    "method": "stable_fixed_window",
                    "valid_count": result.valid_count,
                    "quality_mean": result.quality_mean,
                    "max_feature_mad": result.max_feature_mad,
                    "max_pose_mad": result.max_pose_mad,
                    "settle_seconds": VALIDATION_CONFIG.settle_seconds,
                    "window_seconds": VALIDATION_CONFIG.window_seconds,
                },
            }
        )
        self.state = "complete"
        self.capture = None
        self.order_index += 1
        self.root.after(220, self._draw_target)

    def _show_condition_transition(self) -> None:
        self.state = "between_conditions"
        self.canvas.delete("all")
        self.status_id = None
        next_label = self.conditions[self.condition_index + 1][1]
        self.canvas.create_text(
            self.width // 2,
            self.height // 2 - 100,
            text=f"Condición completada. Prepara la condición {next_label}.",
            fill="#ffffff",
            font=("Segoe UI", 24, "bold"),
        )
        self.canvas.create_text(
            self.width // 2,
            self.height // 2 - 48,
            text="Mantén la cámara y la pantalla en la misma posición.",
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
        self.transition_window = self.canvas.create_window(self.width // 2, self.height // 2 + 100, window=button)

    def _start_next_condition(self) -> None:
        if self.transition_window is not None:
            self.canvas.delete(self.transition_window)
            self.transition_window = None
        self.condition_index += 1
        self.repetition_index = 0
        self.order_index = 0
        self.root.after(300, self._draw_target)

    def _finish(self) -> None:
        expected = len(self.conditions) * self.repetitions * len(CALIBRATION_POINTS)
        if len(self.records) != expected:
            self.root.destroy()
            raise ValidationAborted("validation did not complete all planned captures")
        screen_size = (self.width, self.height)
        order = list(self.order)
        self.root.destroy()
        self.on_complete(self.records, screen_size, order)
