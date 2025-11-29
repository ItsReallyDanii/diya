import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import declarative_base, relationship
from pgvector.sqlalchemy import Vector

Base = declarative_base()


def timestamp_column():
    return Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    plan = Column(Text)
    created_at = timestamp_column()

    users = relationship("User", back_populates="organization")
    workspaces = relationship("Workspace", back_populates="organization")


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="SET NULL"))
    email = Column(Text, nullable=False, unique=True)
    phone = Column(Text)
    role = Column(String(50), nullable=False)
    password_hash = Column(Text, nullable=False)
    created_at = timestamp_column()

    organization = relationship("Organization", back_populates="users")
    workspaces = relationship("Workspace", back_populates="owner")
    materials = relationship("Material", back_populates="owner")
    tools = relationship("Tool", back_populates="owner")


class Material(Base):
    __tablename__ = "materials"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    name = Column(Text, nullable=False)
    properties = Column(JSONB)
    stock = Column(Integer, default=0)
    created_at = timestamp_column()

    organization = relationship("Organization")
    owner = relationship("User", back_populates="materials")


class Tool(Base):
    __tablename__ = "tools"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    name = Column(Text, nullable=False)
    capabilities = Column(JSONB)
    created_at = timestamp_column()

    organization = relationship("Organization")
    owner = relationship("User", back_populates="tools")


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"))
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    location = Column(Text)
    created_at = timestamp_column()

    organization = relationship("Organization", back_populates="workspaces")
    owner = relationship("User", back_populates="workspaces")
    problems = relationship("Problem", back_populates="workspace")


class Problem(Base):
    __tablename__ = "problems"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"))
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"))
    description = Column(Text, nullable=False)
    constraints = Column(JSONB)
    safety_flags = Column(JSONB)
    status = Column(Text, nullable=False, server_default="open")
    embedding = Column(Vector(768))
    created_at = timestamp_column()

    workspace = relationship("Workspace", back_populates="problems")
    recipes = relationship("Recipe", back_populates="problem")

    __table_args__ = (
        Index("ix_problems_org_id", "org_id"),
        Index("ix_problems_embedding", "embedding", postgresql_using="ivfflat", postgresql_with={"lists": 100}),
        Index("ix_problems_constraints", "constraints", postgresql_using="gin"),
    )


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    problem_id = Column(UUID(as_uuid=True), ForeignKey("problems.id", ondelete="CASCADE"))
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"))
    title = Column(Text, nullable=False)
    steps = Column(JSONB, nullable=False)
    safety_notes = Column(Text)
    required_materials = Column(JSONB)
    required_tools = Column(JSONB)
    est_time_min = Column(Integer)
    est_cost_cents = Column(Integer)
    confidence = Column(Numeric(3, 2))
    created_by_ai = Column(Boolean, nullable=False, server_default="true")
    version = Column(Integer, nullable=False, server_default="1")
    parent_recipe_id = Column(UUID(as_uuid=True), ForeignKey("recipes.id", ondelete="SET NULL"))
    embedding = Column(Vector(768))
    created_at = timestamp_column()

    problem = relationship("Problem", back_populates="recipes")
    parent = relationship("Recipe", remote_side=[id])

    __table_args__ = (
        Index("ix_recipes_org_id", "org_id"),
        Index("ix_recipes_embedding", "embedding", postgresql_using="ivfflat", postgresql_with={"lists": 100}),
        Index("ix_recipes_required_materials", "required_materials", postgresql_using="gin"),
    )


class ExecutionLog(Base):
    __tablename__ = "execution_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipe_id = Column(UUID(as_uuid=True), ForeignKey("recipes.id", ondelete="CASCADE"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    outcome = Column(Text)
    notes = Column(Text)
    rating = Column(SmallInteger)
    created_at = timestamp_column()


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_type = Column(Text, nullable=False)
    owner_id = Column(UUID(as_uuid=True), nullable=False)
    uri = Column(Text, nullable=False)
    mime_type = Column(Text)
    created_at = timestamp_column()
