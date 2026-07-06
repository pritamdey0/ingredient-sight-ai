from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
    title="IngredientSight AI",
    description="AI-powered Ingredient Intelligence Platform using LangGraph",
    version="1.0.0",
)


@app.get("/", tags=["Health"])
async def root():
    return JSONResponse(
        content={
            "project": "IngredientSight AI",
            "version": "1.0.0",
            "status": "Running 🚀",
        }
    )