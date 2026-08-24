"""Compare X-ANA-X against direct reformulation on the suite's real source."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).parent
ROOT = HERE.parents[1]
TARGET = ROOT / "research" / "tools" / "run_suite.py"
SOURCE_CARD = HERE / "source_card.json"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest().upper()


def is_returncode_inequality(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Compare)
        and len(node.ops) == 1
        and isinstance(node.ops[0], ast.NotEq)
        and isinstance(node.left, ast.Attribute)
        and node.left.attr == "returncode"
        and any(isinstance(comparator, ast.Constant) and comparator.value == 0 for comparator in node.comparators)
    )


def has_raise(body: list[ast.stmt]) -> bool:
    return any(isinstance(node, (ast.Raise, ast.Return)) for statement in body for node in ast.walk(statement))


def analyze_source(text: str) -> dict[str, Any]:
    tree = ast.parse(text)
    command_function = next(
        (node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "command"),
        None,
    )
    if command_function is None:
        raise ValueError("command function is missing")
    wrapper_guards = [
        node
        for node in ast.walk(command_function)
        if isinstance(node, ast.If) and is_returncode_inequality(node.test) and has_raise(node.body)
    ]
    direct_guards = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.If) and is_returncode_inequality(node.test) and has_raise(node.body)
    ]
    terminal_markers = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "print"
        and any(isinstance(argument, ast.Constant) and argument.value == "SUITE_VALID" for argument in node.args)
    ]
    terminal_line = min((node.lineno for node in terminal_markers), default=None)
    guard_lines = [node.lineno for node in direct_guards]
    return {
        "wrapper_failure_guard": bool(wrapper_guards),
        "returncode_guard_count": len(direct_guards),
        "terminal_marker_present": bool(terminal_markers),
        "terminal_line": terminal_line,
        "guards_before_terminal": terminal_line is not None and all(line < terminal_line for line in guard_lines),
        "suite_release_condition": bool(wrapper_guards) and bool(terminal_markers),
    }


def direct_route(facts: dict[str, Any]) -> dict[str, Any]:
    return {
        "route": "direct-reformulation",
        "question": "what protects SUITE_VALID from a failed reusable command",
        "facts": facts,
        "decision": "terminal_requires_failure_guard" if facts["suite_release_condition"] else "unprotected",
    }


def analogy_route(facts: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    predicted = bool(facts["wrapper_failure_guard"] and facts["terminal_marker_present"])
    return {
        "route": "x-ana-x",
        "source": source["id"],
        "mapping": source["mapping"],
        "prediction": source["prediction"],
        "predicted_decision": "terminal_requires_failure_guard" if predicted else "unprotected",
        "facts_used": facts,
    }


def main() -> None:
    text = TARGET.read_text(encoding="utf-8")
    source = json.loads(SOURCE_CARD.read_text(encoding="utf-8"))
    facts = analyze_source(text)
    direct = direct_route(facts)
    analogy = analogy_route(facts, source)
    comparison = {
        "same_facts": direct["facts"] == analogy["facts_used"],
        "same_decision": direct["decision"] == analogy["predicted_decision"],
        "unique_analogy_decision": direct["decision"] != analogy["predicted_decision"],
        "novelty_status": "not_demonstrated",
        "residue": "source vocabulary and mapping are additional description, not additional target evidence",
    }
    print(
        json.dumps(
            {
                "experiment": "018-xanax-reformulation-control",
                "target": "research/tools/run_suite.py",
                "target_sha256": sha256_text(text),
                "direct_route": direct,
                "analogy_route": analogy,
                "comparison": comparison,
                "human_data": False,
                "network_used": False,
                "arbitrary_corpus": False,
                "scope_limit": "static source comparison; no human comprehension or analogy efficacy claim",
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
