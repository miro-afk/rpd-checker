from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pdf_checker import check_hourtables,chek_headers,check_comp,check_themes,check_literature
import os
import shutil
import uuid

app = FastAPI()
origins = [
    "http://localhost:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)



@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Эндпоинт для загрузки файла на сервер"""
    file_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{file_id}.pdf"
    if file.content_type not in ["application/pdf"]:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                            detail="Неподдерживаемый тип файла")
    try:
        with open(file_path, 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {
            "result":"success",
            "file_id":file_id
                }


    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e

@app.get("/check/{file_id}")
async def check_file(file_id: str):
    """Эндпоинт для проверки статуса файла"""
    file_path = UPLOAD_DIR / f"{file_id}.pdf"
    try:
        os.path.exists(file_path)
        result_hourtables=check_hourtables(file_path)
        print("hours done")
        result_themes=check_themes(file_path)
        print("themes done")
        result_literature = check_literature(file_path)
        print("literature done")
        result_headers = chek_headers(file_path)
        print("headers done")
        result_comp = check_comp(file_path)
        print("comp done")
        return {"result_hourtables":result_hourtables[0],
                    "hourtables_content":result_hourtables[1],
                "result_headers":result_headers[0],
                "headers_content":result_headers[1],
                "result_comp":result_comp[0],
                "comp_content":result_comp[1],
                "result_themes":result_themes[0],
                "themes_content":result_themes[1],
                "result_literature":result_literature[0],
                "literature_content":result_literature[1]
            }
    except Exception as e:
        raise HTTPException(status.HTTP_410_GONE, detail=str(e)) from e

@app.get("/pdf/{file_id}")
async def get_file(file_id: str):
    """Эндпоинт для отправки файла для превью"""
    file_path = UPLOAD_DIR/f"{file_id}.pdf"
    try:
        return FileResponse(file_path)
    except Exception as e:
        raise HTTPException(status.HTTP_410_GONE,detail=str(e)) from e
@app.delete("/delete/{file_id}")
async def delete_file(file_id:str):
    """Эндпоинт для удаления файла"""
    file_path = UPLOAD_DIR/f"{file_id}.pdf"
    try:
        os.remove(file_path)
        return {"success"}
    except Exception as e:
        raise HTTPException(status.HTTP_410_GONE,detail=str(e)) from e
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)