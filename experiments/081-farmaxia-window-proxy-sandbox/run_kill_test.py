"""Adversarial checks for ambiguity in graphical proxy transformations."""

from __future__ import annotations

from proxy_math import DEFAULT_PERMUTATION, QuadrantPermutation


def main() -> None:
    for candidate in ((0, 1, 2, 2), (0, 1, 2, 3, 4), (-1, 1, 2, 3)):
        try:
            QuadrantPermutation(candidate)
        except ValueError:
            continue
        raise AssertionError(f"ambiguous transform accepted: {candidate}")

    for point in ((-1, 0), (0, -1), (320, 0), (0, 320)):
        try:
            DEFAULT_PERMUTATION.proxy_to_source(*point, 320)
        except ValueError:
            continue
        raise AssertionError(f"out-of-surface point accepted: {point}")
    print("FARMAXIA_081_WINDOW_PROXY_KILL_TESTS_VALID")


if __name__ == "__main__":
    main()
