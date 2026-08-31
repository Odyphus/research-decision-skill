#!/usr/bin/env python3
"""Deterministic, dependency-free state helpers for research-decision-skill.

The state file deliberately uses JSON syntax with a .yaml suffix. JSON is a
strict subset of YAML, so the file remains JSON-compatible YAML without adding
a PyYAML runtime dependency.
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, Sequence


SCHEMA_VERSION = 3
SKILL_VERSION = "0.5.0-preview"
SUPPORTED_SKILL_VERSIONS = frozenset(
    {"0.3.0-preview", "0.4.0-preview", SKILL_VERSION}
)
STATE_DIR_NAME = ".research-decision"
LEGACY_STATE_DIR_NAME = ".research-exploration"
STATE_FILE_NAME = "research-state.yaml"
TRACE_FILE_NAME = "decision-trace.md"
EVIDENCE_FILE_NAME = "evidence-ledger.md"
QUESTIONS_FILE_NAME = "open-questions.md"
EXPERT_FILE_NAME = "expert-experience-ledger.md"
LEARNING_FILE_NAME = "learning-ledger.md"

DECISION_STATUSES = {
    "open",
    "provisional",
    "accepted",
    "rejected",
    "blocked",
    "reopened",
    "superseded",
}
CONFIDENCE_LEVELS = {"low", "medium", "high"}
DECISION_RECORD_FIELDS = (
    "decision_record_id",
    "decision_id",
    "decision_label",
    "status",
    "research_context",
    "question",
    "alternatives",
    "current_choice",
    "evidence_for",
    "evidence_against",
    "missing_evidence",
    "constraints",
    "uncertainty",
    "confidence",
    "rationale",
    "next_high_information_action",
    "revisit_condition",
    "stop_or_pivot_condition",
    "source_refs",
    "domain",
    "search_run_ids",
    "expert_judgment_ids",
    "user_initial_judgment",
    "expert_comparison_feedback",
    "user_revised_decision",
    "transferable_principles",
    "decision_support",
    "explanation_support",
    "learning_record_ids",
    "supersedes",
    "created_at",
    "updated_at",
)
STATE_FIELDS = (
    "schema_version",
    "state_revision",
    "skill_version",
    "project",
    "research_goal",
    "scope",
    "constraints",
    "permissions",
    "claims",
    "hypotheses",
    "experiments",
    "evidence_index",
    "domain",
    "search_runs",
    "expert_judgment_index",
    "learning_record_index",
    "current_route",
    "open_questions",
    "revisit_queue",
    "created_at",
    "updated_at",
)
ROUTER_FIELDS = (
    "primary_decision",
    "secondary_decisions",
    "why_now",
    "evidence_used",
    "unknowns",
    "confidence",
    "next_method_module",
)
METHOD_MODULES = {
    "literature_novelty",
    "hypothesis_predictive_framework",
    "experiment_design",
    "ai_ml_evidence_integrity",
    "analysis_anomaly",
    "challenge_try_to_break",
    "claims_implications_communication",
}
EVIDENCE_FIELDS = (
    "evidence_id",
    "usage_ids",
    "claim_ids",
    "canonical_work_id",
    "artifact_id",
    "study_id",
    "aliases",
    "source_identity",
    "relationship",
    "independence_status",
    "independence_basis",
    "relation",
    "location",
    "access_status",
    "verification_status",
    "license_status",
    "limitations",
    "checked_at",
    "notes",
)
OPEN_QUESTION_FIELDS = (
    "question_id",
    "question",
    "decision_id",
    "blocking",
    "next_information_action",
    "revisit_condition",
    "status",
)
SEARCH_RUN_FIELDS = (
    "record_type",
    "search_run_id",
    "decision_record_id",
    "decision_id",
    "domain",
    "research_task",
    "search_question",
    "decision_claim_ids",
    "constraints",
    "inclusion_criteria",
    "exclusion_criteria",
    "queries",
    "source_evidence_ids",
    "coverage",
    "conflicts",
    "support_scope",
    "single_authority_exception",
    "stopping_reason",
    "searched_at",
)
EXPERT_JUDGMENT_FIELDS = (
    "record_type",
    "expert_judgment_id",
    "search_run_id",
    "decision_id",
    "source_evidence_ids",
    "support_locators",
    "expert_identity",
    "expertise_basis",
    "cues",
    "options",
    "judgment",
    "rationale",
    "predictions",
    "tradeoffs",
    "failure_signals",
    "applicability_conditions",
    "limitations",
    "disagreement_status",
    "extracted_at",
)
LEARNING_RECORD_FIELDS = (
    "record_type",
    "learning_record_id",
    "decision_record_id",
    "decision_id",
    "domain",
    "scaffolding_level",
    "activation_reasons",
    "demonstrated_cues",
    "understanding_status",
    "transfer_status",
    "observed_gaps",
    "misconceptions",
    "next_scaffolding_level",
    "recorded_at",
)
DOMAIN_FIELDS = ("name", "support_status")
DOMAIN_SUPPORT_STATUSES = {
    "public_source_decision_support_preview",
    "decision_framework_only",
    "domain_judgment_unavailable",
}
ACTION_STATUSES = {"可直接推进", "验证后推进", "暂缓定论"}
STEM_DOMAINS = {
    "ai_ml",
    "mathematics_statistics",
    "computer_science",
    "physics_astronomy",
    "chemistry_materials",
    "engineering",
    "life_sciences",
    "earth_environmental_sciences",
    "stem_interdisciplinary",
}
ALL_DOMAINS = STEM_DOMAINS | {"other"}
SCAFFOLDING_LEVELS = ("full", "guided", "faded", "verification_only")
UNDERSTANDING_STATUSES = {
    "not_observed",
    "partial",
    "demonstrated",
    "misconception_detected",
    "declined",
}
TRANSFER_STATUSES = {
    "not_observed",
    "partial",
    "demonstrated",
    "not_demonstrated",
    "declined",
}
DECISION_ID_RE = re.compile(r"^D(?:[1-9]|1[0-9]|2[0-9])$")
SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
PROJECT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

TRACE_HEADER = (
    "# Decision Trace\n\n"
    "Schema version: 3\n\n"
    "Records are append-only. Each heading is followed by exactly one strict "
    "JSON object in a json fence.\n"
)
EVIDENCE_HEADER = (
    "# Evidence Ledger\n\n"
    "Schema version: 3\n\n"
    "Trace cites evidence_id. Keep usage, claim, canonical work, artifact, "
    "study, alias, relationship, and claim-specific independence identities "
    "separate.\n"
)
QUESTIONS_HEADER = (
    "# Open Questions\n\n"
    "Schema version: 3\n\n"
    "Track the associated decision, whether the question blocks progress, the "
    "next information action, and the revisit condition.\n"
)
EXPERT_HEADER = (
    "# Expert Experience Ledger\n\n"
    "Schema version: 3\n\n"
    "Records are append-only search runs and source-grounded expert judgments. "
    "Historical records may guide later queries but never replace current verification.\n\n"
    "Create an `expert_judgment` only when its exact `support_locators` expose at "
    "least one observable decision basis: decision criteria, design rationale, "
    "recommendation, discriminating prediction, tradeoff, or failure signal. In "
    "`expertise_basis`, name that source-exposed basis and why it fits this decision; "
    "reputation, affiliation, citation count, or a merely related result is not enough.\n"
)
LEARNING_HEADER = (
    "# Learning Ledger\n\n"
    "Schema version: 3\n\n"
    "Records are append-only observations of explanation support, demonstrated "
    "understanding, transfer, misconceptions, and the next support level. "
    "Silence or skipped checks must remain not_observed.\n"
)

LEGACY_STATE_FIELDS = tuple(
    field
    for field in STATE_FIELDS
    if field
    not in {"domain", "search_runs", "expert_judgment_index", "learning_record_index"}
)
LEGACY_DECISION_RECORD_FIELDS = tuple(
    field
    for field in DECISION_RECORD_FIELDS
    if field
    not in {
        "domain",
        "search_run_ids",
        "expert_judgment_ids",
        "user_initial_judgment",
        "expert_comparison_feedback",
        "user_revised_decision",
        "transferable_principles",
        "decision_support",
        "explanation_support",
        "learning_record_ids",
    }
)
LEGACY_EVIDENCE_FIELDS = tuple(
    field for field in EVIDENCE_FIELDS if field != "source_identity"
)
LEGACY_TRACE_HEADER = TRACE_HEADER.replace("Schema version: 3", "Schema version: 1")
LEGACY_EVIDENCE_HEADER = EVIDENCE_HEADER.replace("Schema version: 3", "Schema version: 1")
LEGACY_QUESTIONS_HEADER = QUESTIONS_HEADER.replace("Schema version: 3", "Schema version: 1")

_UNSET = object()


class ResearchStateError(Exception):
    """Base class for deterministic state errors."""

    reason_code = "state_error"


class ValidationError(ResearchStateError):
    reason_code = "validation_failed"


class UnsupportedSchemaError(ResearchStateError):
    reason_code = "unsupported_schema"


class CorruptStateError(ResearchStateError):
    reason_code = "corrupt_state"


class ConcurrentModificationError(ResearchStateError):
    reason_code = "concurrent_modification"


class ReadOnlyStateError(ResearchStateError):
    reason_code = "read_only"


class DuplicateRecordError(ResearchStateError):
    reason_code = "duplicate_record"


class PartialCommitError(ResearchStateError):
    reason_code = "partial_commit"

    def __init__(self, message: str, files_changed: Sequence[str]) -> None:
        super().__init__(message)
        self.files_changed = list(files_changed)


def _resolve_state_dir(project_root: str | Path) -> Path:
    """Use the renamed state directory, while preserving existing Preview history."""

    root = Path(project_root).resolve()
    current = root / STATE_DIR_NAME
    legacy = root / LEGACY_STATE_DIR_NAME
    if _path_exists(current) and _path_exists(legacy):
        raise ValidationError(
            f"both {STATE_DIR_NAME} and {LEGACY_STATE_DIR_NAME} exist; "
            "refusing to guess which history is authoritative"
        )
    if _path_exists(current):
        return current
    if _path_exists(legacy):
        return legacy
    return current


def utc_now() -> str:
    """Return a stable RFC 3339 UTC timestamp without fractional seconds."""

    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant is not allowed: {value}")


def _object_without_duplicate_keys(pairs: Sequence[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def strict_json_loads(text: str, *, context: str) -> Any:
    try:
        return json.loads(
            text,
            object_pairs_hook=_object_without_duplicate_keys,
            parse_constant=_reject_constant,
        )
    except (json.JSONDecodeError, ValueError) as exc:
        raise CorruptStateError(f"{context} is not strict JSON: {exc}") from exc


def canonical_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _native_fs_path(path: str | Path) -> str:
    """Return a Windows extended-length path without changing other platforms."""

    value = os.path.abspath(os.fspath(path))
    extended_prefix = os.sep * 2 + "?" + os.sep
    if os.name != "nt" or value.startswith(extended_prefix):
        return value
    if value.startswith(os.sep * 2):
        return extended_prefix + "UNC" + os.sep + value[2:]
    return extended_prefix + value


def _path_exists(path: str | Path) -> bool:
    return os.path.exists(_native_fs_path(path))


def _path_is_file(path: str | Path) -> bool:
    return os.path.isfile(_native_fs_path(path))


def sha256_file(path: Path) -> str:
    with open(_native_fs_path(path), "rb") as handle:
        return sha256_bytes(handle.read())


def _require_expected_sha256(value: Any, context: str) -> str:
    if value is None:
        raise ValidationError(f"{context} is required; no files were changed")
    if not isinstance(value, str) or re.fullmatch(r"[0-9A-Fa-f]{64}", value) is None:
        raise ValidationError(f"{context} must be a 64-character SHA-256 digest")
    return value.lower()


def _require_exact_keys(value: Mapping[str, Any], expected: Iterable[str], context: str) -> None:
    expected_set = set(expected)
    actual_set = set(value)
    missing = sorted(expected_set - actual_set)
    extra = sorted(actual_set - expected_set)
    if missing or extra:
        parts = []
        if missing:
            parts.append(f"missing={missing}")
        if extra:
            parts.append(f"extra={extra}")
        raise ValidationError(f"{context} has invalid fields: {', '.join(parts)}")


def _require_string(value: Any, context: str, *, nonempty: bool = False) -> str:
    if not isinstance(value, str):
        raise ValidationError(f"{context} must be a string")
    if nonempty and not value.strip():
        raise ValidationError(f"{context} must not be empty")
    return value


def _require_string_list(
    value: Any,
    context: str,
    *,
    nonempty_items: bool = False,
    unique: bool = True,
) -> list[str]:
    if not isinstance(value, list):
        raise ValidationError(f"{context} must be an array")
    result = []
    for index, item in enumerate(value):
        result.append(_require_string(item, f"{context}[{index}]", nonempty=nonempty_items))
    if unique and len(set(result)) != len(result):
        raise ValidationError(f"{context} must not contain duplicates")
    return result


def _parse_timestamp(value: Any, context: str) -> dt.datetime:
    raw = _require_string(value, context, nonempty=True)
    normalized = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
    try:
        parsed = dt.datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValidationError(f"{context} must be an RFC 3339 timestamp") from exc
    if parsed.tzinfo is None:
        raise ValidationError(f"{context} must include a timezone")
    return parsed.astimezone(dt.timezone.utc)


def _validate_decision_id(value: Any, context: str) -> str:
    decision_id = _require_string(value, context, nonempty=True)
    if not DECISION_ID_RE.fullmatch(decision_id):
        raise ValidationError(f"{context} must be D1 through D29")
    return decision_id


def validate_domain(value: Any, context: str = "domain") -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"{context} must be an object")
    _require_exact_keys(value, DOMAIN_FIELDS, context)
    name = _require_string(value["name"], f"{context}.name", nonempty=True)
    if name not in ALL_DOMAINS:
        raise ValidationError(f"{context}.name is invalid")
    status = value["support_status"]
    if status not in DOMAIN_SUPPORT_STATUSES:
        raise ValidationError(f"{context}.support_status is invalid")
    expected = (
        "public_source_decision_support_preview"
        if name in STEM_DOMAINS
        else "domain_judgment_unavailable"
    )
    if status != expected:
        raise ValidationError(
            f"{context}.support_status must be {expected!r} for domain {name!r}"
        )
    return value


def validate_search_run(record: Any, context: str = "search run") -> dict[str, Any]:
    if not isinstance(record, dict):
        raise ValidationError(f"{context} must be an object")
    _require_exact_keys(record, SEARCH_RUN_FIELDS, context)
    if record["record_type"] != "search_run":
        raise ValidationError(f"{context}.record_type must be search_run")
    record_id = _require_string(
        record["search_run_id"], f"{context}.search_run_id", nonempty=True
    )
    if not SAFE_ID_RE.fullmatch(record_id):
        raise ValidationError(f"{context}.search_run_id contains unsupported characters")
    decision_record_id = _require_string(
        record["decision_record_id"],
        f"{context}.decision_record_id",
        nonempty=True,
    )
    if not SAFE_ID_RE.fullmatch(decision_record_id):
        raise ValidationError(
            f"{context}.decision_record_id contains unsupported characters"
        )
    _validate_decision_id(record["decision_id"], f"{context}.decision_id")
    validate_domain(record["domain"], f"{context}.domain")
    _require_string(record["research_task"], f"{context}.research_task", nonempty=True)
    _require_string(record["search_question"], f"{context}.search_question", nonempty=True)
    _require_string_list(
        record["decision_claim_ids"],
        f"{context}.decision_claim_ids",
        nonempty_items=True,
    )
    for key in (
        "constraints",
        "inclusion_criteria",
        "exclusion_criteria",
        "queries",
        "source_evidence_ids",
        "conflicts",
    ):
        _require_string_list(
            record[key], f"{context}.{key}", nonempty_items=True
        )
    if not record["queries"]:
        raise ValidationError(f"{context}.queries must contain at least one query")
    if record["coverage"] not in {"sufficient", "partial", "insufficient", "blocked"}:
        raise ValidationError(f"{context}.coverage is invalid")
    if record["coverage"] in {"sufficient", "partial"} and not record["source_evidence_ids"]:
        raise ValidationError(
            f"{context}.coverage={record['coverage']} requires at least one source"
        )
    _require_string(record["support_scope"], f"{context}.support_scope", nonempty=True)
    authority_exception = record["single_authority_exception"]
    if not isinstance(authority_exception, dict):
        raise ValidationError(
            f"{context}.single_authority_exception must be an object"
        )
    _require_exact_keys(
        authority_exception,
        (
            "applied",
            "authority_kind",
            "issuer",
            "scope_match",
            "locator",
            "basis",
        ),
        f"{context}.single_authority_exception",
    )
    if not isinstance(authority_exception["applied"], bool):
        raise ValidationError(
            f"{context}.single_authority_exception.applied must be a boolean"
        )
    if authority_exception["authority_kind"] not in {
        "none",
        "official_standard",
        "regulatory_guidance",
    }:
        raise ValidationError(
            f"{context}.single_authority_exception.authority_kind is invalid"
        )
    for key in ("issuer", "scope_match", "locator"):
        _require_string(
            authority_exception[key],
            f"{context}.single_authority_exception.{key}",
            nonempty=authority_exception["applied"],
        )
    _require_string(
        authority_exception["basis"],
        f"{context}.single_authority_exception.basis",
        nonempty=authority_exception["applied"],
    )
    if authority_exception["applied"] and authority_exception["authority_kind"] == "none":
        raise ValidationError(
            f"{context}.single_authority_exception requires a controlling authority kind"
        )
    if not authority_exception["applied"] and authority_exception["authority_kind"] != "none":
        raise ValidationError(
            f"{context}.single_authority_exception authority_kind must be none when unused"
        )
    _require_string(record["stopping_reason"], f"{context}.stopping_reason", nonempty=True)
    _parse_timestamp(record["searched_at"], f"{context}.searched_at")
    if (
        record["domain"]["support_status"]
        != "public_source_decision_support_preview"
        and record["source_evidence_ids"]
    ):
        raise ValidationError(
            f"{context} cannot record domain judgments without a supported domain pack"
        )
    return record


def validate_expert_judgment(
    record: Any,
    context: str = "expert judgment",
) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise ValidationError(f"{context} must be an object")
    _require_exact_keys(record, EXPERT_JUDGMENT_FIELDS, context)
    if record["record_type"] != "expert_judgment":
        raise ValidationError(f"{context}.record_type must be expert_judgment")
    record_id = _require_string(
        record["expert_judgment_id"],
        f"{context}.expert_judgment_id",
        nonempty=True,
    )
    if not SAFE_ID_RE.fullmatch(record_id):
        raise ValidationError(
            f"{context}.expert_judgment_id contains unsupported characters"
        )
    search_run_id = _require_string(
        record["search_run_id"], f"{context}.search_run_id", nonempty=True
    )
    if not SAFE_ID_RE.fullmatch(search_run_id):
        raise ValidationError(f"{context}.search_run_id contains unsupported characters")
    _validate_decision_id(record["decision_id"], f"{context}.decision_id")
    source_ids = _require_string_list(
        record["source_evidence_ids"],
        f"{context}.source_evidence_ids",
        nonempty_items=True,
    )
    if not source_ids:
        raise ValidationError(
            f"{context}.source_evidence_ids must contain at least one verified source"
        )
    if len(source_ids) != 1:
        raise ValidationError(
            f"{context}.source_evidence_ids must contain exactly one canonical perspective"
        )
    support_locators = record["support_locators"]
    if not isinstance(support_locators, dict):
        raise ValidationError(f"{context}.support_locators must be an object")
    if set(support_locators) != set(source_ids):
        raise ValidationError(
            f"{context}.support_locators keys must exactly equal source_evidence_ids"
        )
    for evidence_id, locator in support_locators.items():
        _require_string(
            locator,
            f"{context}.support_locators[{evidence_id!r}]",
            nonempty=True,
        )
    for key in ("expert_identity", "expertise_basis", "judgment", "rationale"):
        _require_string(record[key], f"{context}.{key}", nonempty=True)
    for key in (
        "cues",
        "options",
        "predictions",
        "tradeoffs",
        "failure_signals",
        "applicability_conditions",
        "limitations",
    ):
        _require_string_list(
            record[key], f"{context}.{key}", nonempty_items=True
        )
    if record["disagreement_status"] not in {
        "no_material_disagreement_found",
        "material_disagreement",
        "uncertain",
    }:
        raise ValidationError(f"{context}.disagreement_status is invalid")
    _parse_timestamp(record["extracted_at"], f"{context}.extracted_at")
    return record


def validate_learning_record(
    record: Any,
    context: str = "learning record",
) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise ValidationError(f"{context} must be an object")
    _require_exact_keys(record, LEARNING_RECORD_FIELDS, context)
    if record["record_type"] != "learning_record":
        raise ValidationError(f"{context}.record_type must be learning_record")
    for key in ("learning_record_id", "decision_record_id"):
        value = _require_string(record[key], f"{context}.{key}", nonempty=True)
        if not SAFE_ID_RE.fullmatch(value):
            raise ValidationError(f"{context}.{key} contains unsupported characters")
    _validate_decision_id(record["decision_id"], f"{context}.decision_id")
    validate_domain(record["domain"], f"{context}.domain")
    if record["scaffolding_level"] not in SCAFFOLDING_LEVELS:
        raise ValidationError(f"{context}.scaffolding_level is invalid")
    if record["next_scaffolding_level"] not in SCAFFOLDING_LEVELS:
        raise ValidationError(f"{context}.next_scaffolding_level is invalid")
    _require_string_list(
        record["activation_reasons"],
        f"{context}.activation_reasons",
        nonempty_items=True,
    )
    if not record["activation_reasons"]:
        raise ValidationError(f"{context}.activation_reasons must not be empty")
    for key in ("demonstrated_cues", "observed_gaps", "misconceptions"):
        _require_string_list(record[key], f"{context}.{key}", nonempty_items=True)
    if record["understanding_status"] not in UNDERSTANDING_STATUSES:
        raise ValidationError(f"{context}.understanding_status is invalid")
    if record["transfer_status"] not in TRANSFER_STATUSES:
        raise ValidationError(f"{context}.transfer_status is invalid")
    current_rank = SCAFFOLDING_LEVELS.index(record["scaffolding_level"])
    next_rank = SCAFFOLDING_LEVELS.index(record["next_scaffolding_level"])
    if next_rank > current_rank and not (
        record["understanding_status"] == "demonstrated"
        and record["transfer_status"] == "demonstrated"
    ):
        raise ValidationError(
            f"{context} may fade support only after demonstrated understanding and transfer"
        )
    if (
        record["understanding_status"] == "misconception_detected"
        or record["transfer_status"] == "not_demonstrated"
    ) and record["next_scaffolding_level"] not in {"full", "guided"}:
        raise ValidationError(
            f"{context} must restore full or guided support after a misconception or failed transfer"
        )
    if record["understanding_status"] in {"not_observed", "declined"}:
        if record["demonstrated_cues"]:
            raise ValidationError(
                f"{context}.demonstrated_cues must be empty when understanding was not observed"
            )
    _parse_timestamp(record["recorded_at"], f"{context}.recorded_at")
    return record


def validate_learning_collection(
    records: Sequence[Mapping[str, Any]],
    *,
    context: str = "learning records",
) -> None:
    seen: set[str] = set()
    for index, raw in enumerate(records):
        record = validate_learning_record(dict(raw), f"{context}[{index}]")
        record_id = record["learning_record_id"]
        if record_id in seen:
            raise DuplicateRecordError(f"duplicate learning_record_id: {record_id}")
        seen.add(record_id)


def validate_expert_experience_collection(
    search_runs: Sequence[Mapping[str, Any]],
    judgments: Sequence[Mapping[str, Any]],
    *,
    evidence_records: Sequence[Mapping[str, Any]],
    known_claim_ids: set[str] | None = None,
    context: str = "expert experience",
) -> None:
    evidence_ids = {item["evidence_id"] for item in evidence_records}
    evidence_by_id = {item["evidence_id"]: item for item in evidence_records}
    run_ids: set[str] = set()
    runs_by_id: dict[str, Mapping[str, Any]] = {}
    for index, raw in enumerate(search_runs):
        run = validate_search_run(dict(raw), f"{context}.search_runs[{index}]")
        run_id = run["search_run_id"]
        if run_id in run_ids:
            raise DuplicateRecordError(f"duplicate search_run_id: {run_id}")
        if known_claim_ids is not None:
            unknown_claims = sorted(
                set(run["decision_claim_ids"]) - known_claim_ids
            )
            if unknown_claims:
                raise ValidationError(
                    f"search run {run_id} references unknown decision claim IDs: "
                    f"{unknown_claims}"
                )
        unknown = sorted(set(run["source_evidence_ids"]) - evidence_ids)
        if unknown:
            raise ValidationError(
                f"search run {run_id} references unknown evidence IDs: {unknown}"
            )
        _assert_sources_verified(
            run["source_evidence_ids"],
            evidence_records,
            context=f"search run {run_id}",
        )
        run_ids.add(run_id)
        runs_by_id[run_id] = run
    judgment_ids: set[str] = set()
    for index, raw in enumerate(judgments):
        judgment = validate_expert_judgment(
            dict(raw), f"{context}.expert_judgments[{index}]"
        )
        judgment_id = judgment["expert_judgment_id"]
        if judgment_id in judgment_ids:
            raise DuplicateRecordError(f"duplicate expert_judgment_id: {judgment_id}")
        run_id = judgment["search_run_id"]
        if run_id not in runs_by_id:
            raise ValidationError(
                f"expert judgment {judgment_id} references unknown search run {run_id}"
            )
        run = runs_by_id[run_id]
        if judgment["decision_id"] != run["decision_id"]:
            raise ValidationError(
                f"expert judgment {judgment_id} decision_id differs from search run {run_id}"
            )
        source_ids = set(judgment["source_evidence_ids"])
        unknown = sorted(source_ids - evidence_ids)
        if unknown:
            raise ValidationError(
                f"expert judgment {judgment_id} references unknown evidence IDs: {unknown}"
            )
        _assert_sources_verified(
            judgment["source_evidence_ids"],
            evidence_records,
            context=f"expert judgment {judgment_id}",
        )
        source = evidence_by_id[judgment["source_evidence_ids"][0]]
        if judgment["expert_identity"].strip().casefold() != source[
            "source_identity"
        ]["author_or_issuer"].strip().casefold():
            raise ValidationError(
                f"expert judgment {judgment_id} identity differs from its source identity"
            )
        outside_run = sorted(source_ids - set(run["source_evidence_ids"]))
        if outside_run:
            raise ValidationError(
                f"expert judgment {judgment_id} cites sources outside search run {run_id}: "
                f"{outside_run}"
            )
        judgment_ids.add(judgment_id)


def validate_evidence_record(record: Any, context: str = "evidence record") -> dict[str, Any]:
    if not isinstance(record, dict):
        raise ValidationError(f"{context} must be an object")
    _require_exact_keys(record, EVIDENCE_FIELDS, context)
    evidence_id = _require_string(record["evidence_id"], f"{context}.evidence_id", nonempty=True)
    if not SAFE_ID_RE.fullmatch(evidence_id):
        raise ValidationError(f"{context}.evidence_id contains unsupported characters")
    _require_string_list(
        record["usage_ids"],
        f"{context}.usage_ids",
        nonempty_items=True,
    )
    if not record["usage_ids"]:
        raise ValidationError(f"{context}.usage_ids must contain at least one usage ID")
    _require_string_list(
        record["claim_ids"],
        f"{context}.claim_ids",
        nonempty_items=True,
    )
    for key in ("canonical_work_id", "artifact_id", "study_id"):
        _require_string(record[key], f"{context}.{key}", nonempty=True)
    _require_string_list(
        record["aliases"],
        f"{context}.aliases",
        nonempty_items=True,
    )
    source_identity = record["source_identity"]
    if not isinstance(source_identity, dict):
        raise ValidationError(f"{context}.source_identity must be an object")
    _require_exact_keys(
        source_identity,
        (
            "author_or_issuer",
            "title",
            "publication_date",
            "source_type",
            "stable_locator",
        ),
        f"{context}.source_identity",
    )
    for key in ("author_or_issuer", "title", "stable_locator"):
        _require_string(
            source_identity[key],
            f"{context}.source_identity.{key}",
            nonempty=True,
        )
    _require_string(
        source_identity["publication_date"],
        f"{context}.source_identity.publication_date",
        nonempty=True,
    )
    if source_identity["source_type"] not in {
        "peer_reviewed_paper",
        "official_standard",
        "regulatory_guidance",
        "research_team_protocol",
        "expert_report",
        "technical_article",
        "other",
    }:
        raise ValidationError(f"{context}.source_identity.source_type is invalid")
    if record["relationship"] not in {
        "canonical",
        "version_of",
        "mirror_of",
        "supplement_to",
        "derived_from",
        "same_study",
        "independent_work",
        "unknown",
    }:
        raise ValidationError(f"{context}.relationship is invalid")
    independence_status = record["independence_status"]
    independence_basis = record["independence_basis"]
    if not isinstance(independence_status, dict):
        raise ValidationError(f"{context}.independence_status must be an object")
    if not isinstance(independence_basis, dict):
        raise ValidationError(f"{context}.independence_basis must be an object")
    claim_ids = set(record["claim_ids"])
    if set(independence_status) != claim_ids:
        raise ValidationError(
            f"{context}.independence_status keys must exactly equal claim_ids"
        )
    if set(independence_basis) != claim_ids:
        raise ValidationError(
            f"{context}.independence_basis keys must exactly equal claim_ids"
        )
    for claim_id in sorted(claim_ids):
        if independence_status[claim_id] not in {
            "independent",
            "not_independent",
            "partially_independent",
            "unknown",
            "not_applicable",
        }:
            raise ValidationError(
                f"{context}.independence_status[{claim_id!r}] is invalid"
            )
        _require_string(
            independence_basis[claim_id],
            f"{context}.independence_basis[{claim_id!r}]",
            nonempty=True,
        )
    _require_string(record["location"], f"{context}.location", nonempty=True)
    if record["relation"] not in {"support", "oppose", "mixed", "context", "unknown"}:
        raise ValidationError(f"{context}.relation is invalid")
    if record["access_status"] not in {"available", "blocked", "unknown"}:
        raise ValidationError(f"{context}.access_status is invalid")
    if record["verification_status"] not in {
        "verified",
        "alternate_verified",
        "blocked",
        "unknown",
    }:
        raise ValidationError(f"{context}.verification_status is invalid")
    if record["license_status"] not in {
        "verified_open",
        "verified_restricted",
        "unknown",
        "not_applicable",
    }:
        raise ValidationError(f"{context}.license_status is invalid")
    _require_string_list(
        record["limitations"],
        f"{context}.limitations",
        nonempty_items=True,
    )
    _parse_timestamp(record["checked_at"], f"{context}.checked_at")
    _require_string(record["notes"], f"{context}.notes")
    return record


def validate_evidence_collection(
    records: Sequence[Mapping[str, Any]],
    *,
    known_claim_ids: set[str] | None = None,
    context: str = "evidence collection",
) -> None:
    evidence_ids: set[str] = set()
    usage_owners: dict[str, str] = {}
    alias_owners: dict[str, str] = {}
    for index, raw_record in enumerate(records):
        record = validate_evidence_record(dict(raw_record), f"{context}[{index}]")
        evidence_id = record["evidence_id"]
        if evidence_id in evidence_ids:
            raise ValidationError(f"{context} contains duplicate evidence_id {evidence_id}")
        evidence_ids.add(evidence_id)
        for usage_id in record["usage_ids"]:
            previous = usage_owners.get(usage_id)
            if previous is not None:
                raise ValidationError(
                    f"{context} usage_id {usage_id} is shared by {previous} and {evidence_id}"
                )
            usage_owners[usage_id] = evidence_id
        for alias in record["aliases"]:
            previous_work = alias_owners.get(alias)
            if previous_work is not None and previous_work != record["canonical_work_id"]:
                raise ValidationError(
                    f"{context} alias {alias!r} maps to multiple canonical works"
                )
            alias_owners[alias] = record["canonical_work_id"]
        if known_claim_ids is not None:
            unknown_claims = sorted(set(record["claim_ids"]) - known_claim_ids)
            if unknown_claims:
                raise ValidationError(
                    f"{context} evidence {evidence_id} references unknown claim IDs: "
                    f"{unknown_claims}"
                )


def validate_legacy_evidence_record_v1(
    record: Any,
    context: str = "legacy evidence record",
) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise ValidationError(f"{context} must be an object")
    _require_exact_keys(record, LEGACY_EVIDENCE_FIELDS, context)
    augmented = dict(record)
    augmented["source_identity"] = {
        "author_or_issuer": "legacy-unavailable",
        "title": "legacy-unavailable",
        "publication_date": "unknown",
        "source_type": "other",
        "stable_locator": record.get("location", "legacy-unavailable"),
    }
    validate_evidence_record(augmented, context)
    return record


def validate_legacy_evidence_collection_v1(
    records: Sequence[Mapping[str, Any]],
    *,
    context: str,
) -> None:
    evidence_ids: set[str] = set()
    for index, record in enumerate(records):
        validated = validate_legacy_evidence_record_v1(
            dict(record), f"{context}[{index}]"
        )
        evidence_id = validated["evidence_id"]
        if evidence_id in evidence_ids:
            raise DuplicateRecordError(f"duplicate legacy evidence_id: {evidence_id}")
        evidence_ids.add(evidence_id)


def validate_open_question(record: Any, context: str = "open question") -> dict[str, Any]:
    if not isinstance(record, dict):
        raise ValidationError(f"{context} must be an object")
    _require_exact_keys(record, OPEN_QUESTION_FIELDS, context)
    question_id = _require_string(record["question_id"], f"{context}.question_id", nonempty=True)
    if not SAFE_ID_RE.fullmatch(question_id):
        raise ValidationError(f"{context}.question_id contains unsupported characters")
    _require_string(record["question"], f"{context}.question", nonempty=True)
    if record["decision_id"] is not None:
        _validate_decision_id(record["decision_id"], f"{context}.decision_id")
    if not isinstance(record["blocking"], bool):
        raise ValidationError(f"{context}.blocking must be a boolean")
    _require_string(
        record["next_information_action"],
        f"{context}.next_information_action",
    )
    _require_string(record["revisit_condition"], f"{context}.revisit_condition")
    if record["status"] not in {"open", "answered", "blocked", "closed"}:
        raise ValidationError(f"{context}.status is invalid")
    return record


def validate_router_output(
    route: Any,
    *,
    evidence_ids: set[str] | None = None,
    context: str = "current_route",
) -> dict[str, Any]:
    if not isinstance(route, dict):
        raise ValidationError(f"{context} must be an object")
    _require_exact_keys(route, ROUTER_FIELDS, context)
    primary = route["primary_decision"]
    if primary is not None:
        primary = _validate_decision_id(primary, f"{context}.primary_decision")
    secondary = _require_string_list(
        route["secondary_decisions"],
        f"{context}.secondary_decisions",
        nonempty_items=True,
    )
    if len(secondary) > 2:
        raise ValidationError(f"{context}.secondary_decisions may contain at most two items")
    for index, decision_id in enumerate(secondary):
        _validate_decision_id(decision_id, f"{context}.secondary_decisions[{index}]")
    if primary is not None and primary in secondary:
        raise ValidationError(f"{context} repeats the primary decision as a secondary decision")
    _require_string(route["why_now"], f"{context}.why_now", nonempty=True)
    used = _require_string_list(
        route["evidence_used"],
        f"{context}.evidence_used",
        nonempty_items=True,
    )
    if evidence_ids is not None:
        unknown = sorted(set(used) - evidence_ids)
        if unknown:
            raise ValidationError(f"{context}.evidence_used references unknown IDs: {unknown}")
    _require_string_list(route["unknowns"], f"{context}.unknowns", nonempty_items=True)
    if route["confidence"] not in CONFIDENCE_LEVELS:
        raise ValidationError(f"{context}.confidence is invalid")
    method = route["next_method_module"]
    if method is not None and method not in METHOD_MODULES:
        raise ValidationError(f"{context}.next_method_module is invalid")
    if primary is None:
        if secondary:
            raise ValidationError(
                f"{context} abstention requires secondary_decisions to be empty"
            )
        if route["confidence"] != "low":
            raise ValidationError(f"{context} may abstain only with low confidence")
        if method is not None:
            raise ValidationError(
                f"{context} abstention requires next_method_module to be null"
            )
    return route


def validate_state(state: Any) -> dict[str, Any]:
    if not isinstance(state, dict):
        raise ValidationError("research state must be an object")
    if "schema_version" not in state:
        raise ValidationError("research state is missing schema_version")
    if state["schema_version"] != SCHEMA_VERSION:
        raise UnsupportedSchemaError(
            f"schema_version {state['schema_version']!r} is unsupported; expected {SCHEMA_VERSION}"
        )
    _require_exact_keys(state, STATE_FIELDS, "research state")
    if (
        not isinstance(state["state_revision"], int)
        or isinstance(state["state_revision"], bool)
        or state["state_revision"] < 1
    ):
        raise ValidationError("state_revision must be an integer greater than or equal to 1")
    if state["skill_version"] not in SUPPORTED_SKILL_VERSIONS:
        raise ValidationError(
            "skill_version must be one of "
            + ", ".join(sorted(SUPPORTED_SKILL_VERSIONS))
        )

    project = state["project"]
    if not isinstance(project, dict):
        raise ValidationError("project must be an object")
    _require_exact_keys(project, ("id", "name"), "project")
    project_id = _require_string(project["id"], "project.id", nonempty=True)
    if not PROJECT_ID_RE.fullmatch(project_id):
        raise ValidationError("project.id contains unsupported characters")
    _require_string(project["name"], "project.name", nonempty=True)
    _require_string(state["research_goal"], "research_goal")

    scope = state["scope"]
    if not isinstance(scope, dict):
        raise ValidationError("scope must be an object")
    _require_exact_keys(scope, ("in_scope", "out_of_scope"), "scope")
    _require_string_list(scope["in_scope"], "scope.in_scope")
    _require_string_list(scope["out_of_scope"], "scope.out_of_scope")
    _require_string_list(state["constraints"], "constraints")

    permissions = state["permissions"]
    if not isinstance(permissions, dict):
        raise ValidationError("permissions must be an object")
    _require_exact_keys(
        permissions,
        ("network", "filesystem", "external_actions", "ethics_review"),
        "permissions",
    )
    permission_enums = {
        "network": {"unknown", "allowed", "denied"},
        "filesystem": {"unknown", "read_only", "workspace_write", "unrestricted"},
        "external_actions": {"unknown", "allowed", "denied_until_authorized", "denied"},
        "ethics_review": {"unknown", "not_required", "required", "approved", "blocked"},
    }
    for key, allowed in permission_enums.items():
        if permissions[key] not in allowed:
            raise ValidationError(f"permissions.{key} is invalid")

    tracked_ids: dict[str, set[str]] = {}
    for collection_name in ("claims", "hypotheses", "experiments"):
        items = state[collection_name]
        if not isinstance(items, list):
            raise ValidationError(f"{collection_name} must be an array")
        ids: list[str] = []
        for index, item in enumerate(items):
            context = f"{collection_name}[{index}]"
            if not isinstance(item, dict):
                raise ValidationError(f"{context} must be an object")
            _require_exact_keys(item, ("id", "summary", "status"), context)
            item_id = _require_string(item["id"], f"{context}.id", nonempty=True)
            ids.append(item_id)
            _require_string(item["summary"], f"{context}.summary", nonempty=True)
            if item["status"] not in {
                "open",
                "active",
                "supported",
                "challenged",
                "rejected",
                "blocked",
                "closed",
            }:
                raise ValidationError(f"{context}.status is invalid")
        if len(ids) != len(set(ids)):
            raise ValidationError(f"{collection_name} contains duplicate IDs")
        tracked_ids[collection_name] = set(ids)

    evidence = state["evidence_index"]
    if not isinstance(evidence, list):
        raise ValidationError("evidence_index must be an array")
    validate_evidence_collection(
        evidence,
        known_claim_ids=tracked_ids["claims"],
        context="evidence_index",
    )
    evidence_ids = [item["evidence_id"] for item in evidence]

    validate_domain(state["domain"], "domain")
    search_runs = state["search_runs"]
    judgments = state["expert_judgment_index"]
    if not isinstance(search_runs, list):
        raise ValidationError("search_runs must be an array")
    if not isinstance(judgments, list):
        raise ValidationError("expert_judgment_index must be an array")
    validate_expert_experience_collection(
        search_runs,
        judgments,
        evidence_records=evidence,
        known_claim_ids=tracked_ids["claims"],
        context="research state",
    )
    learning_records = state["learning_record_index"]
    if not isinstance(learning_records, list):
        raise ValidationError("learning_record_index must be an array")
    validate_learning_collection(
        learning_records,
        context="research state.learning_record_index",
    )

    if state["current_route"] is not None:
        current_route = state["current_route"]
        if not isinstance(current_route, dict):
            raise ValidationError("current_route must be null or a wrapper object")
        _require_exact_keys(
            current_route,
            ("decision_record_id", "route"),
            "current_route",
        )
        route_record_id = _require_string(
            current_route["decision_record_id"],
            "current_route.decision_record_id",
            nonempty=True,
        )
        if not SAFE_ID_RE.fullmatch(route_record_id):
            raise ValidationError(
                "current_route.decision_record_id contains unsupported characters"
            )
        route = validate_router_output(
            current_route["route"],
            evidence_ids=set(evidence_ids),
            context="current_route.route",
        )
        if route["primary_decision"] is None:
            raise ValidationError(
                "an abstention cannot be stored as current_route; use null current_route"
            )
    _require_string_list(state["open_questions"], "open_questions", nonempty_items=True)

    revisit_queue = state["revisit_queue"]
    if not isinstance(revisit_queue, list):
        raise ValidationError("revisit_queue must be an array")
    for index, item in enumerate(revisit_queue):
        context = f"revisit_queue[{index}]"
        if not isinstance(item, dict):
            raise ValidationError(f"{context} must be an object")
        _require_exact_keys(item, ("decision_record_id", "condition"), context)
        _require_string(item["decision_record_id"], f"{context}.decision_record_id", nonempty=True)
        _require_string(item["condition"], f"{context}.condition", nonempty=True)

    created = _parse_timestamp(state["created_at"], "created_at")
    updated = _parse_timestamp(state["updated_at"], "updated_at")
    if updated < created:
        raise ValidationError("updated_at precedes created_at")
    return state


def validate_legacy_state_v1(state: Any) -> dict[str, Any]:
    """Validate enough of v1 to expose it safely without authorizing writes."""

    if not isinstance(state, dict):
        raise ValidationError("legacy research state must be an object")
    _require_exact_keys(state, LEGACY_STATE_FIELDS, "legacy research state")
    if state.get("schema_version") != 1:
        raise UnsupportedSchemaError(
            f"schema_version {state.get('schema_version')!r} is unsupported"
        )
    if state.get("skill_version") != "0.1.0":
        raise ValidationError("legacy skill_version must be 0.1.0")
    if (
        not isinstance(state.get("state_revision"), int)
        or isinstance(state.get("state_revision"), bool)
        or state["state_revision"] < 1
    ):
        raise ValidationError("legacy state_revision must be an integer >= 1")
    project = state["project"]
    if not isinstance(project, dict):
        raise ValidationError("legacy project must be an object")
    _require_exact_keys(project, ("id", "name"), "legacy project")
    _require_string(project["id"], "legacy project.id", nonempty=True)
    _require_string(project["name"], "legacy project.name", nonempty=True)
    if not isinstance(state["evidence_index"], list):
        raise ValidationError("legacy evidence_index must be an array")
    validate_legacy_evidence_collection_v1(
        state["evidence_index"], context="legacy evidence_index"
    )
    if not isinstance(state["open_questions"], list):
        raise ValidationError("legacy open_questions must be an array")
    _require_string_list(
        state["open_questions"], "legacy open_questions", nonempty_items=True
    )
    _parse_timestamp(state["created_at"], "legacy created_at")
    _parse_timestamp(state["updated_at"], "legacy updated_at")
    return state


def validate_decision_record(record: Any, context: str = "decision record") -> dict[str, Any]:
    if not isinstance(record, dict):
        raise ValidationError(f"{context} must be an object")
    _require_exact_keys(record, DECISION_RECORD_FIELDS, context)
    record_id = _require_string(record["decision_record_id"], f"{context}.decision_record_id", nonempty=True)
    if not SAFE_ID_RE.fullmatch(record_id):
        raise ValidationError(f"{context}.decision_record_id contains unsupported characters")
    _validate_decision_id(record["decision_id"], f"{context}.decision_id")
    _require_string(record["decision_label"], f"{context}.decision_label", nonempty=True)
    if record["status"] not in DECISION_STATUSES:
        raise ValidationError(f"{context}.status is invalid")
    _require_string(record["research_context"], f"{context}.research_context")
    _require_string(record["question"], f"{context}.question", nonempty=True)
    _require_string_list(record["alternatives"], f"{context}.alternatives", nonempty_items=True, unique=False)
    if record["current_choice"] is not None:
        _require_string(record["current_choice"], f"{context}.current_choice")
    for key in (
        "evidence_for",
        "evidence_against",
        "missing_evidence",
        "constraints",
        "source_refs",
    ):
        _require_string_list(
            record[key],
            f"{context}.{key}",
            nonempty_items=key != "constraints",
        )
    _require_string(record["uncertainty"], f"{context}.uncertainty")
    if record["confidence"] not in CONFIDENCE_LEVELS:
        raise ValidationError(f"{context}.confidence is invalid")
    _require_string(record["rationale"], f"{context}.rationale", nonempty=True)
    _require_string(
        record["next_high_information_action"],
        f"{context}.next_high_information_action",
    )
    _require_string(record["revisit_condition"], f"{context}.revisit_condition")
    _require_string(record["stop_or_pivot_condition"], f"{context}.stop_or_pivot_condition")
    validate_domain(record["domain"], f"{context}.domain")
    search_run_ids = _require_string_list(
        record["search_run_ids"],
        f"{context}.search_run_ids",
        nonempty_items=True,
    )
    if not search_run_ids:
        raise ValidationError(
            f"{context}.search_run_ids must record the mandatory real-time search attempt"
        )
    _require_string_list(
        record["expert_judgment_ids"],
        f"{context}.expert_judgment_ids",
        nonempty_items=True,
    )
    user_initial = record["user_initial_judgment"]
    if not isinstance(user_initial, dict):
        raise ValidationError(f"{context}.user_initial_judgment must be an object")
    _require_exact_keys(
        user_initial,
        ("choice", "reasoning_summary", "elicitation_status"),
        f"{context}.user_initial_judgment",
    )
    if user_initial["choice"] is not None:
        _require_string(
            user_initial["choice"],
            f"{context}.user_initial_judgment.choice",
            nonempty=True,
        )
    _require_string(
        user_initial["reasoning_summary"],
        f"{context}.user_initial_judgment.reasoning_summary",
    )
    if user_initial["elicitation_status"] not in {"provided", "scaffolded", "deferred_by_user"}:
        raise ValidationError(
            f"{context}.user_initial_judgment.elicitation_status is invalid"
        )
    comparison = record["expert_comparison_feedback"]
    if not isinstance(comparison, dict):
        raise ValidationError(f"{context}.expert_comparison_feedback must be an object")
    _require_exact_keys(
        comparison,
        ("agreements", "differences", "feedback"),
        f"{context}.expert_comparison_feedback",
    )
    _require_string_list(
        comparison["agreements"],
        f"{context}.expert_comparison_feedback.agreements",
        nonempty_items=True,
    )
    _require_string_list(
        comparison["differences"],
        f"{context}.expert_comparison_feedback.differences",
        nonempty_items=True,
    )
    _require_string(
        comparison["feedback"],
        f"{context}.expert_comparison_feedback.feedback",
        nonempty=True,
    )
    revised = record["user_revised_decision"]
    if not isinstance(revised, dict):
        raise ValidationError(f"{context}.user_revised_decision must be an object")
    _require_exact_keys(
        revised,
        ("choice", "reasoning_summary", "revision_status"),
        f"{context}.user_revised_decision",
    )
    if revised["choice"] is not None:
        _require_string(
            revised["choice"],
            f"{context}.user_revised_decision.choice",
            nonempty=True,
        )
    _require_string(
        revised["reasoning_summary"],
        f"{context}.user_revised_decision.reasoning_summary",
    )
    if revised["revision_status"] not in {"revised", "confirmed", "pending"}:
        raise ValidationError(
            f"{context}.user_revised_decision.revision_status is invalid"
        )
    _require_string_list(
        record["transferable_principles"],
        f"{context}.transferable_principles",
        nonempty_items=True,
    )
    support = record["decision_support"]
    if not isinstance(support, dict):
        raise ValidationError(f"{context}.decision_support must be an object")
    _require_exact_keys(
        support,
        ("action_status", "applicability_conditions", "conditions_that_change_decision"),
        f"{context}.decision_support",
    )
    if support["action_status"] not in ACTION_STATUSES:
        raise ValidationError(f"{context}.decision_support.action_status is invalid")
    for key in ("applicability_conditions", "conditions_that_change_decision"):
        _require_string_list(
            support[key],
            f"{context}.decision_support.{key}",
            nonempty_items=True,
        )
    if not record["expert_judgment_ids"] and support["action_status"] != "暂缓定论":
        raise ValidationError(
            f"{context} without expert judgments must use action_status 暂缓定论"
        )
    explanation = record["explanation_support"]
    if not isinstance(explanation, dict):
        raise ValidationError(f"{context}.explanation_support must be an object")
    _require_exact_keys(
        explanation,
        (
            "scaffolding_level",
            "activation_reasons",
            "components_shown",
            "understanding_status",
            "transfer_status",
        ),
        f"{context}.explanation_support",
    )
    if explanation["scaffolding_level"] not in SCAFFOLDING_LEVELS:
        raise ValidationError(
            f"{context}.explanation_support.scaffolding_level is invalid"
        )
    for key in ("activation_reasons", "components_shown"):
        _require_string_list(
            explanation[key],
            f"{context}.explanation_support.{key}",
            nonempty_items=True,
        )
    if explanation["understanding_status"] not in UNDERSTANDING_STATUSES:
        raise ValidationError(
            f"{context}.explanation_support.understanding_status is invalid"
        )
    if explanation["transfer_status"] not in TRANSFER_STATUSES:
        raise ValidationError(
            f"{context}.explanation_support.transfer_status is invalid"
        )
    learning_record_ids = _require_string_list(
        record["learning_record_ids"],
        f"{context}.learning_record_ids",
        nonempty_items=True,
    )
    for learning_record_id in learning_record_ids:
        if not SAFE_ID_RE.fullmatch(learning_record_id):
            raise ValidationError(
                f"{context}.learning_record_ids contains unsupported characters"
            )
    supersedes = record["supersedes"]
    if supersedes is not None:
        supersedes = _require_string(supersedes, f"{context}.supersedes", nonempty=True)
        if not SAFE_ID_RE.fullmatch(supersedes):
            raise ValidationError(f"{context}.supersedes contains unsupported characters")
        if supersedes == record_id:
            raise ValidationError(f"{context} cannot supersede itself")
    if record["status"] in {"reopened", "superseded"} and supersedes is None:
        raise ValidationError(f"{context}.status={record['status']} requires supersedes")
    created = _parse_timestamp(record["created_at"], f"{context}.created_at")
    updated = _parse_timestamp(record["updated_at"], f"{context}.updated_at")
    if updated < created:
        raise ValidationError(f"{context}.updated_at precedes created_at")
    return record


def validate_legacy_decision_record_v1(
    record: Any,
    context: str = "legacy decision record",
) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise ValidationError(f"{context} must be an object")
    _require_exact_keys(record, LEGACY_DECISION_RECORD_FIELDS, context)
    record_id = _require_string(
        record["decision_record_id"], f"{context}.decision_record_id", nonempty=True
    )
    if not SAFE_ID_RE.fullmatch(record_id):
        raise ValidationError(f"{context}.decision_record_id contains unsupported characters")
    _validate_decision_id(record["decision_id"], f"{context}.decision_id")
    if record["status"] not in DECISION_STATUSES:
        raise ValidationError(f"{context}.status is invalid")
    for key in ("decision_label", "question", "rationale"):
        _require_string(record[key], f"{context}.{key}", nonempty=True)
    for key in (
        "alternatives",
        "evidence_for",
        "evidence_against",
        "missing_evidence",
        "constraints",
        "source_refs",
    ):
        _require_string_list(record[key], f"{context}.{key}")
    if record["confidence"] not in CONFIDENCE_LEVELS:
        raise ValidationError(f"{context}.confidence is invalid")
    if record["supersedes"] is not None:
        _require_string(record["supersedes"], f"{context}.supersedes", nonempty=True)
    _parse_timestamp(record["created_at"], f"{context}.created_at")
    _parse_timestamp(record["updated_at"], f"{context}.updated_at")
    return record


def initial_state(
    project_id: str,
    project_name: str,
    research_goal: str = "",
    *,
    domain_name: str = "other",
    domain_support_status: str | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    timestamp = timestamp or utc_now()
    if domain_support_status is None:
        domain_support_status = (
            "public_source_decision_support_preview"
            if domain_name in STEM_DOMAINS
            else "domain_judgment_unavailable"
        )
    state = {
        "schema_version": SCHEMA_VERSION,
        "state_revision": 1,
        "skill_version": SKILL_VERSION,
        "project": {"id": project_id, "name": project_name},
        "research_goal": research_goal,
        "scope": {"in_scope": [], "out_of_scope": []},
        "constraints": [],
        "permissions": {
            "network": "unknown",
            "filesystem": "workspace_write",
            "external_actions": "denied_until_authorized",
            "ethics_review": "unknown",
        },
        "claims": [],
        "hypotheses": [],
        "experiments": [],
        "evidence_index": [],
        "domain": {
            "name": domain_name,
            "support_status": domain_support_status,
        },
        "search_runs": [],
        "expert_judgment_index": [],
        "learning_record_index": [],
        "current_route": None,
        "open_questions": [],
        "revisit_queue": [],
        "created_at": timestamp,
        "updated_at": timestamp,
    }
    return validate_state(state)


def load_state(path: str | Path) -> dict[str, Any]:
    state_path = Path(path)
    text = _read_utf8(state_path)
    value = strict_json_loads(text, context=str(state_path))
    return validate_state(value)


def _load_v2_compat_module() -> Any:
    module_path = Path(__file__).with_name("research_state_v2_compat.py")
    spec = __import__("importlib.util").util.spec_from_file_location(
        "research_state_v2_compat_runtime", module_path
    )
    if spec is None or spec.loader is None:
        raise UnsupportedSchemaError("v1/v2 compatibility helper is unavailable")
    module = __import__("importlib.util").util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_state_read_only(path: str | Path) -> tuple[dict[str, Any], bool]:
    """Load v3 or a validated v1/v2 state; the boolean marks read-only legacy data."""

    state_path = Path(path)
    text = _read_utf8(state_path)
    value = strict_json_loads(text, context=str(state_path))
    if isinstance(value, dict) and value.get("schema_version") in {1, 2}:
        legacy_state, _ = _load_v2_compat_module().load_state_read_only(state_path)
        return legacy_state, True
    return validate_state(value), False


@contextlib.contextmanager
def workspace_lock(state_dir: Path, *, timeout: float = 5.0) -> Iterator[None]:
    try:
        os.makedirs(_native_fs_path(state_dir), exist_ok=True)
    except OSError as exc:
        raise ReadOnlyStateError(f"cannot create state directory {state_dir}: {exc}") from exc
    lock_path = state_dir / ".write.lock"
    lock_native = _native_fs_path(lock_path)
    deadline = time.monotonic() + timeout
    descriptor: int | None = None
    while descriptor is None:
        try:
            descriptor = os.open(lock_native, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.write(descriptor, f"pid={os.getpid()}\n".encode("ascii"))
            os.fsync(descriptor)
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise ConcurrentModificationError(
                    f"timed out waiting for state lock {lock_path}; no files were changed"
                )
            time.sleep(0.01)
        except PermissionError as exc:
            # Windows can report sharing violations for O_EXCL as access denied
            # while another thread owns the lock file. The owner may remove it
            # before exists() is observed, so retry writable directories.
            if os.access(_native_fs_path(state_dir), os.W_OK) and time.monotonic() < deadline:
                time.sleep(0.01)
                continue
            if _path_exists(lock_path):
                raise ConcurrentModificationError(
                    f"timed out waiting for state lock {lock_path}; no files were changed"
                ) from exc
            raise ReadOnlyStateError(f"cannot acquire state lock {lock_path}: {exc}") from exc
        except OSError as exc:
            raise ReadOnlyStateError(f"cannot acquire state lock {lock_path}: {exc}") from exc
    try:
        yield
    finally:
        if descriptor is not None:
            os.close(descriptor)
        try:
            os.unlink(lock_native)
        except FileNotFoundError:
            pass
        except OSError:
            # A stale lock is safer than deleting a path whose identity changed.
            pass


def atomic_write_text(
    path: Path,
    text: str,
    *,
    expected_digest: str | None | object = _UNSET,
) -> str:
    """Atomically replace one file after an optional optimistic concurrency check.

    Pass expected_digest=None to require that the target does not yet exist.
    Pass a SHA-256 string to require that exact current content.
    """

    path = Path(path)
    try:
        os.makedirs(_native_fs_path(path.parent), exist_ok=True)
        exists = _path_exists(path)
        if expected_digest is None and exists:
            raise ConcurrentModificationError(f"{path} appeared during initialization")
        if isinstance(expected_digest, str):
            if not exists:
                raise ConcurrentModificationError(f"{path} disappeared before write")
            current_digest = sha256_file(path)
            if current_digest != expected_digest:
                raise ConcurrentModificationError(
                    f"{path} changed concurrently: expected {expected_digest}, got {current_digest}"
                )
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=_native_fs_path(path.parent),
        )
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(text)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_name, _native_fs_path(path))
        except Exception:
            with contextlib.suppress(FileNotFoundError):
                os.unlink(temporary_name)
            raise
    except ConcurrentModificationError:
        raise
    except PermissionError as exc:
        raise ReadOnlyStateError(f"write denied for {path}; continue in read-only mode") from exc
    except OSError as exc:
        raise ReadOnlyStateError(f"cannot atomically write {path}: {exc}") from exc
    return sha256_bytes(text.encode("utf-8"))


def _parse_fenced_record_text(
    text: str,
    *,
    header: str,
    id_field: str,
    validator: Any,
    record_kind: str,
) -> list[dict[str, Any]]:
    if not text.startswith(header):
        raise CorruptStateError(f"{record_kind} file has an unknown or damaged header")
    fence = re.escape(chr(96) * 3)
    block_pattern = re.compile(
        rf"\n## (?P<record_id>[A-Za-z0-9][A-Za-z0-9._:-]*)\n\n"
        rf"{fence}json\n(?P<body>.*?)\n{fence}\n",
        re.DOTALL,
    )
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    position = len(header)
    while position < len(text):
        match = block_pattern.match(text, position)
        if match is None:
            snippet = text[position : position + 80].replace("\n", "\\n")
            raise CorruptStateError(f"invalid {record_kind} content near: {snippet!r}")
        record = strict_json_loads(match.group("body"), context=f"{record_kind} {match.group('record_id')}")
        validator(record, f"{record_kind} {match.group('record_id')}")
        record_id = record[id_field]
        if record_id != match.group("record_id"):
            raise ValidationError(
                f"{record_kind} heading {match.group('record_id')} does not match {id_field} {record_id}"
            )
        if record_id in seen:
            raise ValidationError(f"duplicate {id_field}: {record_id}")
        seen.add(record_id)
        records.append(record)
        position = match.end()
    return records


def _read_utf8(path: Path) -> str:
    try:
        with open(_native_fs_path(path), "r", encoding="utf-8") as handle:
            return handle.read()
    except UnicodeDecodeError as exc:
        raise CorruptStateError(f"{path} is not valid UTF-8") from exc
    except OSError as exc:
        raise ReadOnlyStateError(f"cannot read {path}: {exc}") from exc


def parse_evidence_ledger(path: str | Path) -> list[dict[str, Any]]:
    records = _parse_fenced_record_text(
        _read_utf8(Path(path)),
        header=EVIDENCE_HEADER,
        id_field="evidence_id",
        validator=validate_evidence_record,
        record_kind="evidence record",
    )
    validate_evidence_collection(records, context="evidence ledger")
    return records


def parse_open_questions(path: str | Path) -> list[dict[str, Any]]:
    return _parse_fenced_record_text(
        _read_utf8(Path(path)),
        header=QUESTIONS_HEADER,
        id_field="question_id",
        validator=validate_open_question,
        record_kind="open question",
    )


def _parse_expert_experience_text(
    text: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not text.startswith(EXPERT_HEADER):
        raise CorruptStateError(
            "expert experience ledger has an unknown or damaged header"
        )
    fence = re.escape(chr(96) * 3)
    block_pattern = re.compile(
        rf"\n## (?P<record_id>[A-Za-z0-9][A-Za-z0-9._:-]*)\n\n"
        rf"{fence}json\n(?P<body>.*?)\n{fence}\n",
        re.DOTALL,
    )
    search_runs: list[dict[str, Any]] = []
    judgments: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    position = len(EXPERT_HEADER)
    while position < len(text):
        match = block_pattern.match(text, position)
        if match is None:
            snippet = text[position : position + 80].replace("\n", "\\n")
            raise CorruptStateError(
                f"invalid expert experience content near: {snippet!r}"
            )
        record = strict_json_loads(
            match.group("body"), context=f"expert record {match.group('record_id')}"
        )
        if not isinstance(record, dict):
            raise ValidationError("expert experience record must be an object")
        record_type = record.get("record_type")
        if record_type == "search_run":
            validate_search_run(record, f"search run {match.group('record_id')}")
            record_id = record["search_run_id"]
            search_runs.append(record)
        elif record_type == "expert_judgment":
            validate_expert_judgment(
                record, f"expert judgment {match.group('record_id')}"
            )
            record_id = record["expert_judgment_id"]
            judgments.append(record)
        else:
            raise ValidationError(
                f"expert record {match.group('record_id')} has invalid record_type"
            )
        if record_id != match.group("record_id"):
            raise ValidationError(
                f"expert record heading {match.group('record_id')} does not match ID {record_id}"
            )
        if record_id in seen_ids:
            raise DuplicateRecordError(f"duplicate expert ledger record ID: {record_id}")
        seen_ids.add(record_id)
        position = match.end()
    return search_runs, judgments


def parse_expert_experience_ledger(
    path: str | Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return _parse_expert_experience_text(_read_utf8(Path(path)))


def parse_learning_ledger(path: str | Path) -> list[dict[str, Any]]:
    records = _parse_fenced_record_text(
        _read_utf8(Path(path)),
        header=LEARNING_HEADER,
        id_field="learning_record_id",
        validator=validate_learning_record,
        record_kind="learning record",
    )
    validate_learning_collection(records, context="learning ledger")
    return records


def _assert_support_indexes_consistent(
    state_value: Mapping[str, Any],
    ledger_records: Sequence[Mapping[str, Any]],
    question_records: Sequence[Mapping[str, Any]],
    search_runs: Sequence[Mapping[str, Any]],
    expert_judgments: Sequence[Mapping[str, Any]],
    learning_records: Sequence[Mapping[str, Any]],
) -> None:
    if list(state_value["evidence_index"]) != list(ledger_records):
        raise ValidationError(
            "research-state.yaml evidence_index differs from evidence-ledger.md; "
            "do not write either file manually"
        )
    question_ids = [record["question_id"] for record in question_records]
    if list(state_value["open_questions"]) != question_ids:
        raise ValidationError(
            "research-state.yaml open_questions differs from open-questions.md; "
            "do not write either file manually"
        )
    if list(state_value["search_runs"]) != list(search_runs):
        raise ValidationError(
            "research-state.yaml search_runs differs from expert-experience-ledger.md; "
            "do not write either file manually"
        )
    if list(state_value["expert_judgment_index"]) != list(expert_judgments):
        raise ValidationError(
            "research-state.yaml expert_judgment_index differs from "
            "expert-experience-ledger.md; do not write either file manually"
        )
    if list(state_value["learning_record_index"]) != list(learning_records):
        raise ValidationError(
            "research-state.yaml learning_record_index differs from learning-ledger.md; "
            "do not write either file manually"
        )
    validate_expert_experience_collection(
        search_runs,
        expert_judgments,
        evidence_records=ledger_records,
        known_claim_ids={item["id"] for item in state_value["claims"]},
        context="expert experience ledger",
    )
    validate_learning_collection(learning_records, context="learning ledger")


def _load_support_records(
    state_dir: Path,
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    ledger_records = parse_evidence_ledger(state_dir / EVIDENCE_FILE_NAME)
    question_records = parse_open_questions(state_dir / QUESTIONS_FILE_NAME)
    search_runs, judgments = parse_expert_experience_ledger(
        state_dir / EXPERT_FILE_NAME
    )
    learning_records = parse_learning_ledger(state_dir / LEARNING_FILE_NAME)
    return ledger_records, question_records, search_runs, judgments, learning_records


def _commit_two_files_with_rollback(
    first_path: Path,
    first_old_text: str,
    first_new_text: str,
    second_path: Path,
    second_old_text: str,
    second_new_text: str,
) -> tuple[str, str]:
    first_old_digest = sha256_bytes(first_old_text.encode("utf-8"))
    second_old_digest = sha256_bytes(second_old_text.encode("utf-8"))
    first_new_digest = atomic_write_text(
        first_path,
        first_new_text,
        expected_digest=first_old_digest,
    )
    try:
        second_new_digest = atomic_write_text(
            second_path,
            second_new_text,
            expected_digest=second_old_digest,
        )
    except Exception as original_exc:
        try:
            atomic_write_text(
                first_path,
                first_old_text,
                expected_digest=first_new_digest,
            )
        except Exception as rollback_exc:
            raise PartialCommitError(
                f"second write failed ({original_exc}); rollback also failed "
                f"({rollback_exc}); validate before any further writes",
                [str(first_path)],
            ) from original_exc
        raise
    return first_new_digest, second_new_digest


def init_workspace(
    project_root: str | Path,
    *,
    project_id: str | None = None,
    project_name: str | None = None,
    research_goal: str = "",
    domain_name: str = "other",
    domain_support_status: str | None = None,
    timestamp: str | None = None,
    lock_timeout: float = 5.0,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    state_dir = _resolve_state_dir(root)
    state_path = state_dir / STATE_FILE_NAME
    trace_path = state_dir / TRACE_FILE_NAME
    evidence_path = state_dir / EVIDENCE_FILE_NAME
    questions_path = state_dir / QUESTIONS_FILE_NAME
    expert_path = state_dir / EXPERT_FILE_NAME
    learning_path = state_dir / LEARNING_FILE_NAME
    if _path_is_file(state_path):
        raw_state = strict_json_loads(_read_utf8(state_path), context=str(state_path))
        if isinstance(raw_state, dict) and raw_state.get("schema_version") in {1, 2}:
            _load_v2_compat_module().validate_workspace(root)
            raise UnsupportedSchemaError(
                f"schema_version {raw_state['schema_version']} is recognized read-only; "
                "initialize v3 in a new workspace because this Preview does not migrate state"
            )
    legacy_paths = (state_path, trace_path, evidence_path, questions_path)
    workspace_paths = (*legacy_paths, expert_path, learning_path)
    if all(_path_is_file(path) for path in legacy_paths) and not _path_exists(expert_path):
        legacy_state, is_legacy = load_state_read_only(state_path)
        if is_legacy:
            _validate_legacy_workspace_files(
                legacy_state,
                trace_path,
                evidence_path,
                questions_path,
            )
            raise UnsupportedSchemaError(
                "schema_version 1 is recognized read-only; initialize v2 in a new "
                "workspace because this Preview does not migrate state"
            )
    present_before_lock = sum(_path_exists(path) for path in workspace_paths)
    if present_before_lock not in {0, len(workspace_paths)}:
        present_names = sorted(path.name for path in workspace_paths if _path_exists(path))
        missing_names = sorted(path.name for path in workspace_paths if not _path_exists(path))
        raise ValidationError(
            "partial state workspace is not repairable by init; "
            f"present={present_names}, missing={missing_names}"
        )
    name = project_name or root.name or "research-project"
    if project_id is None:
        project_id = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-") or "research-project"
    created: list[str] = []
    existing: list[str] = []

    with workspace_lock(state_dir, timeout=lock_timeout):
        present_under_lock = sum(_path_exists(path) for path in workspace_paths)
        if present_under_lock not in {0, len(workspace_paths)}:
            present_names = sorted(path.name for path in workspace_paths if _path_exists(path))
            missing_names = sorted(path.name for path in workspace_paths if not _path_exists(path))
            raise ValidationError(
                "state workspace changed to a partial state during initialization; "
                f"present={present_names}, missing={missing_names}"
            )

        # Validate every existing file and cross-file index before creating
        # any missing file.
        existing_state_value = None
        existing_trace_records: list[dict[str, Any]] = []
        existing_ledger_records: list[dict[str, Any]] = []
        existing_question_records: list[dict[str, Any]] = []
        existing_search_runs: list[dict[str, Any]] = []
        existing_expert_judgments: list[dict[str, Any]] = []
        existing_learning_records: list[dict[str, Any]] = []
        if _path_exists(state_path):
            existing_state_value = load_state(state_path)
            existing.append(STATE_FILE_NAME)
        if _path_exists(trace_path):
            existing_trace_records = parse_decision_trace(trace_path)
            existing.append(TRACE_FILE_NAME)
        if _path_exists(evidence_path):
            existing_ledger_records = parse_evidence_ledger(evidence_path)
            existing.append(EVIDENCE_FILE_NAME)
        if _path_exists(questions_path):
            existing_question_records = parse_open_questions(questions_path)
            existing.append(QUESTIONS_FILE_NAME)
        if _path_exists(expert_path):
            existing_search_runs, existing_expert_judgments = (
                parse_expert_experience_ledger(expert_path)
            )
            existing.append(EXPERT_FILE_NAME)
        if _path_exists(learning_path):
            existing_learning_records = parse_learning_ledger(learning_path)
            existing.append(LEARNING_FILE_NAME)
        if existing_state_value is None:
            if existing_trace_records or existing_ledger_records or existing_question_records:
                raise ValidationError(
                    "cannot initialize a missing state over non-empty trace, evidence, "
                    "or question records"
                )
        else:
            _assert_support_indexes_consistent(
                existing_state_value,
                existing_ledger_records,
                existing_question_records,
                existing_search_runs,
                existing_expert_judgments,
                existing_learning_records,
            )
            if existing_trace_records:
                evidence_ids = {
                    item["evidence_id"] for item in existing_state_value["evidence_index"]
                }
                existing_trace_records = parse_decision_trace(
                    trace_path,
                    evidence_ids=evidence_ids,
                )
            _validate_route_trace_links(existing_state_value, existing_trace_records)

        planned = (
            (
                state_path,
                canonical_json(
                    initial_state(
                        project_id,
                        name,
                        research_goal,
                        domain_name=domain_name,
                        domain_support_status=domain_support_status,
                        timestamp=timestamp,
                    )
                ),
            ),
            (trace_path, TRACE_HEADER),
            (evidence_path, EVIDENCE_HEADER),
            (questions_path, QUESTIONS_HEADER),
            (expert_path, EXPERT_HEADER),
            (learning_path, LEARNING_HEADER),
        )
        created_entries: list[tuple[Path, str]] = []
        try:
            for path, content in planned:
                if not _path_exists(path):
                    atomic_write_text(path, content, expected_digest=None)
                    created.append(path.name)
                    created_entries.append((path, sha256_bytes(content.encode("utf-8"))))

            final_state = load_state(state_path)
            final_ledger = parse_evidence_ledger(evidence_path)
            final_questions = parse_open_questions(questions_path)
            final_search_runs, final_judgments = parse_expert_experience_ledger(
                expert_path
            )
            final_learning_records = parse_learning_ledger(learning_path)
            _assert_support_indexes_consistent(
                final_state,
                final_ledger,
                final_questions,
                final_search_runs,
                final_judgments,
                final_learning_records,
            )
            final_trace = parse_decision_trace(
                trace_path,
                evidence_ids={
                    item["evidence_id"] for item in final_state["evidence_index"]
                },
            )
            _validate_route_trace_links(final_state, final_trace)
        except Exception as original_exc:
            rollback_failed: list[str] = []
            for path, expected_digest in reversed(created_entries):
                try:
                    if _path_is_file(path) and sha256_file(path) == expected_digest:
                        os.unlink(_native_fs_path(path))
                    elif _path_exists(path):
                        rollback_failed.append(str(path))
                except OSError:
                    rollback_failed.append(str(path))
            if rollback_failed:
                raise PartialCommitError(
                    f"initialization failed ({original_exc}); rollback was incomplete",
                    rollback_failed,
                ) from original_exc
            raise

    return {
        "status": "pass",
        "mode": "write",
        "state_directory": str(state_dir),
        "created": sorted(created),
        "existing": sorted(existing),
    }


def render_decision_record(record: Mapping[str, Any]) -> str:
    validated = validate_decision_record(dict(record))
    fence = chr(96) * 3
    return (
        f"\n## {validated['decision_record_id']}\n\n"
        f"{fence}json\n"
        f"{canonical_json(validated).rstrip()}\n"
        f"{fence}\n"
    )


def _render_fenced_record(
    record: Mapping[str, Any],
    *,
    id_field: str,
    validator: Any,
) -> str:
    validated = validator(dict(record))
    fence = chr(96) * 3
    return (
        f"\n## {validated[id_field]}\n\n"
        f"{fence}json\n"
        f"{canonical_json(validated).rstrip()}\n"
        f"{fence}\n"
    )


def update_state(
    project_root: str | Path,
    replacement: Mapping[str, Any],
    *,
    expected_state_sha256: str | None = None,
    lock_timeout: float = 5.0,
) -> dict[str, Any]:
    expected_state_sha256 = _require_expected_sha256(
        expected_state_sha256,
        "expected_state_sha256",
    )
    candidate = validate_state(dict(replacement))
    state_dir = _resolve_state_dir(project_root)
    state_path = state_dir / STATE_FILE_NAME
    trace_path = state_dir / TRACE_FILE_NAME
    with workspace_lock(state_dir, timeout=lock_timeout):
        if not _path_is_file(state_path):
            raise ValidationError("state is not initialized; run init first")
        current_text = _read_utf8(state_path)
        current_digest = sha256_bytes(current_text.encode("utf-8"))
        if current_digest != expected_state_sha256:
            raise ConcurrentModificationError(
                f"research state changed: expected {expected_state_sha256}, got {current_digest}"
            )
        current = validate_state(strict_json_loads(current_text, context=str(state_path)))
        ledger_records, question_records, search_runs, judgments, learning_records = (
            _load_support_records(state_dir)
        )
        _assert_support_indexes_consistent(
            current, ledger_records, question_records, search_runs, judgments, learning_records
        )
        _assert_support_indexes_consistent(
            candidate, ledger_records, question_records, search_runs, judgments, learning_records
        )
        trace_records = parse_decision_trace(
            trace_path,
            evidence_ids={item["evidence_id"] for item in ledger_records},
        )
        _validate_route_trace_links(current, trace_records)
        _validate_route_trace_links(candidate, trace_records)
        if candidate["state_revision"] != current["state_revision"] + 1:
            raise ValidationError(
                "replacement state_revision must equal the current revision plus one"
            )
        if candidate["project"]["id"] != current["project"]["id"]:
            raise ValidationError("project.id is immutable in schema v3")
        if candidate["created_at"] != current["created_at"]:
            raise ValidationError("created_at is immutable in schema v3")
        if _parse_timestamp(candidate["updated_at"], "updated_at") < _parse_timestamp(
            current["updated_at"],
            "current.updated_at",
        ):
            raise ValidationError("replacement updated_at precedes the current updated_at")
        new_digest = atomic_write_text(
            state_path,
            canonical_json(candidate),
            expected_digest=current_digest,
        )
    return {
        "status": "pass",
        "mode": "write",
        "state_revision": candidate["state_revision"],
        "state_sha256": new_digest,
    }


def append_evidence(
    project_root: str | Path,
    record: Mapping[str, Any],
    *,
    expected_ledger_sha256: str | None = None,
    expected_state_sha256: str | None = None,
    timestamp: str | None = None,
    lock_timeout: float = 5.0,
) -> dict[str, Any]:
    expected_ledger_sha256 = _require_expected_sha256(
        expected_ledger_sha256,
        "expected_ledger_sha256",
    )
    expected_state_sha256 = _require_expected_sha256(
        expected_state_sha256,
        "expected_state_sha256",
    )
    validated = validate_evidence_record(dict(record))
    state_dir = _resolve_state_dir(project_root)
    state_path = state_dir / STATE_FILE_NAME
    ledger_path = state_dir / EVIDENCE_FILE_NAME
    questions_path = state_dir / QUESTIONS_FILE_NAME
    trace_path = state_dir / TRACE_FILE_NAME
    with workspace_lock(state_dir, timeout=lock_timeout):
        current_state_text = _read_utf8(state_path)
        state_digest = sha256_bytes(current_state_text.encode("utf-8"))
        if state_digest != expected_state_sha256:
            raise ConcurrentModificationError(
                f"research state changed: expected {expected_state_sha256}, got {state_digest}"
            )
        current_state = validate_state(
            strict_json_loads(current_state_text, context=str(state_path))
        )
        current_ledger_text = _read_utf8(ledger_path)
        ledger_digest = sha256_bytes(current_ledger_text.encode("utf-8"))
        if ledger_digest != expected_ledger_sha256:
            raise ConcurrentModificationError(
                f"evidence ledger changed: expected {expected_ledger_sha256}, got {ledger_digest}"
            )
        ledger_records = _parse_fenced_record_text(
            current_ledger_text,
            header=EVIDENCE_HEADER,
            id_field="evidence_id",
            validator=validate_evidence_record,
            record_kind="evidence record",
        )
        question_records = parse_open_questions(questions_path)
        search_runs, judgments = parse_expert_experience_ledger(
            state_dir / EXPERT_FILE_NAME
        )
        learning_records = parse_learning_ledger(state_dir / LEARNING_FILE_NAME)
        _assert_support_indexes_consistent(
            current_state,
            ledger_records,
            question_records,
            search_runs,
            judgments,
            learning_records,
        )
        trace_records = parse_decision_trace(
            trace_path,
            evidence_ids={item["evidence_id"] for item in ledger_records},
        )
        _validate_route_trace_links(current_state, trace_records)
        if validated["evidence_id"] in {item["evidence_id"] for item in ledger_records}:
            raise DuplicateRecordError(f"duplicate evidence_id: {validated['evidence_id']}")

        next_state = strict_json_loads(canonical_json(current_state), context="state copy")
        next_state["evidence_index"].append(validated)
        next_state["state_revision"] += 1
        next_state["updated_at"] = timestamp or utc_now()
        validate_state(next_state)
        next_ledger_text = current_ledger_text + _render_fenced_record(
            validated,
            id_field="evidence_id",
            validator=validate_evidence_record,
        )
        ledger_new_digest, state_new_digest = _commit_two_files_with_rollback(
            ledger_path,
            current_ledger_text,
            next_ledger_text,
            state_path,
            current_state_text,
            canonical_json(next_state),
        )
    return {
        "status": "pass",
        "mode": "write",
        "evidence_id": validated["evidence_id"],
        "state_revision": next_state["state_revision"],
        "ledger_sha256": ledger_new_digest,
        "state_sha256": state_new_digest,
    }


def append_question(
    project_root: str | Path,
    record: Mapping[str, Any],
    *,
    expected_questions_sha256: str | None = None,
    expected_state_sha256: str | None = None,
    timestamp: str | None = None,
    lock_timeout: float = 5.0,
) -> dict[str, Any]:
    expected_questions_sha256 = _require_expected_sha256(
        expected_questions_sha256,
        "expected_questions_sha256",
    )
    expected_state_sha256 = _require_expected_sha256(
        expected_state_sha256,
        "expected_state_sha256",
    )
    validated = validate_open_question(dict(record))
    state_dir = _resolve_state_dir(project_root)
    state_path = state_dir / STATE_FILE_NAME
    ledger_path = state_dir / EVIDENCE_FILE_NAME
    questions_path = state_dir / QUESTIONS_FILE_NAME
    trace_path = state_dir / TRACE_FILE_NAME
    with workspace_lock(state_dir, timeout=lock_timeout):
        current_state_text = _read_utf8(state_path)
        state_digest = sha256_bytes(current_state_text.encode("utf-8"))
        if state_digest != expected_state_sha256:
            raise ConcurrentModificationError(
                f"research state changed: expected {expected_state_sha256}, got {state_digest}"
            )
        current_state = validate_state(
            strict_json_loads(current_state_text, context=str(state_path))
        )
        current_questions_text = _read_utf8(questions_path)
        questions_digest = sha256_bytes(current_questions_text.encode("utf-8"))
        if questions_digest != expected_questions_sha256:
            raise ConcurrentModificationError(
                f"open questions changed: expected {expected_questions_sha256}, "
                f"got {questions_digest}"
            )
        question_records = _parse_fenced_record_text(
            current_questions_text,
            header=QUESTIONS_HEADER,
            id_field="question_id",
            validator=validate_open_question,
            record_kind="open question",
        )
        ledger_records = parse_evidence_ledger(ledger_path)
        search_runs, judgments = parse_expert_experience_ledger(
            state_dir / EXPERT_FILE_NAME
        )
        learning_records = parse_learning_ledger(state_dir / LEARNING_FILE_NAME)
        _assert_support_indexes_consistent(
            current_state,
            ledger_records,
            question_records,
            search_runs,
            judgments,
            learning_records,
        )
        trace_records = parse_decision_trace(
            trace_path,
            evidence_ids={item["evidence_id"] for item in ledger_records},
        )
        _validate_route_trace_links(current_state, trace_records)
        if validated["question_id"] in {item["question_id"] for item in question_records}:
            raise DuplicateRecordError(f"duplicate question_id: {validated['question_id']}")

        next_state = strict_json_loads(canonical_json(current_state), context="state copy")
        next_state["open_questions"].append(validated["question_id"])
        next_state["state_revision"] += 1
        next_state["updated_at"] = timestamp or utc_now()
        validate_state(next_state)
        next_questions_text = current_questions_text + _render_fenced_record(
            validated,
            id_field="question_id",
            validator=validate_open_question,
        )
        questions_new_digest, state_new_digest = _commit_two_files_with_rollback(
            questions_path,
            current_questions_text,
            next_questions_text,
            state_path,
            current_state_text,
            canonical_json(next_state),
        )
    return {
        "status": "pass",
        "mode": "write",
        "question_id": validated["question_id"],
        "state_revision": next_state["state_revision"],
        "questions_sha256": questions_new_digest,
        "state_sha256": state_new_digest,
    }


def _assert_sources_verified(
    source_ids: Sequence[str],
    evidence_records: Sequence[Mapping[str, Any]],
    *,
    context: str,
) -> None:
    evidence_by_id = {item["evidence_id"]: item for item in evidence_records}
    unknown = sorted(set(source_ids) - set(evidence_by_id))
    if unknown:
        raise ValidationError(f"{context} references unknown evidence IDs: {unknown}")
    unacceptable = sorted(
        evidence_id
        for evidence_id in source_ids
        if evidence_by_id[evidence_id]["access_status"] != "available"
        or evidence_by_id[evidence_id]["verification_status"]
        not in {"verified", "alternate_verified"}
    )
    if unacceptable:
        raise ValidationError(
            f"{context} cites sources that are not accessible and verified: {unacceptable}"
        )


def append_search_run(
    project_root: str | Path,
    record: Mapping[str, Any],
    *,
    expected_expert_ledger_sha256: str | None = None,
    expected_state_sha256: str | None = None,
    timestamp: str | None = None,
    lock_timeout: float = 5.0,
) -> dict[str, Any]:
    expected_expert_ledger_sha256 = _require_expected_sha256(
        expected_expert_ledger_sha256,
        "expected_expert_ledger_sha256",
    )
    expected_state_sha256 = _require_expected_sha256(
        expected_state_sha256,
        "expected_state_sha256",
    )
    validated = validate_search_run(dict(record))
    state_dir = _resolve_state_dir(project_root)
    state_path = state_dir / STATE_FILE_NAME
    expert_path = state_dir / EXPERT_FILE_NAME
    with workspace_lock(state_dir, timeout=lock_timeout):
        current_state_text = _read_utf8(state_path)
        current_expert_text = _read_utf8(expert_path)
        state_digest = sha256_bytes(current_state_text.encode("utf-8"))
        expert_digest = sha256_bytes(current_expert_text.encode("utf-8"))
        if state_digest != expected_state_sha256:
            raise ConcurrentModificationError(
                f"research state changed: expected {expected_state_sha256}, got {state_digest}"
            )
        if expert_digest != expected_expert_ledger_sha256:
            raise ConcurrentModificationError(
                "expert experience ledger changed: expected "
                f"{expected_expert_ledger_sha256}, got {expert_digest}"
            )
        current_state = validate_state(
            strict_json_loads(current_state_text, context=str(state_path))
        )
        ledger_records = parse_evidence_ledger(state_dir / EVIDENCE_FILE_NAME)
        question_records = parse_open_questions(state_dir / QUESTIONS_FILE_NAME)
        search_runs, judgments = _parse_expert_experience_text(current_expert_text)
        learning_records = parse_learning_ledger(state_dir / LEARNING_FILE_NAME)
        _assert_support_indexes_consistent(
            current_state,
            ledger_records,
            question_records,
            search_runs,
            judgments,
            learning_records,
        )
        trace_records = parse_decision_trace(
            state_dir / TRACE_FILE_NAME,
            evidence_ids={item["evidence_id"] for item in ledger_records},
        )
        _validate_route_trace_links(current_state, trace_records)
        if validated["domain"] != current_state["domain"]:
            raise ValidationError("search run domain differs from current project domain")
        all_ids = {item["search_run_id"] for item in search_runs} | {
            item["expert_judgment_id"] for item in judgments
        }
        if validated["search_run_id"] in all_ids:
            raise DuplicateRecordError(
                f"duplicate expert ledger record ID: {validated['search_run_id']}"
            )
        _assert_sources_verified(
            validated["source_evidence_ids"],
            ledger_records,
            context=f"search run {validated['search_run_id']}",
        )

        next_state = strict_json_loads(canonical_json(current_state), context="state copy")
        next_state["search_runs"].append(validated)
        next_state["state_revision"] += 1
        next_state["updated_at"] = timestamp or utc_now()
        validate_state(next_state)
        next_expert_text = current_expert_text + _render_fenced_record(
            validated,
            id_field="search_run_id",
            validator=validate_search_run,
        )
        expert_new_digest, state_new_digest = _commit_two_files_with_rollback(
            expert_path,
            current_expert_text,
            next_expert_text,
            state_path,
            current_state_text,
            canonical_json(next_state),
        )
    return {
        "status": "pass",
        "mode": "write",
        "operation": "append_search_run",
        "search_run_id": validated["search_run_id"],
        "state_revision": next_state["state_revision"],
        "expert_ledger_sha256": expert_new_digest,
        "state_sha256": state_new_digest,
    }


def append_expert_judgment(
    project_root: str | Path,
    record: Mapping[str, Any],
    *,
    expected_expert_ledger_sha256: str | None = None,
    expected_state_sha256: str | None = None,
    timestamp: str | None = None,
    lock_timeout: float = 5.0,
) -> dict[str, Any]:
    expected_expert_ledger_sha256 = _require_expected_sha256(
        expected_expert_ledger_sha256,
        "expected_expert_ledger_sha256",
    )
    expected_state_sha256 = _require_expected_sha256(
        expected_state_sha256,
        "expected_state_sha256",
    )
    validated = validate_expert_judgment(dict(record))
    state_dir = _resolve_state_dir(project_root)
    state_path = state_dir / STATE_FILE_NAME
    expert_path = state_dir / EXPERT_FILE_NAME
    with workspace_lock(state_dir, timeout=lock_timeout):
        current_state_text = _read_utf8(state_path)
        current_expert_text = _read_utf8(expert_path)
        state_digest = sha256_bytes(current_state_text.encode("utf-8"))
        expert_digest = sha256_bytes(current_expert_text.encode("utf-8"))
        if state_digest != expected_state_sha256:
            raise ConcurrentModificationError(
                f"research state changed: expected {expected_state_sha256}, got {state_digest}"
            )
        if expert_digest != expected_expert_ledger_sha256:
            raise ConcurrentModificationError(
                "expert experience ledger changed: expected "
                f"{expected_expert_ledger_sha256}, got {expert_digest}"
            )
        current_state = validate_state(
            strict_json_loads(current_state_text, context=str(state_path))
        )
        ledger_records = parse_evidence_ledger(state_dir / EVIDENCE_FILE_NAME)
        question_records = parse_open_questions(state_dir / QUESTIONS_FILE_NAME)
        search_runs, judgments = _parse_expert_experience_text(current_expert_text)
        learning_records = parse_learning_ledger(state_dir / LEARNING_FILE_NAME)
        _assert_support_indexes_consistent(
            current_state,
            ledger_records,
            question_records,
            search_runs,
            judgments,
            learning_records,
        )
        trace_records = parse_decision_trace(
            state_dir / TRACE_FILE_NAME,
            evidence_ids={item["evidence_id"] for item in ledger_records},
        )
        _validate_route_trace_links(current_state, trace_records)
        all_ids = {item["search_run_id"] for item in search_runs} | {
            item["expert_judgment_id"] for item in judgments
        }
        if validated["expert_judgment_id"] in all_ids:
            raise DuplicateRecordError(
                "duplicate expert ledger record ID: "
                f"{validated['expert_judgment_id']}"
            )
        run_by_id = {item["search_run_id"]: item for item in search_runs}
        run = run_by_id.get(validated["search_run_id"])
        if run is None:
            raise ValidationError(
                f"expert judgment references unknown search run {validated['search_run_id']}"
            )
        if validated["decision_id"] != run["decision_id"]:
            raise ValidationError("expert judgment decision differs from its search run")
        outside_run = sorted(
            set(validated["source_evidence_ids"])
            - set(run["source_evidence_ids"])
        )
        if outside_run:
            raise ValidationError(
                f"expert judgment cites sources outside its search run: {outside_run}"
            )
        _assert_sources_verified(
            validated["source_evidence_ids"],
            ledger_records,
            context=f"expert judgment {validated['expert_judgment_id']}",
        )

        next_state = strict_json_loads(canonical_json(current_state), context="state copy")
        next_state["expert_judgment_index"].append(validated)
        next_state["state_revision"] += 1
        next_state["updated_at"] = timestamp or utc_now()
        validate_state(next_state)
        next_expert_text = current_expert_text + _render_fenced_record(
            validated,
            id_field="expert_judgment_id",
            validator=validate_expert_judgment,
        )
        expert_new_digest, state_new_digest = _commit_two_files_with_rollback(
            expert_path,
            current_expert_text,
            next_expert_text,
            state_path,
            current_state_text,
            canonical_json(next_state),
        )
    return {
        "status": "pass",
        "mode": "write",
        "operation": "append_expert_judgment",
        "expert_judgment_id": validated["expert_judgment_id"],
        "state_revision": next_state["state_revision"],
        "expert_ledger_sha256": expert_new_digest,
        "state_sha256": state_new_digest,
    }


def append_learning_record(
    project_root: str | Path,
    record: Mapping[str, Any],
    *,
    expected_learning_ledger_sha256: str | None = None,
    expected_state_sha256: str | None = None,
    timestamp: str | None = None,
    lock_timeout: float = 5.0,
) -> dict[str, Any]:
    expected_learning_ledger_sha256 = _require_expected_sha256(
        expected_learning_ledger_sha256,
        "expected_learning_ledger_sha256",
    )
    expected_state_sha256 = _require_expected_sha256(
        expected_state_sha256,
        "expected_state_sha256",
    )
    validated = validate_learning_record(dict(record))
    state_dir = _resolve_state_dir(project_root)
    state_path = state_dir / STATE_FILE_NAME
    learning_path = state_dir / LEARNING_FILE_NAME
    with workspace_lock(state_dir, timeout=lock_timeout):
        current_state_text = _read_utf8(state_path)
        current_learning_text = _read_utf8(learning_path)
        state_digest = sha256_bytes(current_state_text.encode("utf-8"))
        learning_digest = sha256_bytes(current_learning_text.encode("utf-8"))
        if state_digest != expected_state_sha256:
            raise ConcurrentModificationError(
                f"research state changed: expected {expected_state_sha256}, got {state_digest}"
            )
        if learning_digest != expected_learning_ledger_sha256:
            raise ConcurrentModificationError(
                "learning ledger changed: expected "
                f"{expected_learning_ledger_sha256}, got {learning_digest}"
            )
        current_state = validate_state(
            strict_json_loads(current_state_text, context=str(state_path))
        )
        ledger_records = parse_evidence_ledger(state_dir / EVIDENCE_FILE_NAME)
        question_records = parse_open_questions(state_dir / QUESTIONS_FILE_NAME)
        search_runs, judgments = parse_expert_experience_ledger(
            state_dir / EXPERT_FILE_NAME
        )
        learning_records = _parse_fenced_record_text(
            current_learning_text,
            header=LEARNING_HEADER,
            id_field="learning_record_id",
            validator=validate_learning_record,
            record_kind="learning record",
        )
        _assert_support_indexes_consistent(
            current_state,
            ledger_records,
            question_records,
            search_runs,
            judgments,
            learning_records,
        )
        existing_ids = {item["learning_record_id"] for item in learning_records}
        if validated["learning_record_id"] in existing_ids:
            raise DuplicateRecordError(
                f"duplicate learning_record_id: {validated['learning_record_id']}"
            )
        if validated["domain"] != current_state["domain"]:
            raise ValidationError("learning record domain differs from current project domain")

        next_state = strict_json_loads(canonical_json(current_state), context="state copy")
        next_state["learning_record_index"].append(validated)
        next_state["state_revision"] += 1
        next_state["updated_at"] = timestamp or utc_now()
        validate_state(next_state)
        next_learning_text = current_learning_text + _render_fenced_record(
            validated,
            id_field="learning_record_id",
            validator=validate_learning_record,
        )
        learning_new_digest, state_new_digest = _commit_two_files_with_rollback(
            learning_path,
            current_learning_text,
            next_learning_text,
            state_path,
            current_state_text,
            canonical_json(next_state),
        )
    return {
        "status": "pass",
        "mode": "write",
        "operation": "append_learning_record",
        "learning_record_id": validated["learning_record_id"],
        "state_revision": next_state["state_revision"],
        "learning_ledger_sha256": learning_new_digest,
        "state_sha256": state_new_digest,
    }


def parse_decision_trace_text(
    text: str,
    *,
    evidence_ids: set[str] | None = None,
) -> list[dict[str, Any]]:
    if not text.startswith(TRACE_HEADER):
        raise CorruptStateError("decision trace has an unknown or damaged header")
    fence = re.escape(chr(96) * 3)
    block_pattern = re.compile(
        rf"\n## (?P<record_id>[A-Za-z0-9][A-Za-z0-9._:-]*)\n\n"
        rf"{fence}json\n(?P<body>.*?)\n{fence}\n",
        re.DOTALL,
    )
    records: list[dict[str, Any]] = []
    position = len(TRACE_HEADER)
    seen_ids: set[str] = set()
    while position < len(text):
        match = block_pattern.match(text, position)
        if match is None:
            snippet = text[position : position + 80].replace("\n", "\\n")
            raise CorruptStateError(f"invalid decision trace content near: {snippet!r}")
        record = strict_json_loads(match.group("body"), context=f"record {match.group('record_id')}")
        validate_decision_record(record, f"record {match.group('record_id')}")
        record_id = record["decision_record_id"]
        if record_id != match.group("record_id"):
            raise ValidationError(
                f"record heading {match.group('record_id')} does not match decision_record_id {record_id}"
            )
        if record_id in seen_ids:
            raise DuplicateRecordError(f"duplicate decision_record_id: {record_id}")
        supersedes = record["supersedes"]
        if supersedes is not None and supersedes not in seen_ids:
            raise ValidationError(
                f"record {record_id} supersedes unknown or later record {supersedes}"
            )
        if evidence_ids is not None:
            referenced = set(record["evidence_for"]) | set(record["evidence_against"])
            unknown = sorted(referenced - evidence_ids)
            if unknown:
                raise ValidationError(
                    f"record {record_id} references unknown evidence IDs: {unknown}"
                )
        records.append(record)
        seen_ids.add(record_id)
        position = match.end()
    return records


def parse_decision_trace(
    path: str | Path,
    *,
    evidence_ids: set[str] | None = None,
) -> list[dict[str, Any]]:
    trace_path = Path(path)
    try:
        text = trace_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise CorruptStateError(f"{trace_path} is not valid UTF-8") from exc
    except OSError as exc:
        raise ReadOnlyStateError(f"cannot read {trace_path}: {exc}") from exc
    return parse_decision_trace_text(text, evidence_ids=evidence_ids)


def _parse_legacy_decision_trace_text(
    text: str,
    *,
    evidence_ids: set[str],
) -> list[dict[str, Any]]:
    if not text.startswith(LEGACY_TRACE_HEADER):
        raise CorruptStateError("legacy decision trace has an unknown or damaged header")
    fence = re.escape(chr(96) * 3)
    block_pattern = re.compile(
        rf"\n## (?P<record_id>[A-Za-z0-9][A-Za-z0-9._:-]*)\n\n"
        rf"{fence}json\n(?P<body>.*?)\n{fence}\n",
        re.DOTALL,
    )
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    position = len(LEGACY_TRACE_HEADER)
    while position < len(text):
        match = block_pattern.match(text, position)
        if match is None:
            raise CorruptStateError("legacy decision trace content is malformed")
        record = strict_json_loads(
            match.group("body"), context=f"legacy record {match.group('record_id')}"
        )
        validate_legacy_decision_record_v1(record)
        record_id = record["decision_record_id"]
        if record_id != match.group("record_id") or record_id in seen:
            raise ValidationError("legacy decision trace contains an invalid record identity")
        referenced = set(record["evidence_for"]) | set(record["evidence_against"])
        unknown = sorted(referenced - evidence_ids)
        if unknown:
            raise ValidationError(
                f"legacy record {record_id} references unknown evidence IDs: {unknown}"
            )
        if record["supersedes"] is not None and record["supersedes"] not in seen:
            raise ValidationError(
                f"legacy record {record_id} supersedes an unknown or later record"
            )
        records.append(record)
        seen.add(record_id)
        position = match.end()
    return records


def _validate_legacy_workspace_files(
    legacy_state: Mapping[str, Any],
    trace_path: Path,
    evidence_path: Path,
    questions_path: Path,
) -> dict[str, Any]:
    evidence_records = _parse_fenced_record_text(
        _read_utf8(evidence_path),
        header=LEGACY_EVIDENCE_HEADER,
        id_field="evidence_id",
        validator=validate_legacy_evidence_record_v1,
        record_kind="legacy evidence record",
    )
    validate_legacy_evidence_collection_v1(
        evidence_records, context="legacy evidence ledger"
    )
    questions = _parse_fenced_record_text(
        _read_utf8(questions_path),
        header=LEGACY_QUESTIONS_HEADER,
        id_field="question_id",
        validator=validate_open_question,
        record_kind="legacy open question",
    )
    if list(legacy_state["evidence_index"]) != evidence_records:
        raise ValidationError("legacy evidence index differs from its ledger")
    if list(legacy_state["open_questions"]) != [item["question_id"] for item in questions]:
        raise ValidationError("legacy open-question index differs from its ledger")
    trace_records = _parse_legacy_decision_trace_text(
        _read_utf8(trace_path),
        evidence_ids={item["evidence_id"] for item in evidence_records},
    )
    return {
        "trace_records": trace_records,
        "evidence_records": evidence_records,
        "question_records": questions,
    }


def append_decision(
    project_root: str | Path,
    record: Mapping[str, Any],
    *,
    expected_trace_sha256: str | None = None,
    lock_timeout: float = 5.0,
) -> dict[str, Any]:
    expected_trace_sha256 = _require_expected_sha256(
        expected_trace_sha256,
        "expected_trace_sha256",
    )
    validated = validate_decision_record(dict(record))
    state_dir = _resolve_state_dir(project_root)
    state_path = state_dir / STATE_FILE_NAME
    trace_path = state_dir / TRACE_FILE_NAME
    ledger_path = state_dir / EVIDENCE_FILE_NAME
    questions_path = state_dir / QUESTIONS_FILE_NAME
    with workspace_lock(state_dir, timeout=lock_timeout):
        if not _path_exists(state_path) or not _path_exists(trace_path):
            raise ValidationError("state is not initialized; run init first")
        state = load_state(state_path)
        ledger_records = parse_evidence_ledger(ledger_path)
        question_records = parse_open_questions(questions_path)
        search_runs, judgments = parse_expert_experience_ledger(
            state_dir / EXPERT_FILE_NAME
        )
        learning_records = parse_learning_ledger(state_dir / LEARNING_FILE_NAME)
        _assert_support_indexes_consistent(
            state, ledger_records, question_records, search_runs, judgments, learning_records
        )
        if validated["domain"] != state["domain"]:
            raise ValidationError("decision record domain differs from current project domain")
        _validate_decision_experience_links(
            validated, search_runs, judgments, ledger_records
        )
        _validate_decision_learning_links(validated, learning_records)
        evidence_ids = {item["evidence_id"] for item in state["evidence_index"]}
        try:
            current_text = trace_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise CorruptStateError(f"{trace_path} is not valid UTF-8") from exc
        except OSError as exc:
            raise ReadOnlyStateError(f"cannot read {trace_path}: {exc}") from exc
        current_digest = sha256_bytes(current_text.encode("utf-8"))
        if current_digest != expected_trace_sha256:
            raise ConcurrentModificationError(
                f"decision trace changed: expected {expected_trace_sha256}, got {current_digest}"
            )
        records = parse_decision_trace_text(current_text, evidence_ids=evidence_ids)
        _validate_route_trace_links(state, records)
        record_ids = {item["decision_record_id"] for item in records}
        if validated["decision_record_id"] in record_ids:
            raise DuplicateRecordError(
                f"duplicate decision_record_id: {validated['decision_record_id']}"
            )
        if validated["supersedes"] is not None and validated["supersedes"] not in record_ids:
            raise ValidationError(
                f"supersedes references unknown record: {validated['supersedes']}"
            )
        referenced = set(validated["evidence_for"]) | set(validated["evidence_against"])
        unknown = sorted(referenced - evidence_ids)
        if unknown:
            raise ValidationError(f"record references unknown evidence IDs: {unknown}")
        updated_text = current_text + render_decision_record(validated)
        new_digest = atomic_write_text(
            trace_path,
            updated_text,
            expected_digest=current_digest,
        )
    return {
        "status": "pass",
        "mode": "write",
        "operation": "lifecycle_append_only",
        "current_route_updated": False,
        "decision_record_id": validated["decision_record_id"],
        "trace_sha256": new_digest,
        "record_count": len(records) + 1,
    }


def _validate_route_trace_links(
    state_value: Mapping[str, Any],
    records: Sequence[Mapping[str, Any]],
) -> None:
    records_by_id = {record["decision_record_id"]: record for record in records}
    for record in records:
        if record["domain"] != state_value["domain"]:
            raise ValidationError(
                f"decision record {record['decision_record_id']} has a different domain"
            )
        _validate_decision_experience_links(
            record,
            state_value["search_runs"],
            state_value["expert_judgment_index"],
            state_value["evidence_index"],
        )
        _validate_decision_learning_links(
            record,
            state_value["learning_record_index"],
        )
    current_route = state_value["current_route"]
    if current_route is not None:
        route_record_id = current_route["decision_record_id"]
        if route_record_id not in records_by_id:
            raise ValidationError(
                f"current_route references missing decision record {route_record_id}"
            )
        route_primary = current_route["route"]["primary_decision"]
        record_decision = records_by_id[route_record_id]["decision_id"]
        if route_primary != record_decision:
            raise ValidationError(
                f"current_route primary {route_primary} does not match "
                f"record {route_record_id} decision {record_decision}"
            )
    for item in state_value["revisit_queue"]:
        record_id = item["decision_record_id"]
        if record_id not in records_by_id:
            raise ValidationError(
                f"revisit_queue references missing decision record {record_id}"
            )


def _validate_decision_experience_links(
    record: Mapping[str, Any],
    search_runs: Sequence[Mapping[str, Any]],
    judgments: Sequence[Mapping[str, Any]],
    evidence_records: Sequence[Mapping[str, Any]] | None = None,
) -> None:
    runs_by_id = {item["search_run_id"]: item for item in search_runs}
    judgments_by_id = {
        item["expert_judgment_id"]: item for item in judgments
    }
    missing_runs = sorted(set(record["search_run_ids"]) - set(runs_by_id))
    if missing_runs:
        raise ValidationError(
            f"decision record references unknown search run IDs: {missing_runs}"
        )
    missing_judgments = sorted(
        set(record["expert_judgment_ids"]) - set(judgments_by_id)
    )
    if missing_judgments:
        raise ValidationError(
            f"decision record references unknown expert judgment IDs: {missing_judgments}"
        )
    for run_id in record["search_run_ids"]:
        run = runs_by_id[run_id]
        if run["decision_record_id"] != record["decision_record_id"]:
            raise ValidationError(
                f"search run {run_id} is bound to a different decision record"
            )
        if run["decision_id"] != record["decision_id"]:
            raise ValidationError(
                f"search run {run_id} belongs to a different decision"
            )
        if run["domain"] != record["domain"]:
            raise ValidationError(f"search run {run_id} belongs to a different domain")
    for judgment_id in record["expert_judgment_ids"]:
        judgment = judgments_by_id[judgment_id]
        if judgment["decision_id"] != record["decision_id"]:
            raise ValidationError(
                f"expert judgment {judgment_id} belongs to a different decision"
            )
        if judgment["search_run_id"] not in set(record["search_run_ids"]):
            raise ValidationError(
                f"expert judgment {judgment_id} is outside the decision's search runs"
            )
    if record["decision_support"]["action_status"] == "可直接推进":
        if evidence_records is None:
            raise ValidationError(
                "可直接推进 requires evidence identity and independence validation"
            )
        _validate_direct_advance_requirements(
            record,
            [runs_by_id[run_id] for run_id in record["search_run_ids"]],
            [judgments_by_id[item] for item in record["expert_judgment_ids"]],
            evidence_records,
        )


def _validate_decision_learning_links(
    record: Mapping[str, Any],
    learning_records: Sequence[Mapping[str, Any]],
) -> None:
    learning_by_id = {
        item["learning_record_id"]: item for item in learning_records
    }
    missing = sorted(set(record["learning_record_ids"]) - set(learning_by_id))
    if missing:
        raise ValidationError(
            f"decision record references unknown learning record IDs: {missing}"
        )
    for learning_record_id in record["learning_record_ids"]:
        learning = learning_by_id[learning_record_id]
        if learning["decision_record_id"] != record["decision_record_id"]:
            raise ValidationError(
                f"learning record {learning_record_id} is bound to a different decision record"
            )
        if learning["decision_id"] != record["decision_id"]:
            raise ValidationError(
                f"learning record {learning_record_id} belongs to a different decision"
            )
        if learning["domain"] != record["domain"]:
            raise ValidationError(
                f"learning record {learning_record_id} belongs to a different domain"
            )
        explanation = record["explanation_support"]
        if learning["scaffolding_level"] != explanation["scaffolding_level"]:
            raise ValidationError(
                f"learning record {learning_record_id} scaffolding level differs from the decision summary"
            )
        if learning["understanding_status"] != explanation["understanding_status"]:
            raise ValidationError(
                f"learning record {learning_record_id} understanding status differs from the decision summary"
            )
        if learning["transfer_status"] != explanation["transfer_status"]:
            raise ValidationError(
                f"learning record {learning_record_id} transfer status differs from the decision summary"
            )


def _validate_direct_advance_requirements(
    record: Mapping[str, Any],
    search_runs: Sequence[Mapping[str, Any]],
    judgments: Sequence[Mapping[str, Any]],
    evidence_records: Sequence[Mapping[str, Any]],
) -> None:
    if not judgments:
        raise ValidationError("可直接推进 requires at least one expert judgment")
    if any(run["coverage"] != "sufficient" for run in search_runs):
        raise ValidationError("可直接推进 requires sufficient search coverage")
    if any(run["conflicts"] for run in search_runs):
        raise ValidationError(
            "可直接推进 is not allowed while material search conflicts are recorded"
        )
    if any(
        item["disagreement_status"] != "no_material_disagreement_found"
        for item in judgments
    ):
        raise ValidationError(
            "可直接推进 requires all cited disagreements to be resolved or absent"
        )
    decision_claim_ids = {
        claim_id for run in search_runs for claim_id in run["decision_claim_ids"]
    }
    if not decision_claim_ids:
        raise ValidationError(
            "可直接推进 requires explicit decision-changing claim IDs"
        )
    source_ids = {
        source_id
        for judgment in judgments
        for source_id in judgment["source_evidence_ids"]
    }
    evidence_by_id = {item["evidence_id"]: item for item in evidence_records}
    sources = [evidence_by_id[item] for item in sorted(source_ids)]
    distinct_works = {item["canonical_work_id"] for item in sources}
    distinct_studies = {item["study_id"] for item in sources}
    independent_relationships = all(
        item["relationship"] in {"canonical", "independent_work"} for item in sources
    )
    claim_independence_verified = all(
        decision_claim_ids.issubset(set(item["claim_ids"]))
        and all(
            item["independence_status"].get(claim_id) == "independent"
            and bool(item["independence_basis"].get(claim_id, "").strip())
            for claim_id in decision_claim_ids
        )
        for item in sources
    )
    independently_anchored = (
        len(distinct_works) >= 2
        and len(distinct_studies) >= 2
        and independent_relationships
        and claim_independence_verified
    )
    authority_runs = [
        run for run in search_runs if run["single_authority_exception"]["applied"]
    ]
    explicit_single_authority = False
    if len(sources) == 1 and len(authority_runs) == 1:
        exception = authority_runs[0]["single_authority_exception"]
        identity = sources[0]["source_identity"]
        explicit_single_authority = (
            sources[0]["relationship"] == "canonical"
            and identity["source_type"]
            in {"official_standard", "regulatory_guidance"}
            and exception["authority_kind"] == identity["source_type"]
            and exception["issuer"].strip().casefold()
            == identity["author_or_issuer"].strip().casefold()
            and exception["locator"].strip() == identity["stable_locator"].strip()
            and bool(exception["scope_match"].strip())
            and bool(exception["basis"].strip())
        )
    if not (independently_anchored or explicit_single_authority):
        raise ValidationError(
            "可直接推进 requires two identity-distinct sources or one explicit "
            "controlling-authority exception"
        )


def commit_route(
    project_root: str | Path,
    route: Mapping[str, Any],
    decision_record: Mapping[str, Any],
    *,
    expected_state_sha256: str | None = None,
    expected_trace_sha256: str | None = None,
    timestamp: str | None = None,
    lock_timeout: float = 5.0,
) -> dict[str, Any]:
    expected_state_sha256 = _require_expected_sha256(
        expected_state_sha256,
        "expected_state_sha256",
    )
    expected_trace_sha256 = _require_expected_sha256(
        expected_trace_sha256,
        "expected_trace_sha256",
    )
    candidate_route = validate_router_output(dict(route), context="route")
    candidate_record = validate_decision_record(dict(decision_record))
    if candidate_route["primary_decision"] is None:
        raise ValidationError(
            "commit-route requires a primary decision; abstention leaves current_route null"
        )
    if candidate_route["primary_decision"] != candidate_record["decision_id"]:
        raise ValidationError(
            "route.primary_decision must equal decision_record.decision_id"
        )

    state_dir = _resolve_state_dir(project_root)
    state_path = state_dir / STATE_FILE_NAME
    trace_path = state_dir / TRACE_FILE_NAME
    ledger_path = state_dir / EVIDENCE_FILE_NAME
    questions_path = state_dir / QUESTIONS_FILE_NAME
    with workspace_lock(state_dir, timeout=lock_timeout):
        current_state_text = _read_utf8(state_path)
        current_trace_text = _read_utf8(trace_path)
        current_state_digest = sha256_bytes(current_state_text.encode("utf-8"))
        current_trace_digest = sha256_bytes(current_trace_text.encode("utf-8"))
        if current_state_digest != expected_state_sha256:
            raise ConcurrentModificationError(
                f"research state changed: expected {expected_state_sha256}, "
                f"got {current_state_digest}"
            )
        if current_trace_digest != expected_trace_sha256:
            raise ConcurrentModificationError(
                f"decision trace changed: expected {expected_trace_sha256}, "
                f"got {current_trace_digest}"
            )

        current_state = validate_state(
            strict_json_loads(current_state_text, context=str(state_path))
        )
        ledger_records = parse_evidence_ledger(ledger_path)
        question_records = parse_open_questions(questions_path)
        search_runs, judgments = parse_expert_experience_ledger(
            state_dir / EXPERT_FILE_NAME
        )
        learning_records = parse_learning_ledger(state_dir / LEARNING_FILE_NAME)
        _assert_support_indexes_consistent(
            current_state,
            ledger_records,
            question_records,
            search_runs,
            judgments,
            learning_records,
        )
        if candidate_record["domain"] != current_state["domain"]:
            raise ValidationError("decision record domain differs from current project domain")
        evidence_ids = {item["evidence_id"] for item in ledger_records}
        validate_router_output(
            candidate_route,
            evidence_ids=evidence_ids,
            context="route",
        )
        current_records = parse_decision_trace_text(
            current_trace_text,
            evidence_ids=evidence_ids,
        )
        _validate_route_trace_links(current_state, current_records)
        record_ids = {item["decision_record_id"] for item in current_records}
        if candidate_record["decision_record_id"] in record_ids:
            raise DuplicateRecordError(
                f"duplicate decision_record_id: {candidate_record['decision_record_id']}"
            )
        if (
            candidate_record["supersedes"] is not None
            and candidate_record["supersedes"] not in record_ids
        ):
            raise ValidationError(
                f"supersedes references unknown record: {candidate_record['supersedes']}"
            )
        record_evidence = set(candidate_record["evidence_for"]) | set(
            candidate_record["evidence_against"]
        )
        unknown_record_evidence = sorted(record_evidence - evidence_ids)
        if unknown_record_evidence:
            raise ValidationError(
                f"decision record references unknown evidence IDs: "
                f"{unknown_record_evidence}"
            )
        _validate_decision_experience_links(
            candidate_record,
            search_runs,
            judgments,
            ledger_records,
        )
        _validate_decision_learning_links(candidate_record, learning_records)

        next_state = strict_json_loads(canonical_json(current_state), context="state copy")
        next_state["state_revision"] += 1
        next_state["updated_at"] = timestamp or utc_now()
        next_state["current_route"] = {
            "decision_record_id": candidate_record["decision_record_id"],
            "route": candidate_route,
        }
        superseded_id = candidate_record["supersedes"]
        next_state["revisit_queue"] = [
            item
            for item in next_state["revisit_queue"]
            if item["decision_record_id"]
            not in {candidate_record["decision_record_id"], superseded_id}
        ]
        if candidate_record["revisit_condition"].strip():
            next_state["revisit_queue"].append(
                {
                    "decision_record_id": candidate_record["decision_record_id"],
                    "condition": candidate_record["revisit_condition"],
                }
            )
        validate_state(next_state)
        next_trace_text = current_trace_text + render_decision_record(candidate_record)
        trace_new_digest, state_new_digest = _commit_two_files_with_rollback(
            trace_path,
            current_trace_text,
            next_trace_text,
            state_path,
            current_state_text,
            canonical_json(next_state),
        )

        committed_state = load_state(state_path)
        committed_records = parse_decision_trace(
            trace_path,
            evidence_ids=evidence_ids,
        )
        _validate_route_trace_links(committed_state, committed_records)
    return {
        "status": "pass",
        "mode": "write",
        "operation": "commit_decision_cycle",
        "decision_record_id": candidate_record["decision_record_id"],
        "state_revision": next_state["state_revision"],
        "state_sha256": state_new_digest,
        "trace_sha256": trace_new_digest,
        "record_count": len(current_records) + 1,
    }


# Preferred v3 name; commit_route remains as a compatibility alias for callers.
commit_decision_cycle = commit_route


def validate_workspace(project_root: str | Path) -> dict[str, Any]:
    state_dir = _resolve_state_dir(project_root)
    base_required = {
        STATE_FILE_NAME: state_dir / STATE_FILE_NAME,
        TRACE_FILE_NAME: state_dir / TRACE_FILE_NAME,
        EVIDENCE_FILE_NAME: state_dir / EVIDENCE_FILE_NAME,
        QUESTIONS_FILE_NAME: state_dir / QUESTIONS_FILE_NAME,
    }
    missing = sorted(name for name, path in base_required.items() if not _path_is_file(path))
    if missing:
        raise ValidationError(f"state workspace is missing files: {missing}")
    state, is_legacy = load_state_read_only(base_required[STATE_FILE_NAME])
    if is_legacy:
        if _path_exists(state_dir / LEARNING_FILE_NAME):
            raise ValidationError(
                "mixed legacy/v3 state workspace is not valid; no files were changed"
            )
        result = dict(_load_v2_compat_module().validate_workspace(project_root))
        result["mode"] = "legacy_read_only"
        result["write_status"] = "not_written"
        result["migration"] = "not_available"
        return result
    required = {
        **base_required,
        EXPERT_FILE_NAME: state_dir / EXPERT_FILE_NAME,
        LEARNING_FILE_NAME: state_dir / LEARNING_FILE_NAME,
    }
    missing_v3 = sorted(
        name for name in (EXPERT_FILE_NAME, LEARNING_FILE_NAME)
        if not _path_is_file(required[name])
    )
    if missing_v3:
        raise ValidationError(
            f"state workspace is missing files: {missing_v3}"
        )
    evidence_ids = {item["evidence_id"] for item in state["evidence_index"]}
    records = parse_decision_trace(required[TRACE_FILE_NAME], evidence_ids=evidence_ids)
    ledger_records = parse_evidence_ledger(required[EVIDENCE_FILE_NAME])
    question_records = parse_open_questions(required[QUESTIONS_FILE_NAME])
    search_runs, judgments = parse_expert_experience_ledger(
        required[EXPERT_FILE_NAME]
    )
    learning_records = parse_learning_ledger(required[LEARNING_FILE_NAME])
    _assert_support_indexes_consistent(
        state, ledger_records, question_records, search_runs, judgments, learning_records
    )
    _validate_route_trace_links(state, records)
    return {
        "status": "pass",
        "mode": "read_only",
        "schema_version": state["schema_version"],
        "state_revision": state["state_revision"],
        "decision_record_count": len(records),
        "evidence_count": len(evidence_ids),
        "evidence_ledger_record_count": len(ledger_records),
        "open_question_record_count": len(question_records),
        "search_run_count": len(search_runs),
        "expert_judgment_count": len(judgments),
        "learning_record_count": len(learning_records),
        "files": {
            name: sha256_file(path)
            for name, path in sorted(required.items())
        },
    }


def _blocked_result(exc: Exception) -> dict[str, Any]:
    reason_code = getattr(exc, "reason_code", "io_error")
    files_changed = getattr(exc, "files_changed", False)
    return {
        "status": "blocked",
        "mode": "read_only",
        "reason_code": reason_code,
        "message": str(exc),
        "write_status": "partial" if files_changed else "not_written",
        "trace_status": "not_written",
        "files_changed": files_changed,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="initialize state without overwriting files")
    init_parser.add_argument("project_root")
    init_parser.add_argument("--project-id")
    init_parser.add_argument("--project-name")
    init_parser.add_argument("--goal", default="")
    init_parser.add_argument(
        "--domain",
        choices=sorted(ALL_DOMAINS),
        default="other",
    )
    init_parser.add_argument(
        "--support-status",
        choices=sorted(DOMAIN_SUPPORT_STATUSES),
        default=None,
    )

    validate_parser = subparsers.add_parser("validate", help="validate state and trace read-only")
    validate_parser.add_argument("project_root")

    append_parser = subparsers.add_parser(
        "append",
        aliases=["append-decision", "append-trace"],
        help="append one strict JSON decision record",
    )
    append_parser.add_argument("project_root")
    append_parser.add_argument("--record", required=True, help="path to a strict JSON record")
    append_parser.add_argument("--expected-trace-sha256")

    update_parser = subparsers.add_parser(
        "update-state",
        help="replace state at exactly the next revision",
    )
    update_parser.add_argument("project_root")
    update_parser.add_argument("--state", required=True, help="strict JSON replacement state")
    update_parser.add_argument("--expected-state-sha256")

    evidence_parser = subparsers.add_parser(
        "append-evidence",
        help="append evidence and update the state index",
    )
    evidence_parser.add_argument("project_root")
    evidence_parser.add_argument("--record", required=True, help="strict JSON evidence record")
    evidence_parser.add_argument("--expected-ledger-sha256")
    evidence_parser.add_argument("--expected-state-sha256")

    question_parser = subparsers.add_parser(
        "append-question",
        help="append an open question and update the state index",
    )
    question_parser.add_argument("project_root")
    question_parser.add_argument("--record", required=True, help="strict JSON question record")
    question_parser.add_argument("--expected-questions-sha256")
    question_parser.add_argument("--expected-state-sha256")

    search_parser = subparsers.add_parser(
        "append-search-run",
        help="append one real-time expert-search run and update its state index",
    )
    search_parser.add_argument("project_root")
    search_parser.add_argument("--record", required=True, help="strict JSON search run")
    search_parser.add_argument("--expected-expert-ledger-sha256")
    search_parser.add_argument("--expected-state-sha256")

    judgment_parser = subparsers.add_parser(
        "append-expert-judgment",
        help="append one source-grounded expert judgment and update its state index",
    )
    judgment_parser.add_argument("project_root")
    judgment_parser.add_argument(
        "--record", required=True, help="strict JSON expert judgment"
    )
    judgment_parser.add_argument("--expected-expert-ledger-sha256")
    judgment_parser.add_argument("--expected-state-sha256")

    learning_parser = subparsers.add_parser(
        "append-learning-record",
        help="append one observed explanation-and-transfer record and update its state index",
    )
    learning_parser.add_argument(
        "project_root"
    )
    learning_parser.add_argument(
        "--record", required=True, help="path to a strict JSON learning record"
    )
    learning_parser.add_argument("--expected-learning-ledger-sha256")
    learning_parser.add_argument("--expected-state-sha256")

    commit_parser = subparsers.add_parser(
        "commit-decision-cycle",
        aliases=["commit-route"],
        help="atomically append the final decision-cycle record and make its route current",
    )
    commit_parser.add_argument("project_root")
    commit_parser.add_argument("--route", required=True, help="strict router JSON")
    commit_parser.add_argument("--decision", required=True, help="strict decision record JSON")
    commit_parser.add_argument("--expected-state-sha256")
    commit_parser.add_argument("--expected-trace-sha256")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            result = init_workspace(
                args.project_root,
                project_id=args.project_id,
                project_name=args.project_name,
                research_goal=args.goal,
                domain_name=args.domain,
                domain_support_status=args.support_status,
            )
        elif args.command == "validate":
            result = validate_workspace(args.project_root)
        elif args.command in {"append", "append-decision", "append-trace"}:
            record_path = Path(args.record)
            record = strict_json_loads(
                record_path.read_text(encoding="utf-8"),
                context=str(record_path),
            )
            result = append_decision(
                args.project_root,
                record,
                expected_trace_sha256=args.expected_trace_sha256,
            )
        elif args.command == "update-state":
            state_path = Path(args.state)
            replacement = strict_json_loads(
                state_path.read_text(encoding="utf-8"),
                context=str(state_path),
            )
            result = update_state(
                args.project_root,
                replacement,
                expected_state_sha256=args.expected_state_sha256,
            )
        elif args.command == "append-evidence":
            record_path = Path(args.record)
            record = strict_json_loads(
                record_path.read_text(encoding="utf-8"),
                context=str(record_path),
            )
            result = append_evidence(
                args.project_root,
                record,
                expected_ledger_sha256=args.expected_ledger_sha256,
                expected_state_sha256=args.expected_state_sha256,
            )
        elif args.command == "append-question":
            record_path = Path(args.record)
            record = strict_json_loads(
                record_path.read_text(encoding="utf-8"),
                context=str(record_path),
            )
            result = append_question(
                args.project_root,
                record,
                expected_questions_sha256=args.expected_questions_sha256,
                expected_state_sha256=args.expected_state_sha256,
            )
        elif args.command == "append-search-run":
            record_path = Path(args.record)
            record = strict_json_loads(
                record_path.read_text(encoding="utf-8"),
                context=str(record_path),
            )
            result = append_search_run(
                args.project_root,
                record,
                expected_expert_ledger_sha256=args.expected_expert_ledger_sha256,
                expected_state_sha256=args.expected_state_sha256,
            )
        elif args.command == "append-expert-judgment":
            record_path = Path(args.record)
            record = strict_json_loads(
                record_path.read_text(encoding="utf-8"),
                context=str(record_path),
            )
            result = append_expert_judgment(
                args.project_root,
                record,
                expected_expert_ledger_sha256=args.expected_expert_ledger_sha256,
                expected_state_sha256=args.expected_state_sha256,
            )
        elif args.command == "append-learning-record":
            record_path = Path(args.record)
            record = strict_json_loads(
                record_path.read_text(encoding="utf-8"),
                context=str(record_path),
            )
            result = append_learning_record(
                args.project_root,
                record,
                expected_learning_ledger_sha256=args.expected_learning_ledger_sha256,
                expected_state_sha256=args.expected_state_sha256,
            )
        else:
            route_path = Path(args.route)
            decision_path = Path(args.decision)
            route = strict_json_loads(
                route_path.read_text(encoding="utf-8"),
                context=str(route_path),
            )
            decision = strict_json_loads(
                decision_path.read_text(encoding="utf-8"),
                context=str(decision_path),
            )
            result = commit_route(
                args.project_root,
                route,
                decision,
                expected_state_sha256=args.expected_state_sha256,
                expected_trace_sha256=args.expected_trace_sha256,
            )
    except (ResearchStateError, OSError, UnicodeError) as exc:
        print(json.dumps(_blocked_result(exc), ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
