"""
Photos API Endpoints

Handles photo uploads and retrieval for game use.

Endpoints:
- POST /photos - Upload a new photo
- GET /photos/{photo_id} - Get photo metadata
- GET /photos/{photo_id}/image - Get photo file
- GET /photos/random - Get a random approved photo
"""

import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Header, Request, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings
from src.database import get_session
from src.middleware.rate_limit import get_client_ip
from src.models.photo import Photo, PhotoStatus
from src.services.audit_service import AuditService
from src.services.photo_service import PhotoProcessor
from src.workers.moderation import check_photo_content
from src.utils.errors import NotFoundError, PhotoValidationError

router = APIRouter(prefix="/photos", tags=["photos"])


# Response Models

class PhotoUploadResponse(BaseModel):
    """Response after uploading a photo."""
    
    photo_id: uuid.UUID = Field(description="Photo identifier")
    status: str = Field(description="Moderation status")
    message: str = Field(description="Status message")


class PhotoMetadataResponse(BaseModel):
    """Photo metadata for display."""
    
    id: uuid.UUID = Field(description="Photo identifier")
    width: int = Field(description="Image width in pixels")
    height: int = Field(description="Image height in pixels")
    status: str = Field(description="Moderation status")
    aircraft_type: str | None = Field(description="Aircraft type (if approved)")
    airport_code: str | None = Field(description="Airport code (if approved)")


# Dependencies

def get_photo_processor() -> PhotoProcessor:
    """Dependency for PhotoProcessor."""
    return PhotoProcessor()


def get_audit_service() -> AuditService:
    """Dependency for AuditService."""
    return AuditService()


# Endpoints

@router.post(
    "",
    response_model=PhotoUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a photo",
    description=(
        "Upload a new aircraft photo for use in games. "
        "Photos are automatically checked and queued for moderation."
    ),
)
async def upload_photo(
    request: Request,
    file: Annotated[UploadFile, File(description="Photo file (JPEG, PNG, WebP)")],
    aircraft_type: Annotated[str, Form(description="Aircraft type/model")],
    session: Annotated[AsyncSession, Depends(get_session)],
    photo_processor: Annotated[PhotoProcessor, Depends(get_photo_processor)],
    audit_service: Annotated[AuditService, Depends(get_audit_service)],
    x_player_id: Annotated[str | None, Header()] = None,
    airline: Annotated[str | None, Form(description="Airline name")] = None,
    airport_code: Annotated[str | None, Form(description="Airport ICAO/IATA code")] = None,
    aircraft_registration: Annotated[str | None, Form(description="Aircraft registration")] = None,
) -> PhotoUploadResponse:
    """
    Upload a new photo.
    
    The photo will be processed to:
    - Strip all EXIF metadata
    - Generate perceptual hash for duplicates
    - Resize if too large
    - Queue for moderation
    """
    client_ip = get_client_ip(request)
    
    # Parse player ID if provided
    uploader_id = None
    if x_player_id:
        try:
            uploader_id = uuid.UUID(x_player_id)
        except ValueError:
            pass
    
    # Validate file
    if not file.filename:
        raise PhotoValidationError("No filename provided")
    
    # Process the upload
    processed = photo_processor.process_upload(
        file.file,
        file.filename,
    )
    
    # Run content moderation check
    storage_path = processed["stored_path"]
    moderation_result = await check_photo_content(storage_path)
    
    # Handle moderation failures
    if not moderation_result.is_safe:
        # Delete the uploaded file since it failed moderation
        Path(storage_path).unlink(missing_ok=True)
        raise PhotoValidationError(
            f"Photo rejected: {moderation_result.reason}"
        )
    
    # Check for duplicates by file hash
    existing = await session.execute(
        select(Photo).where(Photo.file_hash == processed["file_hash"])
    )
    if existing.scalar_one_or_none():
        raise PhotoValidationError("This photo has already been uploaded")
    
    # Check for perceptual duplicates
    if processed["perceptual_hash"]:
        similar_query = select(Photo.perceptual_hash).where(
            Photo.perceptual_hash.isnot(None)
        )
        result = await session.execute(similar_query)
        existing_hashes = [r[0] for r in result.all()]
        
        if photo_processor.check_duplicate(
            processed["perceptual_hash"],
            existing_hashes,
        ):
            raise PhotoValidationError("A similar photo has already been uploaded")
    
    # Create photo record
    photo = Photo.create(
        filename=processed["filename"],
        file_path=storage_path,
        file_hash=processed["file_hash"],
        file_size=processed["file_size"],
        width=processed["width"],
        height=processed["height"],
        mime_type=processed["mime_type"],
        perceptual_hash=processed["perceptual_hash"],
        aircraft_type=aircraft_type,
        aircraft_registration=aircraft_registration,
        airline=airline,
        airport_code=airport_code,
        uploader_id=uploader_id,
        exif_stripped=True,
    )
    
    # Apply moderation result
    if moderation_result.confidence > 0.9:
        # High confidence - auto-approve
        photo.approve(notes="Auto-approved by moderation system")
        photo.moderation_status = "auto_approved"
    else:
        # Lower confidence - flag for review
        photo.moderation_status = "flagged"
        photo.rejection_reason = f"Flagged: {', '.join(moderation_result.flags)}"
    
    photo.moderation_score = moderation_result.confidence
    
    session.add(photo)
    await session.flush()
    
    # Audit log
    await audit_service.log_photo_uploaded(
        session,
        photo_id=photo.id,
        player_id=uploader_id,
        client_ip=client_ip,
    )
    
    await session.commit()
    
    return PhotoUploadResponse(
        photo_id=photo.id,
        status=photo.status.value,
        message="Photo uploaded successfully. Pending moderation.",
    )


