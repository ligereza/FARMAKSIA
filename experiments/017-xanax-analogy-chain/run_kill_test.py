"""Kill tests for the X-ANA-X analogy chain."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).parent
SPEC = importlib.util.spec_from_file_location("xanax_runner", HERE / "run_experiment.py")
if SPEC is None or SPEC.loader is None:
    raise SystemExit("KILL_TEST_INVALID: could not load runner")
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


def main() -> None:
    result = RUNNER.run_chain()
    catalog = json.loads((HERE / "source_catalog.json").read_text(encoding="utf-8"))
    static_rankings = RUNNER.select_source(catalog["sources"], {"point", "contains", "region"})
    events = RUNNER.load_events()
    regions = RUNNER.load_regions()
    if result["search"]["selected_source"] != "queue-interval":
        raise SystemExit("KILL_TEST_INVALID: temporal search did not select interval source")
    if result["verification"]["prediction_verified"] is not True:
        raise SystemExit("KILL_TEST_INVALID: valid analogy lost verification")
    if result["rupture"]["source_prediction"] != "unavailable_without_target_geometry":
        raise SystemExit("KILL_TEST_INVALID: analogy invented target geometry")
    if static_rankings[0]["source"] != "static-containment":
        raise SystemExit("KILL_TEST_INVALID: scent ranking control failed")
    if RUNNER.active_regions(None, 0.25) is not None:
        raise SystemExit("KILL_TEST_INVALID: temporal prediction survived missing events")
    no_events_target = RUNNER.verify_target(regions, None, 0.25)
    if no_events_target["active_and_center"] is not None:
        raise SystemExit("KILL_TEST_INVALID: target answered without events")
    if result["human_data"] or result["arbitrary_corpus"] or result["search"]["network_used"]:
        raise SystemExit("KILL_TEST_INVALID: chain used prohibited data source")
    print("KILL_TESTS_VALID")
    print("temporal_without_events=unavailable")
    print("geometry_without_mapping=unavailable")


if __name__ == "__main__":
    main()
