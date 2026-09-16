"""Mathematical contract for VIZZ distance-relative visual scaling.

The credit card is deliberately absent from runtime observations. It is a
one-time reference object; runtime scale is estimated from two independent
facial measurements and an explicit, limited pose correction.
"""

from __future__ import annotations

from dataclasses import dataclass
import math


class ScaleContractError(ValueError):
    """The observation cannot support a trustworthy scale estimate."""


def _finite_positive(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise ScaleContractError(f"{name} must be finite and positive")
    return value


def _finite(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ScaleContractError(f"{name} must be finite")
    return value


@dataclass(frozen=True)
class ScaleObservation:
    """One timestamp or robust window summary in camera pixels."""

    eye_distance_px: float
    face_width_px: float
    yaw_deg: float = 0.0
    pitch_deg: float = 0.0
    roll_deg: float = 0.0
    eye_quality: float = 1.0
    face_quality: float = 1.0

    def validate(self) -> None:
        _finite_positive("eye_distance_px", self.eye_distance_px)
        _finite_positive("face_width_px", self.face_width_px)
        for name, value in (
            ("yaw_deg", self.yaw_deg),
            ("pitch_deg", self.pitch_deg),
            ("roll_deg", self.roll_deg),
        ):
            _finite(name, value)
        for name, value in (
            ("eye_quality", self.eye_quality),
            ("face_quality", self.face_quality),
        ):
            value = _finite(name, value)
            if not 0.0 < value <= 1.0:
                raise ScaleContractError(f"{name} must be in (0, 1]")


def pose_projection_factor(
    observation: ScaleObservation,
    *,
    max_abs_pose_deg: float = 35.0,
    min_projection_factor: float = 0.55,
) -> float:
    """Approximate horizontal projection correction for a bounded pose.

    This is a controlled-protocol correction, not a 3-D anatomical model.
    Roll does not change Euclidean distances. Outside the bounded yaw/pitch
    domain the correct answer is UNKNOWN rather than extrapolation.
    """

    observation.validate()
    if abs(observation.yaw_deg) > max_abs_pose_deg:
        raise ScaleContractError("yaw is outside the calibrated domain")
    if abs(observation.pitch_deg) > max_abs_pose_deg:
        raise ScaleContractError("pitch is outside the calibrated domain")
    factor = math.cos(math.radians(observation.yaw_deg)) * math.cos(
        math.radians(observation.pitch_deg)
    )
    if factor < min_projection_factor:
        raise ScaleContractError("pose projection is too oblique")
    return factor


def corrected_dimensions(observation: ScaleObservation) -> tuple[float, float, float]:
    """Return pose-corrected eye distance, face width and projection factor."""

    factor = pose_projection_factor(observation)
    return observation.eye_distance_px / factor, observation.face_width_px / factor, factor


@dataclass(frozen=True)
class ScaleEstimate:
    status: str
    eye_scale: float
    face_scale: float
    fused_scale: float | None
    relative_distance_ratio: float | None
    log_disagreement: float
    reference_projection_factor: float
    current_projection_factor: float

    def as_dict(self) -> dict[str, float | str | None]:
        return {
            "status": self.status,
            "eye_scale": self.eye_scale,
            "face_scale": self.face_scale,
            "fused_scale": self.fused_scale,
            "relative_distance_ratio": self.relative_distance_ratio,
            "log_disagreement": self.log_disagreement,
            "reference_projection_factor": self.reference_projection_factor,
            "current_projection_factor": self.current_projection_factor,
        }


def fuse_scale(
    reference: ScaleObservation,
    current: ScaleObservation,
    *,
    max_log_disagreement: float = 0.25,
) -> ScaleEstimate:
    """Fuse both facial rulers through a weighted geometric mean.

    ``fused_scale`` is apparent facial scale relative to the reference. The
    relative eye-to-screen distance is its reciprocal. Both signals are
    mandatory; disagreement produces UNKNOWN instead of silently selecting
    the cleaner-looking signal.
    """

    if max_log_disagreement <= 0 or not math.isfinite(max_log_disagreement):
        raise ScaleContractError("max_log_disagreement must be positive and finite")
    ref_eye, ref_face, ref_factor = corrected_dimensions(reference)
    cur_eye, cur_face, cur_factor = corrected_dimensions(current)
    eye_scale = cur_eye / ref_eye
    face_scale = cur_face / ref_face
    log_disagreement = abs(math.log(eye_scale) - math.log(face_scale))
    if log_disagreement > max_log_disagreement:
        return ScaleEstimate(
            "UNKNOWN", eye_scale, face_scale, None, None, log_disagreement,
            ref_factor, cur_factor,
        )

    eye_weight = current.eye_quality * reference.eye_quality
    face_weight = current.face_quality * reference.face_quality
    if eye_weight <= 0 or face_weight <= 0:
        raise ScaleContractError("both eye and face measurements must contribute")
    fused = math.exp(
        (eye_weight * math.log(eye_scale) + face_weight * math.log(face_scale))
        / (eye_weight + face_weight)
    )
    return ScaleEstimate(
        "VALID", eye_scale, face_scale, fused, 1.0 / fused,
        log_disagreement, ref_factor, cur_factor,
    )


@dataclass(frozen=True)
class ScreenSpec:
    width_mm: float
    height_mm: float
    width_px: int
    height_px: int

    def validate(self) -> None:
        _finite_positive("screen.width_mm", self.width_mm)
        _finite_positive("screen.height_mm", self.height_mm)
        if self.width_px <= 0 or self.height_px <= 0:
            raise ScaleContractError("screen pixel dimensions must be positive")

    @property
    def pixel_pitch_x_mm(self) -> float:
        self.validate()
        return self.width_mm / self.width_px

    @property
    def pixel_pitch_y_mm(self) -> float:
        self.validate()
        return self.height_mm / self.height_px

    def target_geometry(
        self,
        *,
        base_diameter_px: float,
        distance_mm: float,
        reference_distance_mm: float,
        gap_ratio: float = 0.20,
        stroke_ratio: float = 0.20,
    ) -> dict[str, float]:
        """Size a Landolt C so its angular size stays constant."""

        base_diameter_px = _finite_positive("base_diameter_px", base_diameter_px)
        distance_mm = _finite_positive("distance_mm", distance_mm)
        reference_distance_mm = _finite_positive(
            "reference_distance_mm", reference_distance_mm
        )
        if not 0 < gap_ratio < 1 or not 0 < stroke_ratio < 0.5:
            raise ScaleContractError("Landolt C ratios are outside their contract")
        diameter_px = base_diameter_px * distance_mm / reference_distance_mm
        diameter_mm = diameter_px * self.pixel_pitch_x_mm
        angular_width_deg = math.degrees(
            2.0 * math.atan((diameter_mm / 2.0) / distance_mm)
        )
        return {
            "diameter_px": diameter_px,
            "diameter_mm": diameter_mm,
            "angular_width_deg": angular_width_deg,
            "gap_px": diameter_px * gap_ratio,
            "stroke_px": diameter_px * stroke_ratio,
        }


def landolt_c_geometry(
    diameter_px: float, *, gap_ratio: float = 0.20, stroke_ratio: float = 0.20
) -> dict[str, float | str]:
    """Return the scale-invariant geometry used by the visual target."""

    diameter_px = _finite_positive("diameter_px", diameter_px)
    if not 0 < gap_ratio < 1 or not 0 < stroke_ratio < 0.5:
        raise ScaleContractError("Landolt C ratios are outside their contract")
    return {
        "shape": "landolt_c",
        "diameter_px": diameter_px,
        "gap_ratio": gap_ratio,
        "stroke_ratio": stroke_ratio,
        "opening": "right",
    }
