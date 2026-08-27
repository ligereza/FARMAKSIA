"""Declarative, reversible contract for a grandMA3-to-Titan visual adapter."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any


SCHEMA = "farmaxia:lighting-surface-contract:0.1"
TASKS = frozenset(
    {
        "fixture_selection",
        "attribute_control",
        "reusable_value",
        "cue_sequence",
        "playback_control",
    }
)
STATUSES = frozenset({"compatible", "partial", "unknown", "unsupported"})
CAPABILITIES = frozenset({"read_only", "preview", "input_pending", "execute_blocked"})


class ContractError(ValueError):
    """Raised when the adapter contract would make an unsafe claim."""


@dataclass(frozen=True)
class Rect:
    x: float
    y: float
    width: float
    height: float

    @classmethod
    def from_value(cls, value: Any) -> "Rect":
        if not isinstance(value, list) or len(value) != 4:
            raise ContractError("rect must contain [x, y, width, height]")
        numbers = tuple(float(item) for item in value)
        if not all(math.isfinite(item) for item in numbers):
            raise ContractError("rect must contain finite numbers")
        rect = cls(*numbers)
        if rect.x < 0 or rect.y < 0 or rect.width <= 0 or rect.height <= 0:
            raise ContractError("rect must be positive and inside the surface")
        if rect.x + rect.width > 1 or rect.y + rect.height > 1:
            raise ContractError("rect must use normalized coordinates in [0, 1]")
        return rect

    def forward(self, point: tuple[float, float]) -> tuple[float, float]:
        u, v = point
        if not 0 <= u <= 1 or not 0 <= v <= 1:
            raise ContractError("local point is outside the source region")
        return self.x + u * self.width, self.y + v * self.height

    def inverse(self, point: tuple[float, float]) -> tuple[float, float]:
        x, y = point
        if not self.x <= x <= self.x + self.width or not self.y <= y <= self.y + self.height:
            raise ContractError("point is outside the destination region")
        return (x - self.x) / self.width, (y - self.y) / self.height

    def overlaps(self, other: "Rect") -> bool:
        return not (
            self.x + self.width <= other.x
            or other.x + other.width <= self.x
            or self.y + self.height <= other.y
            or other.y + other.height <= self.y
        )


@dataclass(frozen=True)
class Region:
    region_id: str
    canonical_task: str
    source_object_kind: str
    source_role: str
    target_term: str | None
    target_object_kind: str | None
    status: str
    confidence: float
    source_rect: Rect
    destination_rect: Rect

    @classmethod
    def from_value(cls, value: Any) -> "Region":
        if not isinstance(value, dict):
            raise ContractError("region must be an object")
        required = (
            "region_id",
            "canonical_task",
            "source_object_kind",
            "source_role",
            "status",
            "confidence",
            "source_rect",
            "destination_rect",
        )
        missing = [key for key in required if key not in value]
        if missing:
            raise ContractError(f"region missing fields: {','.join(missing)}")
        region_id = str(value["region_id"])
        task = str(value["canonical_task"])
        source_kind = str(value["source_object_kind"])
        source_role = str(value["source_role"])
        status = str(value["status"])
        confidence = float(value["confidence"])
        if not region_id or not source_kind or not source_role:
            raise ContractError("region identity fields cannot be empty")
        if task not in TASKS:
            raise ContractError(f"unknown canonical task: {task}")
        if status not in STATUSES:
            raise ContractError(f"unknown mapping status: {status}")
        if not 0 <= confidence <= 1 or not math.isfinite(confidence):
            raise ContractError("confidence must be in [0, 1]")
        target_term = value.get("target_term")
        target_kind = value.get("target_object_kind")
        if status in {"compatible", "partial"} and not target_term:
            raise ContractError("mapped regions require a target term")
        if status in {"unknown", "unsupported"} and confidence != 0:
            raise ContractError("unknown or unsupported regions require confidence 0")
        return cls(
            region_id=region_id,
            canonical_task=task,
            source_object_kind=source_kind,
            source_role=source_role,
            target_term=str(target_term) if target_term else None,
            target_object_kind=str(target_kind) if target_kind else None,
            status=status,
            confidence=confidence,
            source_rect=Rect.from_value(value["source_rect"]),
            destination_rect=Rect.from_value(value["destination_rect"]),
        )


@dataclass(frozen=True)
class LightingSurfaceContract:
    source_app: str
    source_version: str
    target_vocabulary: str
    mode: str
    capabilities: tuple[str, ...]
    regions: tuple[Region, ...]

    @classmethod
    def from_value(cls, value: Any) -> "LightingSurfaceContract":
        if not isinstance(value, dict) or value.get("schema") != SCHEMA:
            raise ContractError("unexpected lighting surface contract schema")
        source = value.get("source_surface")
        target = value.get("target_vocabulary")
        mode = value.get("mode")
        if not isinstance(source, dict) or not source.get("app") or not source.get("version"):
            raise ContractError("source surface requires app and version")
        if target != "Avolites Titan":
            raise ContractError("this experiment targets Avolites Titan")
        if mode not in {"declarative_fixture", "observed_read_only"}:
            raise ContractError("contract mode must be declarative_fixture or observed_read_only")
        capabilities = tuple(str(item) for item in value.get("capabilities", []))
        if set(capabilities) - CAPABILITIES:
            raise ContractError("unknown capability in contract")
        if "read_only" not in capabilities or "execute_blocked" not in capabilities:
            raise ContractError("lighting adapter must be read-only and execution-blocked")
        raw_regions = value.get("regions")
        if not isinstance(raw_regions, list) or not raw_regions:
            raise ContractError("contract requires at least one region")
        regions = tuple(Region.from_value(item) for item in raw_regions)
        ids = [region.region_id for region in regions]
        if len(ids) != len(set(ids)):
            raise ContractError("region ids must be unique")
        tasks = [region.canonical_task for region in regions]
        if set(tasks) != TASKS:
            raise ContractError("fixture must cover exactly the five canonical tasks")
        for left_index, left in enumerate(regions):
            for right in regions[left_index + 1 :]:
                if left.destination_rect.overlaps(right.destination_rect):
                    raise ContractError("destination regions overlap")
        return cls(
            source_app=str(source["app"]),
            source_version=str(source["version"]),
            target_vocabulary=str(target),
            mode=str(mode),
            capabilities=capabilities,
            regions=regions,
        )

    def region_for_task(self, task: str) -> Region:
        matches = [region for region in self.regions if region.canonical_task == task]
        if len(matches) != 1:
            raise ContractError(f"task must map to exactly one region: {task}")
        return matches[0]

    def preview_point(self, task: str, local_point: tuple[float, float]) -> tuple[float, float]:
        region = self.region_for_task(task)
        if region.status not in {"compatible", "partial"}:
            raise ContractError(f"task is not previewable: {task}")
        source_point = region.source_rect.forward(local_point)
        source_local = region.source_rect.inverse(source_point)
        return region.destination_rect.forward(source_local)

    def inverse_point(self, task: str, destination_point: tuple[float, float]) -> tuple[float, float]:
        region = self.region_for_task(task)
        if region.status not in {"compatible", "partial"}:
            raise ContractError(f"task is not reversible: {task}")
        local_point = region.destination_rect.inverse(destination_point)
        return region.source_rect.forward(local_point)

    def as_summary(self) -> dict[str, Any]:
        return {
            "source_app": self.source_app,
            "source_version": self.source_version,
            "target_vocabulary": self.target_vocabulary,
            "mode": self.mode,
            "task_count": len(self.regions),
            "mapped_task_count": sum(region.status in {"compatible", "partial"} for region in self.regions),
            "partial_task_count": sum(region.status == "partial" for region in self.regions),
            "capabilities": list(self.capabilities),
        }
