from __future__ import annotations

import uuid
from datetime import datetime

from api_app.db.database import Base
from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="clinician", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    predictions: Mapped[list[Prediction]] = relationship(back_populates="user")
    uploaded_images: Mapped[list[UploadedImage]] = relationship(back_populates="user")


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    model_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="trained", nullable=False)
    metrics: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    trained_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    predictions: Mapped[list[Prediction]] = relationship(back_populates="model_version")


class UploadedImage(Base):
    __tablename__ = "uploaded_images"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    secure_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    sha256: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped[User | None] = relationship(back_populates="uploaded_images")
    prediction: Mapped[Prediction | None] = relationship(
        back_populates="uploaded_image", uselist=False
    )


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    model_version_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("model_versions.id"), nullable=True, index=True
    )
    uploaded_image_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("uploaded_images.id"), unique=True, nullable=True, index=True
    )
    label: Mapped[str] = mapped_column(String(120), nullable=False)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="completed", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped[User | None] = relationship(back_populates="predictions")
    model_version: Mapped[ModelVersion | None] = relationship(back_populates="predictions")
    uploaded_image: Mapped[UploadedImage | None] = relationship(back_populates="prediction")
    result: Mapped[PredictionResult | None] = relationship(
        back_populates="prediction", uselist=False
    )


class PredictionResult(Base):
    __tablename__ = "prediction_results"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    prediction_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("predictions.id"), unique=True, nullable=False, index=True
    )
    label: Mapped[str] = mapped_column(String(120), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    probabilities: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    entropy: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_rejected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    prediction: Mapped[Prediction] = relationship(back_populates="result")
