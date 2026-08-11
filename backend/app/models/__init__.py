"""Import every model so Alembic and SQLAlchemy discover all tables."""
from app.models.assessment import Assessment, AssessmentResult  # noqa: F401
from app.models.audit import AuditEvent  # noqa: F401
from app.models.batch import Batch, Resource  # noqa: F401
from app.models.evidence import Evidence, ExceptionRecord  # noqa: F401
from app.models.migration import MigrationProject, MigrationWave, Tenant  # noqa: F401
