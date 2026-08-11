"""phase 2 assessments and audit

Revision ID: 76945f6872d3
Revises: 8383857ac293
Create Date: 2026-08-11 01:03:02.968811
"""
from alembic import op
import sqlalchemy as sa

revision = '76945f6872d3'
down_revision = '8383857ac293'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('audit_events',
        sa.Column('event_type', sa.String(length=64), nullable=False),
        sa.Column('entity_type', sa.String(length=32), nullable=False),
        sa.Column('entity_id', sa.String(length=36), nullable=False),
        sa.Column('migration_id', sa.String(length=36), nullable=True),
        sa.Column('batch_id', sa.String(length=36), nullable=True),
        sa.Column('run_id', sa.String(length=64), nullable=True),
        sa.Column('operation_id', sa.String(length=64), nullable=True),
        sa.Column('detail', sa.Text(), nullable=True),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_events_batch_id'), 'audit_events', ['batch_id'], unique=False)
    op.create_index(op.f('ix_audit_events_entity_id'), 'audit_events', ['entity_id'], unique=False)
    op.create_index(op.f('ix_audit_events_event_type'), 'audit_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_audit_events_migration_id'), 'audit_events', ['migration_id'], unique=False)
    op.create_index(op.f('ix_audit_events_run_id'), 'audit_events', ['run_id'], unique=False)
    op.create_table('assessments',
        sa.Column('run_id', sa.String(length=64), nullable=False),
        sa.Column('batch_id', sa.String(length=36), nullable=False),
        sa.Column('requested_domains', sa.Text(), nullable=False),
        sa.Column('force_refresh', sa.Boolean(), nullable=False),
        sa.Column('run_status', sa.String(length=16), nullable=False),
        sa.Column('overall_status', sa.String(length=16), nullable=True),
        sa.Column('can_proceed', sa.Boolean(), nullable=True),
        sa.Column('blocker_count', sa.Integer(), nullable=False),
        sa.Column('warning_count', sa.Integer(), nullable=False),
        sa.Column('completed_at', sa.String(length=64), nullable=True),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['batch_id'], ['batches.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_assessments_batch_id'), 'assessments', ['batch_id'], unique=False)
    op.create_index(op.f('ix_assessments_run_id'), 'assessments', ['run_id'], unique=True)
    op.create_table('assessment_results',
        sa.Column('assessment_id', sa.String(length=36), nullable=False),
        sa.Column('batch_id', sa.String(length=36), nullable=False),
        sa.Column('domain', sa.String(length=32), nullable=False),
        sa.Column('assessment_version', sa.String(length=16), nullable=False),
        sa.Column('status', sa.String(length=16), nullable=False),
        sa.Column('evaluated_resources', sa.Integer(), nullable=False),
        sa.Column('ready', sa.Integer(), nullable=False),
        sa.Column('warning', sa.Integer(), nullable=False),
        sa.Column('blocked', sa.Integer(), nullable=False),
        sa.Column('can_proceed', sa.Boolean(), nullable=False),
        sa.Column('blockers', sa.Text(), nullable=True),
        sa.Column('recommended_actions', sa.Text(), nullable=True),
        sa.Column('error_code', sa.String(length=64), nullable=True),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id']),
        sa.ForeignKeyConstraint(['batch_id'], ['batches.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_assessment_results_assessment_id'), 'assessment_results', ['assessment_id'], unique=False)
    op.create_index(op.f('ix_assessment_results_batch_id'), 'assessment_results', ['batch_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_assessment_results_batch_id'), table_name='assessment_results')
    op.drop_index(op.f('ix_assessment_results_assessment_id'), table_name='assessment_results')
    op.drop_table('assessment_results')
    op.drop_index(op.f('ix_assessments_run_id'), table_name='assessments')
    op.drop_index(op.f('ix_assessments_batch_id'), table_name='assessments')
    op.drop_table('assessments')
    op.drop_index(op.f('ix_audit_events_run_id'), table_name='audit_events')
    op.drop_index(op.f('ix_audit_events_migration_id'), table_name='audit_events')
    op.drop_index(op.f('ix_audit_events_event_type'), table_name='audit_events')
    op.drop_index(op.f('ix_audit_events_entity_id'), table_name='audit_events')
    op.drop_index(op.f('ix_audit_events_batch_id'), table_name='audit_events')
    op.drop_table('audit_events')