@router.get(
    "/{photo_id}",
    response_model=PhotoMetadataResponse,
    summary="Get photo metadata",
    description="Get metadata for a specific photo.",
)
async def get_photo_metadata(
    photo_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> PhotoMetadataResponse:
    """Get photo metadata by ID."""
    photo = await session.get(Photo, photo_id)
    if not photo:
        raise NotFoundError("Photo", str(photo_id))
    
    # Only show details for approved photos
    if photo.status == PhotoStatus.APPROVED:
        return PhotoMetadataResponse(
            id=photo.id,
            width=photo.width,
            height=photo.height,
            status=photo.status.value,
            aircraft_type=photo.aircraft_type,
            airport_code=photo.airport_code,
        )
    
    return PhotoMetadataResponse(
        id=photo.id,
        width=photo.width,
        height=photo.height,
        status=photo.status.value,
        aircraft_type=None,
        airport_code=None,
    )


@router.get(
    "/{photo_id}/image",
    response_class=FileResponse,
    summary="Get photo image",
    description="Get the actual photo file.",
)
async def get_photo_image(
    photo_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    photo_processor: Annotated[PhotoProcessor, Depends(get_photo_processor)],
) -> FileResponse:
    """Get photo file by ID."""
    photo = await session.get(Photo, photo_id)
    if not photo:
        raise NotFoundError("Photo", str(photo_id))
    
    # Only serve approved photos (or pending for uploaders)
    if photo.status not in (PhotoStatus.APPROVED, PhotoStatus.PENDING):
        raise NotFoundError("Photo", str(photo_id))
    
    file_path = photo_processor.get_photo_path(photo.filename)
    if not file_path.exists():
        raise NotFoundError("Photo", str(photo_id))
    
    return FileResponse(
        path=file_path,
        media_type=photo.mime_type,
        filename=f"photo_{photo_id}.jpg",
    )


@router.get(
    "/random",
    response_model=PhotoMetadataResponse,
    summary="Get random photo",
    description="Get a random approved photo for gameplay.",
)
async def get_random_photo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> PhotoMetadataResponse:
    """Get a random approved photo."""
    # Select random approved photo
    query = (
        select(Photo)
        .where(Photo.status == PhotoStatus.APPROVED)
        .order_by(func.random())
        .limit(1)
    )
    result = await session.execute(query)
    photo = result.scalar_one_or_none()
    
    if not photo:
        raise NotFoundError("Photo", "No approved photos available")
    
    return PhotoMetadataResponse(
        id=photo.id,
        width=photo.width,
        height=photo.height,
        status=photo.status.value,
        aircraft_type=None,  # Don't reveal for gameplay
        airport_code=None,
    )
