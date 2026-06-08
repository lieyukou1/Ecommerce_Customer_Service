from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
DATASET_ROOT = REPO_ROOT / "Material" / "Datasets" / "turnplan-phase1"
CANONICAL_LLM_DIR = DATASET_ROOT / "canonical_llm"
TRIAGE_OUTPUT_DIR = DATASET_ROOT / "reduced_round04_triage_v1"
KEEP_BASE_OUTPUT_DIR = DATASET_ROOT / "reduced_round04_keep_base_v1"
DATASET_SCRIPTS_DIR = DATASET_ROOT / "scripts"

KEEP_BUCKETS = (
    "task_interrupt_resume_cancel",
    "work_order_business_urge",
    "work_order_business_complaint",
)
TARGETED_FIX_BUCKETS = (
    "active_task_slot_fill",
)
BUCKET_REBUILD_BUCKETS = (
    "ambiguous_all_null",
    "directive_exit_runtime",
)
TRIAGE_BUCKETS = KEEP_BUCKETS + TARGETED_FIX_BUCKETS + BUCKET_REBUILD_BUCKETS

CATEGORY_KEEP = "keep"
CATEGORY_TARGETED_FIX = "targeted_fix"
CATEGORY_BUCKET_REBUILD = "bucket_rebuild"

CATEGORY_DESCRIPTIONS = {
    CATEGORY_KEEP: "Audit-clean and structurally aligned rows that can stay as the next reduced training base.",
    CATEGORY_TARGETED_FIX: "Rows that are on the right task line but still need focused repair before final training.",
    CATEGORY_BUCKET_REBUILD: "Systemically noisy buckets that should be rebuilt as a group instead of patched row by row.",
}

BUCKET_CLASSIFICATION_RULES = {
    "task_interrupt_resume_cancel": CATEGORY_KEEP,
    "work_order_business_urge": CATEGORY_KEEP,
    "work_order_business_complaint": CATEGORY_KEEP,
    "active_task_slot_fill": CATEGORY_TARGETED_FIX,
    "ambiguous_all_null": CATEGORY_BUCKET_REBUILD,
    "directive_exit_runtime": CATEGORY_BUCKET_REBUILD,
}
