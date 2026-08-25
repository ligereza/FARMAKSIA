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
POINT_TIMEOUT_SECONDS = 3.0


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
        self.root.after(300, self._begin_point)

    def run(self) -> None:
        self.root.mainloop()

    def abort(self) -> None:
        self.root.destroy()
        raise CalibrationAborted("calibration cancelled")

    def _on_resize(self, _event: tk.Event[tk.Misc]) -> None:
        self.width = max(1, self.canvas.winfo_width())
        self.height = max(1, self.canvas.winfo_height())

    def _begin_point(self) -> None:
        if self.point_index >= len(CALIBRATION_POINTS):
            self._finish()
            return
        self.point_samples = []
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
            text=f"Mira el punto {self.point_index + 1}/{len(CALIBRATION_POINTS)} · Esc cancela",
            fill="#d0d0d0",
            font=("Segoe UI", 12),
        )

    def _tick(self) -> None:
        if not self.root.winfo_exists():
            return
        sample = self.sample_provider()
        if sample is not None and sample.quality >= 0.50:
            self.point_samples.append(sample.features)
        elapsed = time.monotonic() - self.started_at
        if len(self.point_samples) >= SAMPLES_PER_POINT or elapsed >= POINT_TIMEOUT_SECONDS:
            if self.point_samples:
                feature_count = len(self.point_samples)
                mean_features = tuple(sum(values[index] for values in self.point_samples) / feature_count for index in range(6))
                target = CALIBRATION_POINTS[self.point_index]
                self.samples.append({"features": list(mean_features), "target": list(target)})
            self.point_index += 1
            self.root.after(220, self._begin_point)
            return
        self.root.after(50, self._tick)

    def _finish(self) -> None:
        if len(self.samples) < len(CALIBRATION_POINTS):
            self.root.destroy()
            raise CalibrationAborted("calibration did not obtain a valid sample for every point")
        screen_size = (self.width, self.height)
        self.root.destroy()
        self.on_complete(self.samples, screen_size)
