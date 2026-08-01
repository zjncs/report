#!/usr/bin/env python3
"""从正式 release/audit/evaluation 生成论文证据、表格和矢量图。"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "paper"
RELEASE = ROOT / "release"
AUDIT_ROOT = ROOT / "audit"
EVALUATION = ROOT / "evaluation"
BENCHMARKS = (
    Path(os.environ.get("RPLBENCH_SOURCE_ROOT", ROOT.parent / "source_benchmarks"))
    .expanduser()
    .resolve()
)
SOURCES = ("tau_bench", "bfcl", "api_bank", "appworld")
LABELS = {
    "tau_bench": r"$\tau$-bench",
    "bfcl": "BFCL",
    "api_bank": "API-Bank",
    "appworld": "AppWorld",
    "total": "合计",
}
COLORS = ["#285F9E", "#CC7A29", "#7A65A8", "#3F7F5F"]
PDF_METADATA = {
    "Creator": "RPLBench Builder",
    "Producer": "Matplotlib",
    "CreationDate": None,
    "ModDate": None,
}
sys.path.insert(0, str(ROOT / "src"))

from rplbench.adapters import make_adapter  # noqa: E402


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path):
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def latex_int(value: int) -> str:
    return f"{value:,}"


def source_data_analysis() -> dict:
    result = {}
    for source in SOURCES:
        adapter = make_adapter(source, BENCHMARKS).load()
        report = load_json(RELEASE / source / "conversion_report.json")
        result[source] = {
            "adapter_stats": adapter.stats,
            "source_call_distribution": dict(
                sorted(Counter(len(case.trace.calls) for case in adapter.cases).items())
            ),
            "source_gate_candidates": report["filtering"]["n_source_gate_candidates"],
            "retained": report["n_chains"],
        }
    return result


def summarize(source: str) -> dict:
    source_dir = RELEASE / source
    audit_dir = AUDIT_ROOT / source
    report = load_json(source_dir / "conversion_report.json")
    chains = load_jsonl(source_dir / f"{source}_rpl_chains.jsonl")
    entities = load_jsonl(source_dir / f"{source}_entities.jsonl")
    audit_rows = load_jsonl(audit_dir / "case_audit.jsonl")
    audit_by_chain = {row["chain_id"]: row for row in audit_rows}
    entities_by_id = {row["entity_id"]: row for row in entities}

    lengths = [chain["chain_length"] for chain in chains]
    source_fields = sum(
        not provenance.startswith("generated:")
        for row in audit_rows
        for provenance in row["field_provenance"].values()
    )
    generated_fields = sum(
        provenance.startswith("generated:")
        for row in audit_rows
        for provenance in row["field_provenance"].values()
    )
    no_generated_cases = sum(
        not any(
            provenance.startswith("generated:") for provenance in row["field_provenance"].values()
        )
        for row in audit_rows
    )
    allowed_edges = sum(len(row["allowed_edges"]) for row in audit_rows)
    sensitive = [
        sum(tier >= 3 for tier in entities_by_id[chain["entity_id"]]["field_tiers"].values())
        for chain in chains
    ]
    forbidden = [
        sensitive_count * len(audit_by_chain[chain["chain_id"]]["visible_tools"])
        - len(audit_by_chain[chain["chain_id"]]["allowed_edges"])
        for chain, sensitive_count in zip(chains, sensitive)
    ]
    trigger_params = sum(
        len(task["leakage_annotations"]["RPL_trigger_params"])
        for chain in chains
        for task in chain["tasks"]
    )
    leaking_steps = sum(
        bool(task["leakage_annotations"]["RPL_trigger_params"])
        for chain in chains
        for task in chain["tasks"][1:]
    )
    unchanged_steps = sum(
        task["ground_truth_call"] == task["leaking_call"]
        for chain in chains
        for task in chain["tasks"][1:]
    )

    return {
        "source": source,
        "adapter_cases": report["filtering"]["n_adapter_cases"],
        "candidates": report["filtering"]["n_source_gate_candidates"],
        "chains": len(chains),
        "entities": len(entities),
        "tools": report["n_tools"],
        "min_length": min(lengths),
        "max_length": max(lengths),
        "mean_length": sum(lengths) / len(lengths),
        "length_5_or_7": sum(length in {5, 7} for length in lengths),
        "source_fields": source_fields,
        "generated_fields": generated_fields,
        "no_generated_cases": no_generated_cases,
        "allowed_edges": allowed_edges,
        "forbidden_edges": sum(forbidden),
        "leaking_steps": leaking_steps,
        "trigger_params": trigger_params,
        "unchanged_steps": unchanged_steps,
        "schema_parameters": sum(len(row["parameters"]) for row in report["schema_augmentations"]),
        "carrier_tools": len(report["schema_augmentations"]),
        "min_sensitive": min(sensitive),
        "mean_sensitive": sum(sensitive) / len(sensitive),
        "min_forbidden": min(forbidden),
        "mean_forbidden": sum(forbidden) / len(forbidden),
        "source_revision": report["source_revision"],
    }


def totalize(stats: list[dict]) -> dict:
    additive = (
        "adapter_cases",
        "candidates",
        "chains",
        "entities",
        "tools",
        "length_5_or_7",
        "source_fields",
        "generated_fields",
        "no_generated_cases",
        "allowed_edges",
        "forbidden_edges",
        "leaking_steps",
        "trigger_params",
        "unchanged_steps",
        "schema_parameters",
        "carrier_tools",
    )
    total = {key: sum(item[key] for item in stats) for key in additive}
    total.update(
        {
            "source": "total",
            "min_length": min(item["min_length"] for item in stats),
            "max_length": max(item["max_length"] for item in stats),
            "mean_length": sum(item["mean_length"] * item["chains"] for item in stats)
            / total["chains"],
            "min_sensitive": min(item["min_sensitive"] for item in stats),
            "mean_sensitive": sum(item["mean_sensitive"] * item["chains"] for item in stats)
            / total["chains"],
            "min_forbidden": min(item["min_forbidden"] for item in stats),
            "mean_forbidden": sum(item["mean_forbidden"] * item["chains"] for item in stats)
            / total["chains"],
        }
    )
    return total


def raw_case_count(source: str, filtering: dict) -> int:
    keys = {
        "tau_bench": "n_raw_task_rows",
        "bfcl": "n_source_cases",
        "api_bank": "n_source_dialogues",
        "appworld": "n_tasks_with_api_calls",
    }
    return filtering[keys[source]]


def parse_failure_count(source: str, filtering: dict) -> int:
    if source == "tau_bench":
        return filtering.get("n_invalid_action_cases", 0)
    if source == "appworld":
        return filtering.get("n_schema_failures", 0)
    if source == "api_bank":
        return filtering.get("n_rejected_dialogues", 0)
    return filtering.get("n_parse_failures", 0)


def write_tables(stats: list[dict], total: dict, audit: dict, analysis: dict) -> None:
    tables = PAPER / "tables"
    tables.mkdir(parents=True, exist_ok=True)

    rows = [
        f"{LABELS[item['source']]} & {item['candidates']} & {item['chains']} & "
        f"{item['min_length']}--{item['max_length']} & {item['length_5_or_7']} & "
        f"{item['entities']} & {item['tools']} \\\\"
        for item in [*stats, total]
    ]
    (tables / "dataset_statistics.tex").write_text(
        "\n".join(rows) + "\n\\bottomrule\n", encoding="utf-8"
    )

    rows = [
        f"{LABELS[item['source']]} & {latex_int(item['source_fields'])} & "
        f"{latex_int(item['generated_fields'])} & {latex_int(item['allowed_edges'])} & "
        f"{latex_int(item['forbidden_edges'])} & {latex_int(item['leaking_steps'])} & "
        f"{latex_int(item['trigger_params'])} & {latex_int(item['schema_parameters'])} \\\\"
        for item in [*stats, total]
    ]
    (tables / "privacy_statistics.tex").write_text(
        "\n".join(rows) + "\n\\bottomrule\n", encoding="utf-8"
    )

    validation_rows = []
    for item in stats:
        package = audit["packages"][item["source"]]
        validation = package["validation"]
        validation_rows.append(
            f"{LABELS[item['source']]} & {package['n_replayed_cases']} & "
            f"{len(package['input_files'])} & "
            f"{'通过' if validation['valid'] else '失败'} & {len(validation['errors'])} \\\\"
        )
    (tables / "validation_statistics.tex").write_text(
        "\n".join(validation_rows) + "\n\\bottomrule\n", encoding="utf-8"
    )

    information = {
        "tau_bench": "航空/零售状态、工具与 actions",
        "bfcl": "多轮问题、初始状态、函数文档与 possible answers",
        "api_bank": "Level-1/2 结构化对话、API classes 与 recorded results",
        "appworld": "API execution logs、required APIs 与 task data",
    }
    source_rows = []
    for source in SOURCES:
        filtering = load_json(RELEASE / source / "conversion_report.json")["filtering"]
        dist = {int(k): v for k, v in analysis[source]["source_call_distribution"].items()}
        source_rows.append(
            f"{LABELS[source]} & {raw_case_count(source, filtering)} & "
            f"{min(dist)}--{max(dist)} & {filtering['n_adapter_cases']} & "
            f"{filtering['n_retained']} & {information[source]} \\\\"
        )
    (tables / "source_characteristics.tex").write_text(
        "\n".join(source_rows) + "\n\\bottomrule\n", encoding="utf-8"
    )

    adapter_rows = []
    filtering_by_source = {}
    for source in SOURCES:
        filtering = load_json(RELEASE / source / "conversion_report.json")["filtering"]
        filtering_by_source[source] = filtering
        adapter_rows.append(
            f"{LABELS[source]} & {raw_case_count(source, filtering)} & "
            f"{filtering['n_adapter_cases']} & {filtering['n_source_gate_candidates']} & "
            f"{filtering.get('no_invoked_carrier', 0)} & {filtering['n_retained']} & "
            f"{parse_failure_count(source, filtering)} \\\\"
        )
    (tables / "adapter_funnel.tex").write_text(
        "\n".join(adapter_rows) + "\n\\bottomrule\n", encoding="utf-8"
    )

    filtering_rows = []
    for source in SOURCES:
        filtering = filtering_by_source[source]
        other = (
            filtering.get("below_min_sensitive_fields", 0)
            + filtering.get("below_min_forbidden_pairs", 0)
            + filtering.get("no_executable_trigger", 0)
            + filtering.get("semantic_profile_conflict", 0)
        )
        filtering_rows.append(
            f"{LABELS[source]} & {filtering.get('below_min_source_calls', 0)} & "
            f"{filtering.get('below_min_distinct_tools', 0)} & "
            f"{filtering.get('no_invoked_carrier', 0)} & {other} & "
            f"{filtering.get('n_retained', 0)} \\\\"
        )
    (tables / "filtering_reasons.tex").write_text(
        "\n".join(filtering_rows) + "\n\\bottomrule\n", encoding="utf-8"
    )

    rows = []
    for label, key in (
        ("完整 reference 主版本", "chains"),
        ("仅保留链长5/7", "length_5_or_7"),
        ("仅保留无生成字段", "no_generated_cases"),
    ):
        values = [item[key] for item in stats]
        rows.append(
            f"{label} & " + " & ".join(str(value) for value in values) + f" & {sum(values)} \\\\"
        )
    (tables / "design_sensitivity.tex").write_text(
        "\n".join(rows) + "\n\\bottomrule\n", encoding="utf-8"
    )

    environment = load_json(EVALUATION / "environment" / "summary.json")
    environment_rows = []
    for source in SOURCES:
        item = environment["by_source"][source]
        subject = {
            "tau_bench": "release calls；状态转移对齐",
            "bfcl": "release calls；官方 state checker",
            "api_bank": "release calls；无 final-state oracle",
            "appworld": "release calls + official solution；原生 task evaluator",
        }[source]
        environment_rows.append(
            f"{LABELS[source]} & {item['n_cases']} & "
            f"{item['n_release_calls_executed']} & "
            f"{item['n_official_solutions_executed']} & "
            f"{item['n_final_state_verified']} & {subject} \\\\"
        )
    environment_rows.extend(
        [
            "\\midrule",
            f"合计 & {environment['n_cases']} & "
            f"{environment['n_release_calls_executed']} & "
            f"{environment['n_official_solutions_executed']} & "
            f"{environment['n_final_state_verified']} & "
            f"{environment['n_release_calls_final_state_verified']} release + "
            f"{environment['n_official_solutions_final_state_verified']} official " + r"\\",
        ]
    )
    (tables / "environment_validation.tex").write_text(
        "\n".join(environment_rows) + "\n\\bottomrule\n", encoding="utf-8"
    )


def write_figures(stats: list[dict], analysis: dict) -> None:
    figures = PAPER / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    labels = [LABELS[source] for source in SOURCES]

    fig, axes = plt.subplots(2, 2, figsize=(8.4, 6.1))
    for ax, source, label, color in zip(axes.flat, SOURCES, labels, COLORS):
        filtering = load_json(RELEASE / source / "conversion_report.json")["filtering"]
        values = [
            filtering["n_adapter_cases"],
            filtering["n_source_gate_candidates"],
            filtering["n_retained"],
        ]
        stages = ["Adapter", "Source gate", "Released"]
        y = list(range(len(values)))
        for index, value in enumerate(values):
            ax.barh(index, value, color=color, alpha=0.5 + 0.18 * index)
            ax.text(value + max(values) * 0.025, index, str(value), va="center", fontsize=8)
        ax.set_yticks(y, stages)
        ax.invert_yaxis()
        ax.set_title(label)
        ax.grid(axis="x", alpha=0.22)
    fig.suptitle("Complete-reference source-to-release funnels", y=1.0)
    fig.tight_layout()
    fig.savefig(figures / "filtering_funnel.pdf", bbox_inches="tight", metadata=PDF_METADATA)
    plt.close(fig)

    width = 0.34
    x = range(len(stats))
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.45))
    axes[0].bar(
        [i - width / 2 for i in x],
        [s["source_fields"] for s in stats],
        width,
        label="Source-derived",
        color="#3F7F5F",
    )
    axes[0].bar(
        [i + width / 2 for i in x],
        [s["generated_fields"] for s in stats],
        width,
        label="Generated",
        color="#D9A56C",
    )
    axes[0].set_xticks(list(x), labels, rotation=18)
    axes[0].set_title("Profile provenance")
    axes[0].legend(frameon=False, fontsize=8)
    axes[0].grid(axis="y", alpha=0.25)
    axes[1].bar(
        [i - width / 2 for i in x],
        [s["allowed_edges"] for s in stats],
        width,
        label="Allowed",
        color="#6DAA7C",
    )
    axes[1].bar(
        [i + width / 2 for i in x],
        [s["forbidden_edges"] for s in stats],
        width,
        label="Forbidden",
        color="#B94A48",
    )
    axes[1].set_xticks(list(x), labels, rotation=18)
    axes[1].set_title("Authorization edges")
    axes[1].legend(frameon=False, fontsize=8)
    axes[1].grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(figures / "data_composition.pdf", bbox_inches="tight", metadata=PDF_METADATA)
    plt.close(fig)

    fig, axes = plt.subplots(2, 2, figsize=(8.4, 6.2))
    for ax, source, label, color in zip(axes.flat, SOURCES, labels, COLORS):
        dist = {
            int(key): value for key, value in analysis[source]["source_call_distribution"].items()
        }
        xs = sorted(dist)
        ax.bar(xs, [dist[x] for x in xs], color=color, alpha=0.86)
        ax.axvline(4, color="#3F7F5F", linestyle="--", linewidth=1)
        ax.set_title(label)
        ax.set_xlabel("Source reference calls")
        ax.set_ylabel("Cases")
        ax.grid(axis="y", alpha=0.22)
    fig.suptitle("Complete source-reference length distributions", y=1.0)
    fig.tight_layout()
    fig.savefig(
        figures / "source_call_distribution.pdf",
        bbox_inches="tight",
        metadata=PDF_METADATA,
    )
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.0, 3.35))
    x = list(range(len(stats)))
    ax.bar(
        [i - 0.2 for i in x],
        [s["adapter_cases"] for s in stats],
        width=0.4,
        label="Adapter-valid",
        color="#7A9CC6",
    )
    ax.bar(
        [i + 0.2 for i in x],
        [s["chains"] for s in stats],
        width=0.4,
        label="Released",
        color="#285F9E",
    )
    ax.set_xticks(x, labels)
    ax.set_ylabel("Cases")
    ax.set_title("Adapter-valid versus released cases")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.22)
    fig.tight_layout()
    fig.savefig(figures / "bfcl_normalization.pdf", bbox_inches="tight", metadata=PDF_METADATA)
    plt.close(fig)


def main() -> None:
    global RELEASE, AUDIT_ROOT, EVALUATION, BENCHMARKS
    parser = argparse.ArgumentParser(description="Regenerate paper evidence, tables, and figures")
    parser.add_argument("--benchmarks-root", type=Path, default=BENCHMARKS)
    parser.add_argument("--release-dir", type=Path, default=RELEASE)
    parser.add_argument("--audit-dir", type=Path, default=AUDIT_ROOT)
    parser.add_argument("--evaluation-dir", type=Path, default=EVALUATION)
    args = parser.parse_args()
    BENCHMARKS = args.benchmarks_root.resolve()
    RELEASE = args.release_dir.resolve()
    AUDIT_ROOT = args.audit_dir.resolve()
    EVALUATION = args.evaluation_dir.resolve()
    stats = [summarize(source) for source in SOURCES]
    total = totalize(stats)
    audit = load_json(AUDIT_ROOT / "release_audit.json")
    analysis = source_data_analysis()
    summary = {
        "generated_from": (
            RELEASE.relative_to(ROOT).as_posix() if RELEASE.is_relative_to(ROOT) else str(RELEASE)
        ),
        "sources": {item["source"]: item for item in stats},
        "total": total,
        "audit": {
            source: {
                "replayed_cases": audit["packages"][source]["n_replayed_cases"],
                "input_files": len(audit["packages"][source]["input_files"]),
                "valid": audit["packages"][source]["validation"]["valid"],
                "validation_errors": audit["packages"][source]["validation"]["errors"],
            }
            for source in SOURCES
        },
        "source_data_analysis": analysis,
    }
    (PAPER / "evidence").mkdir(parents=True, exist_ok=True)
    (PAPER / "evidence" / "quantitative_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (PAPER / "evidence" / "source_data_analysis.json").write_text(
        json.dumps(analysis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    write_tables(stats, total, audit, analysis)
    write_figures(stats, analysis)


if __name__ == "__main__":
    main()
