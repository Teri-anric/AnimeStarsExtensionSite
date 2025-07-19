import uuid
from typing import Annotated
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse

from app.web.deps import StorageServiceDep
from app.web.auth.deps import UserDep

MAX_FILE_SIZE = 20 * 1024 * 1024

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload")
async def upload_file(
    upload_file: Annotated[UploadFile, File(...)],
    current_user: UserDep,
    storage_service: StorageServiceDep,
):
    """
    Uploads a file to the server.

    Args:
        upload_file: File to upload
        current_user: Current authenticated user
        storage_service: Storage service for file operations

    Returns:
        JSON with the uploaded file URL
    """
    if upload_file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File is too large. Maximum size: {MAX_FILE_SIZE // (1024 * 1024)}MB",
        )

    relative_path = f"uploads/{current_user.id}/{uuid.uuid4()}_{upload_file.filename}"

    try:
        saved_path = await storage_service.save(upload_file, relative_path)
        file_url = storage_service.get_url(saved_path)

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "file_url": file_url,
                "file_path": saved_path,
                "filename": upload_file.filename,
                "size": upload_file.size,
                "content_type": upload_file.content_type,
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error saving file: {str(e)}"
        )


@router.delete("/{file_path:path}")
async def delete_file(
    file_path: str,
    current_user: UserDep,
    storage_service: StorageServiceDep,
):
    """
    Deletes a file from the server.

    Args:
        file_path: Path to the file to delete
        current_user: Current authenticated user
        storage_service: Storage service for file operations

    Returns:
        JSON with operation result
    """
    try:
        if not await storage_service.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        await storage_service.delete(file_path)

        return JSONResponse(
            status_code=200,
            content={"success": True, "message": "File successfully deleted"},
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error deleting file: {str(e)}"
        )
