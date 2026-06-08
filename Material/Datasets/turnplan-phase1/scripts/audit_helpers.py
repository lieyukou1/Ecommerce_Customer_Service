from __future__ import annotations

from audit_rules import build_audit_meta, build_semantic_meta


def enrich_record(record: dict) -> dict:
    enriched = dict(record)
    enriched["semantic_meta"] = record.get("semantic_meta") or build_semantic_meta(record)
    enriched["audit_meta"] = record.get("audit_meta") or build_audit_meta(record)
    return enriched


def enrich_records(records: list[dict]) -> list[dict]:
    return [enrich_record(record) for record in records]
