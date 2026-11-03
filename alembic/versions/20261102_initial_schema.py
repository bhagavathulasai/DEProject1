"""Initial DentalVision schema

Revision ID: 20261102_initial
Revises: 
Create Date: 2026-11-02 01:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20261102_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.create_table(
        "model_versions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("version", sa.String(length=50), nullable=False),
        sa.Column("model_path", sa.String(length=1024), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("metrics", sa.JSON(), nullable=False),
        sa.Column("trained_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_model_versions_id"), "model_versions", ["id"], unique=False)

    op.create_table(
        "uploaded_images",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("secure_filename", sa.String(length=255), nullable=False),
        sa.Column("storage_path", sa.String(length=1024), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=False),
        sa.Column("sha256", sa.String(length=128), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_uploaded_images_id"), "uploaded_images", ["id"], unique=False)
    op.create_index(op.f("ix_uploaded_images_sha256"), "uploaded_images", ["sha256"], unique=False)
    op.create_index(
        op.f("ix_uploaded_images_user_id"), "uploaded_images", ["user_id"], unique=False
    )

    op.create_table(
        "predictions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("model_version_id", sa.Uuid(), nullable=True),
        sa.Column("uploaded_image_id", sa.Uuid(), nullable=True),
        sa.Column("label", sa.String(length=120), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["model_version_id"], ["model_versions.id"]),
        sa.ForeignKeyConstraint(["uploaded_image_id"], ["uploaded_images.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uploaded_image_id"),
    )
    op.create_index(op.f("ix_predictions_id"), "predictions", ["id"], unique=False)
    op.create_index(
        op.f("ix_predictions_model_version_id"), "predictions", ["model_version_id"], unique=False
    )
    op.create_index(
        op.f("ix_predictions_uploaded_image_id"), "predictions", ["uploaded_image_id"], unique=False
    )
    op.create_index(op.f("ix_predictions_user_id"), "predictions", ["user_id"], unique=False)

    op.create_table(
        "prediction_results",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("prediction_id", sa.Uuid(), nullable=False),
        sa.Column("label", sa.String(length=120), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("probabilities", sa.JSON(), nullable=True),
        sa.Column("entropy", sa.Float(), nullable=True),
        sa.Column("is_rejected", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["prediction_id"], ["predictions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("prediction_id"),
    )
    op.create_index(op.f("ix_prediction_results_id"), "prediction_results", ["id"], unique=False)
    op.create_index(
        op.f("ix_prediction_results_prediction_id"),
        "prediction_results",
        ["prediction_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_prediction_results_prediction_id"), table_name="prediction_results")
    op.drop_index(op.f("ix_prediction_results_id"), table_name="prediction_results")
    op.drop_table("prediction_results")

    op.drop_index(op.f("ix_predictions_user_id"), table_name="predictions")
    op.drop_index(op.f("ix_predictions_uploaded_image_id"), table_name="predictions")
    op.drop_index(op.f("ix_predictions_model_version_id"), table_name="predictions")
    op.drop_index(op.f("ix_predictions_id"), table_name="predictions")
    op.drop_table("predictions")

    op.drop_index(op.f("ix_uploaded_images_user_id"), table_name="uploaded_images")
    op.drop_index(op.f("ix_uploaded_images_sha256"), table_name="uploaded_images")
    op.drop_index(op.f("ix_uploaded_images_id"), table_name="uploaded_images")
    op.drop_table("uploaded_images")

    op.drop_index(op.f("ix_model_versions_id"), table_name="model_versions")
    op.drop_table("model_versions")

    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
