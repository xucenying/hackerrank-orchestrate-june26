"""
evaluation/main.py — Evaluation entry point.

Runs the verification pipeline against dataset/sample_claims.csv
(which includes expected labels) and reports accuracy metrics.
"""

import asyncio
import pathlib
import textwrap

import pandas as pd

from code.config import SAMPLE_CLAIMS_CSV
from code.main import run_pipeline

EVAL_DIR = pathlib.Path(__file__).parent
EVAL_OUTPUT_CSV = EVAL_DIR / "eval_output.csv"
REPORT_PATH = EVAL_DIR / "evaluation_report.md"

EVAL_FIELDS = [
    "claim_status",
    "evidence_standard_met",
    "valid_image",
    "severity",
    "issue_type",
]

INPUT_COLUMNS = ["user_id", "image_paths", "user_claim", "claim_object"]


def _normalize(value) -> str:
    """Lowercase + strip so 'True'/'true'/True all compare equal."""
    return str(value).strip().lower()


def compute_metrics(expected: pd.DataFrame, predicted: pd.DataFrame) -> dict:
    metrics = {}
    for field in EVAL_FIELDS:
        exp = expected[field].map(_normalize)
        pred = predicted[field].map(_normalize)
        metrics[field] = (exp == pred).mean()
    metrics["OVERALL"] = sum(metrics.values()) / len(EVAL_FIELDS)
    return metrics


def print_table(metrics: dict) -> None:
    print(f"\n{'Field':<28} {'Accuracy':>8}")
    print("-" * 38)
    for field, acc in metrics.items():
        print(f"{field:<28} {acc:>8.2f}")
    print()


def write_report(metrics: dict) -> None:
    rows = "\n".join(f"| {field:<26} | {acc:.2f}   |" for field, acc in metrics.items())
    report = textwrap.dedent(f"""\
        # Evaluation Report

        ## Results

        | Field                      | Accuracy |
        |----------------------------|----------|
        {rows}

        ## Strategy used

        Each claim is processed by a four-agent pipeline:

        1. **context_builder** — fetches user history and evidence requirements from CSV.
        2. **image_analyst** — sends claim images to `claude-sonnet-4-6` (vision) with a
           structured prompt; returns `valid_image`, `issue_type`, `object_part`, `severity`,
           `supporting_image_ids`, `evidence_standard_met`, and `evidence_standard_met_reason`.
        3. **claim_verifier** — text-only call to `claude-sonnet-4-6`; compares the user
           transcript against the image analysis to decide `claim_status` and
           `claim_status_justification`.
        4. **risk_scorer** — text-only call to `claude-sonnet-4-6`; cross-references user
           history and image analysis to produce `risk_flags`.

        Steps 3 and 4 run concurrently via `asyncio.gather`. Up to
        `MAX_CONCURRENT_CLAIMS` claims are processed in parallel via an `asyncio.Semaphore`.

        ## Operational analysis

        | Metric            | Value                        |
        |-------------------|------------------------------|
        | Model             | claude-sonnet-4-6            |
        | Calls per claim   | 3 (1 vision + 2 text)        |
        | Image count       | _TBD — varies per claim_     |
        | Token usage       | _TBD — measure with SDK_     |
        | Cost estimate     | _TBD — calculate after run_  |
        | Latency (p50)     | _TBD_                        |
        | TPM / RPM notes   | Semaphore limits concurrency; increase `MAX_CONCURRENT_CLAIMS` carefully to stay within rate limits |

        ## What to improve next

        - **Prompt tuning**: tighten `severity` vocabulary to match expected labels
          (e.g. the sample data uses `"medium"` while the prompt emits `"moderate"`).
        - **Evidence requirements**: pass structured requirements as a typed list rather
          than a raw string so the model can reason over them more precisely.
        - **Retry / backoff**: add exponential backoff on rate-limit errors instead of
          falling back to the safe-default row immediately.
        - **Caching**: cache `build_context` results; CSV reads are cheap but avoidable
          when processing many claims in one run.
        - **Confidence scores**: extend JSON schema to include a confidence field per
          output so borderline cases can be flagged for human review automatically.
    """)

    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"Report written to {REPORT_PATH}")


async def evaluate() -> None:
    df = pd.read_csv(SAMPLE_CLAIMS_CSV)

    # Strip expected outputs so the pipeline only sees inputs
    input_df = df[INPUT_COLUMNS].copy()
    input_csv = EVAL_DIR / "eval_input.csv"
    input_df.to_csv(input_csv, index=False)

    await run_pipeline(input_csv, EVAL_OUTPUT_CSV)

    predicted = pd.read_csv(EVAL_OUTPUT_CSV)
    metrics = compute_metrics(df, predicted)

    print_table(metrics)
    write_report(metrics)


if __name__ == "__main__":
    asyncio.run(evaluate())
