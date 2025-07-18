import uuid
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse

from app.web.deps import StorageServiceDep
from app.web.auth.deps import get_current_user
from app.database.models.animestars_user import AnimestarsUser

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    storage_service: StorageServiceDep = Depends(),
    current_user: AnimestarsUser = Depends(get_current_user)
):
    """
    Завантажує файл на сервер.
    
    Args:
        file: Файл для завантаження
        storage_service: Сервіс для зберігання файлів
        current_user: Поточний авторизований користувач
        
    Returns:
        JSON з URL завантаженого файлу
    """
    # Перевіряємо розмір файлу (максимум 10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # Читаємо файл для перевірки розміру
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Файл занадто великий. Максимальний розмір: {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Генеруємо унікальне ім'я файлу
    file_extension = Path(file.filename).suffix if file.filename else ""
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Створюємо шлях з урахуванням дати для кращої організації
    current_date = datetime.now().strftime("%Y/%m/%d")
    relative_path = f"{current_date}/{unique_filename}"
    
    # Створюємо тимчасовий UploadFile з прочитаним контентом
    from io import BytesIO
    temp_file = UploadFile(
        filename=file.filename,
        file=BytesIO(content),
        content_type=file.content_type
    )
    
    try:
        # Зберігаємо файл
        saved_path = await storage_service.save(temp_file, relative_path)
        
        # Отримуємо URL для доступу до файлу
        file_url = storage_service.get_url(saved_path)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "file_url": file_url,
                "file_path": saved_path,
                "filename": file.filename,
                "size": len(content),
                "content_type": file.content_type
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Помилка при збереженні файлу: {str(e)}"
        )


@router.delete("/{file_path:path}")
async def delete_file(
    file_path: str,
    storage_service: StorageServiceDep = Depends(),
    current_user: AnimestarsUser = Depends(get_current_user)
):
    """
    Видаляє файл з сервера.
    
    Args:
        file_path: Шлях до файлу для видалення
        storage_service: Сервіс для зберігання файлів
        current_user: Поточний авторизований користувач
        
    Returns:
        JSON з результатом операції
    """
    try:
        # Перевіряємо чи існує файл
        if not await storage_service.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail="Файл не знайдено"
            )
        
        # Видаляємо файл
        await storage_service.delete(file_path)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Файл успішно видалено"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Помилка при видаленні файлу: {str(e)}"
        )