"""Audit the real VIZZ/WebGazer adapter without opening a camera."""

from __future__ import annotations

import json
import re
from pathlib import Path


HERE = Path(__file__).parent


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> None:
    failures: list[str] = []
    policy = json.loads((HERE / "runtime_policy.json").read_text(encoding="utf-8"))
    html = (HERE / "index.html").read_text(encoding="utf-8")
    js = (HERE / "app.js").read_text(encoding="utf-8")
    vendor = HERE / "vendor" / "webgazer.js"

    require(policy["schema"] == "farmaxia:vizz-webgazer-runtime:0.1", "wrong runtime policy schema", failures)
    require(policy["dependency"]["version"] == "3.5.3", "WebGazer version is not pinned", failures)
    require(policy["dependency"]["license"] == "GPL-3.0-or-later", "WebGazer license is not recorded", failures)
    require(policy["privacy"] == {
        "consent_required": True,
        "camera_default": "off",
        "network_allowed": False,
        "network_scope": "same_origin_only_for_bundled_assets",
        "sample_persistence": "none",
        "raw_video_persistence": "none",
        "clear_on_stop": True,
        "coordinates_displayed_in_memory": True,
    }, "privacy policy drifted", failures)
    require(vendor.is_file() and vendor.stat().st_size > 1_000_000, "local WebGazer bundle is missing or unexpectedly small", failures)
    require((HERE / "vendor" / "LICENSE.md").is_file(), "WebGazer license file is missing", failures)
    require((HERE / "vendor" / "GPLv3.md").is_file(), "GPLv3 text is missing", failures)

    local_scripts = re.findall(r'<script[^>]+src="([^"]+)"', html, flags=re.IGNORECASE)
    require(local_scripts == ["./vendor/webgazer.js", "./app.js"], "HTML has an unpinned or remote script", failures)
    require('id="consent-checkbox" type="checkbox"' in html, "consent checkbox is missing or not opt-in", failures)
    require('id="start-button" type="button" disabled' in html, "start button is not disabled by default", failures)
    require('id="stop-button" type="button"' in html, "stop button is missing", failures)
    require('class="topbar"' in html, "controls are not in the top toolbar", failures)
    require('id="calibration-stage"' in html, "full calibration stage is missing", failures)
    require("connect-src 'self'" in html, "CSP does not allow same-origin bundled resources", failures)
    require("connect-src 'none'" not in html, "CSP blocks WebGazer's same-origin resource loader", failures)

    required_tokens = [
        "window.saveDataAcrossSessions = false",
        ".saveDataAcrossSessions(false)",
        "webgazer.begin()",
        "setGazeListener(onGaze)",
        "recordScreenPosition",
        "webgazer.clearGazeListener()",
        "webgazer.stopVideo()",
        "webgazer.end()",
        "webgazer.clearData()",
        "consentCheckbox.checked",
        "state.calibrated",
    ]
    for token in required_tokens:
        require(token in js, f"required runtime token is missing: {token}", failures)

    forbidden_runtime = re.compile(r"\b(fetch|XMLHttpRequest|sendBeacon|localStorage|sessionStorage)\b")
    require(not forbidden_runtime.search(js), "runtime contains a persistence or network primitive", failures)
    require("https://" not in html and "http://" not in html, "HTML contains a remote runtime URL", failures)
    require("navigator.mediaDevices.getUserMedia" not in js, "adapter bypasses WebGazer consent flow", failures)

    if failures:
        print("CONTRACT_TESTS_INVALID")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print("CONTRACT_TESTS_VALID")
    print("camera_started_by_automation=False")
    print("external_network_used_by_adapter=False")
    print("same_origin_assets_allowed=True")
    print("persistent_samples=False")


if __name__ == "__main__":
    main()
