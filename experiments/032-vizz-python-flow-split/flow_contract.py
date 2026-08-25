"""Executable state boundary for visible calibration and invisible runtime."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class Phase(StrEnum):
    IDLE = "idle"
    CALIBRATION_UI = "calibration_ui"
    PROFILE_SEALED = "profile_sealed"
    HEADLESS_RUNTIME = "headless_runtime"
    CONTENT_MODIFIER = "content_modifier"
    STOPPED = "stopped"


class FlowContractError(RuntimeError):
    pass


@dataclass
class VizzFlow:
    phase: Phase = Phase.IDLE
    sample_count: int = 0
    profile_path: Path | None = None
    interface_visible: bool = False

    def start_calibration(self) -> None:
        if self.phase not in (Phase.IDLE, Phase.STOPPED):
            raise FlowContractError("calibration can only start from idle or stopped")
        self.phase = Phase.CALIBRATION_UI
        self.sample_count = 0
        self.profile_path = None
        self.interface_visible = True

    def capture_sample(self, feature_vector_present: bool) -> None:
        if self.phase is not Phase.CALIBRATION_UI:
            raise FlowContractError("samples require the visible calibration phase")
        if not feature_vector_present:
            raise FlowContractError("a calibration sample cannot be sealed without GPU features")
        self.sample_count += 1

    def seal_profile(self, profile_path: Path, minimum_samples: int = 12) -> None:
        if self.phase is not Phase.CALIBRATION_UI:
            raise FlowContractError("only calibration can seal a profile")
        if self.sample_count < minimum_samples:
            raise FlowContractError("profile does not meet the calibration sample minimum")
        self.phase = Phase.PROFILE_SEALED
        self.profile_path = profile_path
        self.interface_visible = False

    def start_headless_runtime(self, cuda_ready: bool) -> None:
        if self.phase is not Phase.PROFILE_SEALED:
            raise FlowContractError("headless runtime requires a sealed profile")
        if not cuda_ready:
            raise FlowContractError("cuda_unavailable")
        self.phase = Phase.HEADLESS_RUNTIME
        self.interface_visible = False

    def attach_content_modifier(self, modifier_ready: bool) -> None:
        if self.phase is not Phase.HEADLESS_RUNTIME:
            raise FlowContractError("content modifier requires headless runtime")
        if not modifier_ready:
            raise FlowContractError("content_modifier_unavailable")
        self.phase = Phase.CONTENT_MODIFIER
        self.interface_visible = False

    def stop(self) -> None:
        self.phase = Phase.STOPPED
        self.interface_visible = False
        self.sample_count = 0
        self.profile_path = None
