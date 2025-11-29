"""initial schema"""

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    op.create_table(
        "organizations",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("plan", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("org_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="SET NULL")),
        sa.Column("email", sa.Text, nullable=False, unique=True),
        sa.Column("phone", sa.Text),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("password_hash", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "materials",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("org_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE")),
        sa.Column("user_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("properties", sa.JSONB),
        sa.Column("stock", sa.Integer, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "tools",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("org_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE")),
        sa.Column("user_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("capabilities", sa.JSONB),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "workspaces",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("org_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE")),
        sa.Column("owner_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("location", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "problems",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("workspace_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("workspaces.id", ondelete="CASCADE")),
        sa.Column("org_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE")),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("constraints", sa.JSONB),
        sa.Column("safety_flags", sa.JSONB),
        sa.Column("status", sa.Text, nullable=False, server_default="open"),
        sa.Column("embedding", Vector(768)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "recipes",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("problem_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("problems.id", ondelete="CASCADE")),
        sa.Column("org_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE")),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("steps", sa.JSONB, nullable=False),
        sa.Column("safety_notes", sa.Text),
        sa.Column("required_materials", sa.JSONB),
        sa.Column("required_tools", sa.JSONB),
        sa.Column("est_time_min", sa.Integer),
        sa.Column("est_cost_cents", sa.Integer),
        sa.Column("confidence", sa.Numeric(3, 2)),
        sa.Column("created_by_ai", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("parent_recipe_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("recipes.id", ondelete="SET NULL")),
        sa.Column("embedding", Vector(768)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "execution_logs",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("recipe_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("recipes.id", ondelete="CASCADE")),
        sa.Column("user_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("outcome", sa.Text),
        sa.Column("notes", sa.Text),
        sa.Column("rating", sa.SmallInteger),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "attachments",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("owner_type", sa.Text, nullable=False),
        sa.Column("owner_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("uri", sa.Text, nullable=False),
        sa.Column("mime_type", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_index("ix_problems_org_id", "problems", ["org_id"])
    op.create_index(
        "ix_problems_embedding",
        "problems",
        ["embedding"],
        postgresql_using="ivfflat",
        postgresql_with={"lists": 100},
    )
    op.create_index("ix_problems_constraints", "problems", ["constraints"], postgresql_using="gin")

    op.create_index("ix_recipes_org_id", "recipes", ["org_id"])
    op.create_index(
        "ix_recipes_embedding",
        "recipes",
        ["embedding"],
        postgresql_using="ivfflat",
        postgresql_with={"lists": 100},
    )
    op.create_index(
        "ix_recipes_required_materials",
        "recipes",
        ["required_materials"],
        postgresql_using="gin",
    )


def downgrade() -> None:
    op.drop_index("ix_recipes_required_materials", table_name="recipes")
    op.drop_index("ix_recipes_embedding", table_name="recipes")
    op.drop_index("ix_recipes_org_id", table_name="recipes")
    op.drop_index("ix_problems_constraints", table_name="problems")
    op.drop_index("ix_problems_embedding", table_name="problems")
    op.drop_index("ix_problems_org_id", table_name="problems")

    op.drop_table("attachments")
    op.drop_table("execution_logs")
    op.drop_table("recipes")
    op.drop_table("problems")
    op.drop_table("workspaces")
    op.drop_table("tools")
    op.drop_table("materials")
    op.drop_table("users")
    op.drop_table("organizations")
    op.execute('DROP EXTENSION IF EXISTS vector')
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
