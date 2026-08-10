"""initial schema

Revision ID: 8383857ac293
Revises:
Create Date: 2026-08-10
"""
from alembic import op
import sqlalchemy as sa

revision = "8383857ac293"
down_revision = None
branch_labels = None
depends_on = None

LIFECYCLE = ("RECEIVED", "DISCOVERED", "ASSESSED", "PREPARED", "PREFLIGHT_PASS", "READY", "PRESTAGED", "APPROVAL_PENDING", "CUTOVER_RUNNING", "VALIDATING", "HYPERCARE", "CLOSED")

def upgrade() -> None:
    op.create_table("tenants", sa.Column("display_name", sa.String(255), nullable=False), sa.Column("tenant_domain", sa.String(255), nullable=False), sa.Column("role", sa.String(16), nullable=False), sa.Column("id", sa.String(36), primary_key=True), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("migration_projects", sa.Column("migration_code", sa.String(32), nullable=False), sa.Column("name", sa.String(255), nullable=False), sa.Column("description", sa.String(1000)), sa.Column("source_tenant_id", sa.String(36), sa.ForeignKey("tenants.id"), nullable=False), sa.Column("target_tenant_id", sa.String(36), sa.ForeignKey("tenants.id"), nullable=False), sa.Column("status", sa.Enum(*LIFECYCLE, name="lifecycle_state"), nullable=False), sa.Column("id", sa.String(36), primary_key=True), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_migration_projects_migration_code", "migration_projects", ["migration_code"], unique=True)
    op.create_table("migration_waves", sa.Column("migration_project_id", sa.String(36), sa.ForeignKey("migration_projects.id"), nullable=False), sa.Column("name", sa.String(255), nullable=False), sa.Column("sequence", sa.Integer(), nullable=False), sa.Column("status", sa.Enum(*LIFECYCLE, name="wave_lifecycle_state"), nullable=False), sa.Column("id", sa.String(36), primary_key=True), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_migration_waves_migration_project_id", "migration_waves", ["migration_project_id"])
    op.create_table("batches", sa.Column("batch_code", sa.String(32), nullable=False), sa.Column("wave_id", sa.String(36), sa.ForeignKey("migration_waves.id"), nullable=False), sa.Column("name", sa.String(255), nullable=False), sa.Column("lifecycle_state", sa.Enum(*LIFECYCLE, name="batch_lifecycle_state"), nullable=False), sa.Column("readiness_status", sa.Enum("READY", "WARNING", "BLOCKED", "NOT_ASSESSED", name="batch_readiness_state"), nullable=False), sa.Column("id", sa.String(36), primary_key=True), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_batches_batch_code", "batches", ["batch_code"]); op.create_index("ix_batches_wave_id", "batches", ["wave_id"])
    op.create_table("evidence", sa.Column("batch_id", sa.String(36), sa.ForeignKey("batches.id"), nullable=False), sa.Column("domain", sa.String(32), nullable=False), sa.Column("tool", sa.String(128), nullable=False), sa.Column("operation_id", sa.String(64), nullable=False), sa.Column("assessment_id", sa.String(64)), sa.Column("affected_resource", sa.String(255)), sa.Column("input_parameters", sa.Text()), sa.Column("normalized_result", sa.Text()), sa.Column("raw_output", sa.Text()), sa.Column("status", sa.String(16), nullable=False), sa.Column("duration_ms", sa.Integer()), sa.Column("id", sa.String(36), primary_key=True), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_evidence_batch_id", "evidence", ["batch_id"]); op.create_index("ix_evidence_operation_id", "evidence", ["operation_id"]); op.create_index("ix_evidence_assessment_id", "evidence", ["assessment_id"])
    op.create_table("resources", sa.Column("batch_id", sa.String(36), sa.ForeignKey("batches.id"), nullable=False), sa.Column("resource_type", sa.String(32), nullable=False), sa.Column("display_name", sa.String(255), nullable=False), sa.Column("source_identifier", sa.String(255), nullable=False), sa.Column("target_identifier", sa.String(255)), sa.Column("id", sa.String(36), primary_key=True), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_resources_batch_id", "resources", ["batch_id"])
    op.create_table("exceptions", sa.Column("batch_id", sa.String(36), sa.ForeignKey("batches.id"), nullable=False), sa.Column("domain", sa.String(32), nullable=False), sa.Column("code", sa.String(64), nullable=False), sa.Column("description", sa.String(500)), sa.Column("severity", sa.Enum("INFO", "WARNING", "BLOCKING", name="exception_severity"), nullable=False), sa.Column("status", sa.Enum("OPEN", "ACKNOWLEDGED", "RESOLVED", name="exception_status"), nullable=False), sa.Column("evidence_id", sa.String(36), sa.ForeignKey("evidence.id")), sa.Column("affected_resource", sa.String(255)), sa.Column("owner", sa.String(255)), sa.Column("id", sa.String(36), primary_key=True), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_exceptions_batch_id", "exceptions", ["batch_id"])

def downgrade() -> None:
    op.drop_index("ix_exceptions_batch_id", table_name="exceptions"); op.drop_table("exceptions"); op.drop_index("ix_resources_batch_id", table_name="resources"); op.drop_table("resources"); op.drop_index("ix_evidence_assessment_id", table_name="evidence"); op.drop_index("ix_evidence_operation_id", table_name="evidence"); op.drop_index("ix_evidence_batch_id", table_name="evidence"); op.drop_table("evidence"); op.drop_index("ix_batches_wave_id", table_name="batches"); op.drop_index("ix_batches_batch_code", table_name="batches"); op.drop_table("batches"); op.drop_index("ix_migration_waves_migration_project_id", table_name="migration_waves"); op.drop_table("migration_waves"); op.drop_index("ix_migration_projects_migration_code", table_name="migration_projects"); op.drop_table("migration_projects"); op.drop_table("tenants")
