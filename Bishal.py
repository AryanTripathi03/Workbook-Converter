from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import List
import pandas as pd
from io import BytesIO

app = FastAPI(title="Excel & CSV Merger API")

from fastapi import Form

@app.post("/api/login/")
async def login(user_id: str = Form(...), password: str = Form(...)):
    valid_users = {
        "aryan": "mypassword123",
        "admin": "adminpass"
    }

    if user_id.strip() in valid_users and password.strip() == valid_users[user_id.strip()]:
        return {"status": "ok", "user": user_id.strip()}

    raise HTTPException(status_code=401, detail="Invalid credentials")


# ---- CORS (required for frontend) ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # lock later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- FILE MERGE ENDPOINT ----
@app.post("/api/upload/")
async def merge_uploaded_files(files: List[UploadFile] = File(...)):
    if len(files) < 1:
        raise HTTPException(status_code=400, detail="No files uploaded")

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for file in files:
            filename = file.filename.lower()

            # SAME logic you had
            if filename.endswith(".csv"):
                df = pd.read_csv(file.file, encoding="latin1")
            elif filename.endswith(".xlsx") or filename.endswith(".xls"):
                df = pd.read_excel(file.file)
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type: {file.filename}"
                )

            sheet_name = file.filename.rsplit(".", 1)[0][:31]
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=One_workbook.xlsx"
        }
    )
