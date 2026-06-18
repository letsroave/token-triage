#!/usr/bin/env python3
"""Compare baseline vs triaged token spend.

Use this after a Token Triage pass to show estimated tokens saved, percentage
saved, and optional dollar savings when model pricing is supplied.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from estimate_context import estimate_file, format_int, iter_files


@dataclass(frozen=True)
class TokenSpend:
    label: str
    input_tokens: int
    output_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


def estimate_paths(paths: list[Path], include_patterns: tuple[str, ...], extra_excludes: tuple[str, ...]) -> int:
    estimates = [
        estimate
        for estimate in (
            estimate_file(path)
            for path in iter_files(paths, include_patterns, extra_excludes)
        )
        if estimate is not None
    ]
    return sum(item.tokens for item in estimates)


def resolve_input_tokens(
    manual_tokens: int | None,
    paths: list[Path] | None,
    include_patterns: tuple[str, ...],
    extra_excludes: tuple[str, ...],
    label: str,
) -> int:
    if manual_tokens is not None and paths:
        raise ValueError(f"Use either --{label}-tokens or --{label}, not both.")
    if manual_tokens is not None:
        return manual_tokens
    if paths:
        return estimate_paths(paths, include_patterns, extra_excludes)
    raise ValueError(f"Provide --{label}-tokens or --{label}.")


def cost_usd(input_tokens: int, output_tokens: int, input_price: float | None, output_price: float | None) -> float | None:
    if input_price is None and output_price is None:
        return None
    input_cost = (input_tokens / 1_000_000) * (input_price or 0.0)
    output_cost = (output_tokens / 1_000_000) * (output_price or 0.0)
    return input_cost + output_cost


def pct_saved(baseline: int, saved: int) -> float:
    if baseline <= 0:
        return 0.0
    return (saved / baseline) * 100


def print_report(
    baseline: TokenSpend,
    triaged: TokenSpend,
    runs: int,
    input_price: float | None,
    output_price: float | None,
) -> None:
    input_delta = baseline.input_tokens - triaged.input_tokens
    output_delta = baseline.output_tokens - triaged.output_tokens
    total_delta = baseline.total_tokens - triaged.total_tokens
    repeated_delta = total_delta * runs
    delta_label = "Saved" if total_delta >= 0 else "Extra spent"

    print("Token savings calculator")
    print(f"- Baseline input tokens: {format_int(baseline.input_tokens)}")
    print(f"- Triaged input tokens: {format_int(triaged.input_tokens)}")
    if baseline.output_tokens or triaged.output_tokens:
        print(f"- Baseline output tokens: {format_int(baseline.output_tokens)}")
        print(f"- Triaged output tokens: {format_int(triaged.output_tokens)}")
    print(
        f"- {delta_label} per run: {format_int(abs(total_delta))} tokens "
        f"({pct_saved(baseline.total_tokens, total_delta):.1f}%)"
    )
    print(f"- {delta_label} across {format_int(runs)} run(s): {format_int(abs(repeated_delta))} tokens")

    baseline_cost = cost_usd(baseline.input_tokens, baseline.output_tokens, input_price, output_price)
    triaged_cost = cost_usd(triaged.input_tokens, triaged.output_tokens, input_price, output_price)
    if baseline_cost is None or triaged_cost is None:
        print("- Cost saved: provide --input-price-per-1m and/or --output-price-per-1m to estimate dollars")
        return

    saved_cost = baseline_cost - triaged_cost
    cost_label = "Cost saved" if saved_cost >= 0 else "Extra cost"
    print(f"- Baseline cost per run: ${baseline_cost:.6f}")
    print(f"- Triaged cost per run: ${triaged_cost:.6f}")
    print(f"- {cost_label} per run: ${abs(saved_cost):.6f}")
    print(f"- {cost_label} across {format_int(runs)} run(s): ${abs(saved_cost * runs):.6f}")
    if input_delta or output_delta:
        print(f"- Input/output delta: {format_int(input_delta)} input, {format_int(output_delta)} output")


def non_negative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("value must be non-negative")
    return parsed


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be greater than zero")
    return parsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Calculate estimated token and optional cost savings from Token Triage."
    )
    parser.add_argument("--baseline", nargs="+", type=Path, help="Baseline paths, such as the whole repo or raw docs.")
    parser.add_argument("--actual", nargs="+", type=Path, help="Triaged paths actually read or planned.")
    parser.add_argument("--baseline-tokens", type=non_negative_int, help="Manual baseline input token estimate.")
    parser.add_argument("--actual-tokens", type=non_negative_int, help="Manual triaged input token estimate.")
    parser.add_argument("--baseline-output-tokens", type=non_negative_int, default=0, help="Manual baseline output tokens.")
    parser.add_argument("--actual-output-tokens", type=non_negative_int, default=0, help="Manual triaged output tokens.")
    parser.add_argument("--runs", type=positive_int, default=1, help="How many repeated runs/sessions to project.")
    parser.add_argument("--input-price-per-1m", type=float, help="Input token price in USD per 1M tokens.")
    parser.add_argument("--output-price-per-1m", type=float, help="Output token price in USD per 1M tokens.")
    parser.add_argument("--include", action="append", default=[], help="Include glob pattern for path estimates; may repeat.")
    parser.add_argument("--exclude", action="append", default=[], help="Extra exclude pattern or path fragment; may repeat.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        baseline_input = resolve_input_tokens(
            args.baseline_tokens,
            args.baseline,
            tuple(args.include),
            tuple(args.exclude),
            "baseline",
        )
        actual_input = resolve_input_tokens(
            args.actual_tokens,
            args.actual,
            tuple(args.include),
            tuple(args.exclude),
            "actual",
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    baseline = TokenSpend(
        label="baseline",
        input_tokens=baseline_input,
        output_tokens=args.baseline_output_tokens,
    )
    triaged = TokenSpend(
        label="triaged",
        input_tokens=actual_input,
        output_tokens=args.actual_output_tokens,
    )
    print_report(
        baseline=baseline,
        triaged=triaged,
        runs=args.runs,
        input_price=args.input_price_per_1m,
        output_price=args.output_price_per_1m,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
