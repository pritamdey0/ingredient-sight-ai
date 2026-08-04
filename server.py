"""
IngredientSight AI - FastAPI Web Server

Exposes backend REST API endpoints for the React Frontend / Dashboard to invoke
the 5-Agent LangGraph Pipeline (OCR -> Ingredient -> Research -> Safety -> Report).
"""
import os
import sys
import uuid
from typing import Optional
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Ensure UTF-8 output encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from langgraphagentic.graph import build_graph

app = FastAPI(
    title="IngredientSight AI API",
    description="Backend service powering PRMPT Archive & IngredientSight AI Frontend",
    version="1.0.0"
)

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compile LangGraph pipeline on startup
print("Compiling LangGraph StateGraph pipeline...")
pipeline_app = build_graph()
print("Graph compiled successfully.")

# Temp upload folder
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "IngredientSight AI LangGraph Pipeline"}


@app.post("/api/analyze")
async def analyze_label(file: Optional[UploadFile] = File(None), sample_name: Optional[str] = None):
    """
    Run 5-Agent LangGraph Pipeline on an uploaded cosmetic label image or sample item.
    """
    try:
        if file:
            file_ext = os.path.splitext(file.filename)[1] or ".png"
            file_name = f"upload_{uuid.uuid4().hex[:8]}{file_ext}"
            file_path = os.path.join(UPLOAD_DIR, file_name)
            
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
        else:
            # Fallback to local sample image if no file provided
            file_path = os.path.join(os.path.dirname(__file__), "ingredients_en.5.full.jpg")
            if not os.path.exists(file_path):
                raise HTTPException(status_code=400, detail="No file uploaded and sample image not found.")

        print(f"\nInvoking LangGraph pipeline with image: {file_path}")
        result = pipeline_app.invoke({"image_path": file_path})
        
        return {
            "success": True,
            "ocr_text": result.get("ocr_text", ""),
            "ingredients": result.get("ingredients", []),
            "safety_analysis": result.get("safety_analysis", {}),
            "report_md_path": result.get("report_md_path", ""),
            "report_json_path": result.get("report_json_path", ""),
        }
    except Exception as e:
        print(f"Error running pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
