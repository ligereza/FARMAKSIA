from __future__ import annotations

from phase_chaser import PhaseChaser


def event(sequence: int, seconds: float, *, state: str = "present") -> dict:
    return {
        "sequence": sequence,
        "event_id": f"event-{sequence}",
        "timestamp": f"2026-01-01T00:00:0{sequence}.000Z",
        "time_seconds": seconds,
        "timecode": f"00:00:00:{sequence:02d}",
        "event_type": "audio.gap" if state == "missing" else "audio.pulse",
        "payload": {"amplitude": 0.8 if state == "present" else 0.0, "pulse": 1.0 if state == "present" else 0.0, "signal_state": state},
    }


def test_restart_resume_matches_continuous_phase_chaser():
    events = [event(1, 0.2), event(2, 0.8), event(3, 1.2, state="missing"), event(4, 1.6)]
    continuous = PhaseChaser(["ble-01", "ble-02", "ble-03"]).process_all(events)
    first = PhaseChaser(["ble-01", "ble-02", "ble-03"])
    first_states = first.process_all(events[:2])
    resumed = PhaseChaser.from_checkpoint(first.checkpoint())
    resumed_states = resumed.process_all(events[2:])
    assert [*first_states, *resumed_states] == continuous


def test_audio_loss_blackouts_intensity_and_fixture_count_is_configurable():
    state = PhaseChaser(["ble-01", "ble-02", "ble-03", "ble-04"]).process(event(1, 0.4, state="missing"))
    assert len(state["lights"]) == 4
    assert all(light["intensity"] == 0.0 and light["pulse"] == 0.0 for light in state["lights"])
