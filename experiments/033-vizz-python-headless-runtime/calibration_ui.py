"""The only visible VIZZ surface: a fullscreen, one-shot calibration."""

from __future__ import annotations

import time
import tkinter as tk
from collections.abc import Callable

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
SAMPLES_PER_POINT = 16
CLICK_TARGET_RADIUS_PX = 100


class CalibrationAborted(RuntimeError):
    pass


class CalibrationWindow:
    def __init__(
        self,
        sample_provider: Callable[[], GazeSample | None],
        on_complete: Callable[[list[dict[str, object]], tuple[int, int]], None],
    ) -> None:
        self.sample_provider = sample_provider
        self.on_complete = on_complete
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
        self.samples: list[dict[str, object]] = []
        self.point_samples: list[tuple[float, ...]] = []
        self.started_at = 0.0
        self.dot_id: int | None = None
        self.status_id: int | None = None
        self.started = False
        self.point_active = False
        self.start_window: int | None = None
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
            text="Presiona el botón cuando estés preparado. Después mira cada punto.",
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
        self.root.after(300, self._begin_point)

    def _begin_point(self) -> None:
        if not self.started:
            return
        if self.point_index >= len(CALIBRATION_POINTS):
            self._finish()
            return
        self.point_samples = []
        self.point_active = True
        self.started_at = time.monotonic()
        self._draw_point()
        self.root.after(50, self._tick)

    def _draw_point(self) -> None:
        self.canvas.delete("all")
        target_x, target_y = CALIBRATION_POINTS[self.point_index]
        x = int(round(target_x * self.width))
        y = int(round(target_y * self.height))
        self.canvas.create_oval(x - 18, y - 18, x + 18, y + 18, fill="#d62027", outline="#ffffff", width=2)
        self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="#ffffff", outline="")
        self.status_id = self.canvas.create_text(
            18,
            18,
            anchor="nw",
            text=f"Mira el punto y haz clic sobre él cuando estés listo · {self.point_index + 1}/{len(CALIBRATION_POINTS)} · Esc cancela",
            fill="#d0d0d0",
            font=("Segoe UI", 12),
        )

    def _tick(self) -> None:
        if not self.root.winfo_exists() or not self.point_active:
            return
        sample = self.sample_provider()
        if sample is not None and sample.quality >= 0.50:
            self.point_samples.append(sample.features)
        if self.status_id is not None:
            self.canvas.itemconfig(
                self.status_id,
                text=f"Mira el punto y haz clic sobre él cuando estés listo · muestras {len(self.point_samples)}/{SAMPLES_PER_POINT} · Esc cancela",
            )
        self.root.after(50, self._tick)

    def _on_canvas_click(self, event: tk.Event[tk.Misc]) -> None:
        if not self.started or not self.point_active:
            return
        target_x, target_y = CALIBRATION_POINTS[self.point_index]
        target_px = target_x * self.width
        target_py = target_y * self.height
        distance = ((event.x - target_px) ** 2 + (event.y - target_py) ** 2) ** 0.5
        if distance > CLICK_TARGET_RADIUS_PX:
            if self.status_id is not None:
                self.canvas.itemconfig(self.status_id, text="Haz clic sobre el punto rojo para confirmar esta muestra")
            return
        if len(self.point_samples) < SAMPLES_PER_POINT:
            if self.status_id is not None:
                self.canvas.itemconfig(
                    self.status_id,
                    text=f"Aún faltan muestras válidas ({len(self.point_samples)}/{SAMPLES_PER_POINT}); mantén la mirada y vuelve a hacer clic",
                )
            return
        feature_count = len(self.point_samples)
        mean_features = tuple(sum(values[index] for values in self.point_samples) / feature_count for index in range(6))
        self.samples.append({"features": list(mean_features), "target": [target_x, target_y]})
        self.point_active = False
        self.point_index += 1
        self.root.after(220, self._begin_point)

    def _finish(self) -> None:
        if len(self.samples) < len(CALIBRATION_POINTS):
            self.root.destroy()
            raise CalibrationAborted("calibration did not obtain a valid sample for every point")
        screen_size = (self.width, self.height)
        self.root.destroy()
        self.on_complete(self.samples, screen_size)
