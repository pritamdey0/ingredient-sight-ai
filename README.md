# IngredientSight AI & PRMPT Archive

An ultra-sleek, full-screen scroll-driven fashion/archive Landing Page and interactive **5-Agent LangGraph AI Ingredient Analyzer Dashboard** for cosmetic, food, and skincare products.

---

## Architecture Overview

```
                      LangGraph Pipeline
                               │
                     Supervisor (Workflow)
                               │
      ┌────────────────────────┼────────────────────────┐
      ▼                        ▼                        ▼
  OCR Agent            Ingredient Agent         Research Agent
                               │
                               ▼
                          Safety Agent
                               │
                               ▼
                          Report Agent
```

- **Frontend**: React 19 + TypeScript + Vite 6 + Tailwind CSS v4 + GSAP 3 + Framer Motion (`motion`)
- **Backend**: FastAPI + Python + LangGraph StateGraph (5 agents: OCR → Ingredient → Research → Safety → Report)

---

## Quick Start / How to Run

### Prerequisites
- **Node.js**: v18+ or v24+ ([Download Node.js](https://nodejs.org/))
- **Python**: v3.11+ ([Download Python](https://www.python.org/))
- **uv** (recommended) or standard `pip`

---

### Step 1: Install Dependencies

#### 1. Backend Dependencies
```bash
# Using uv (recommended)
uv pip install fastapi uvicorn pydantic python-multipart langgraph langchain-openai pillow pytesseract

# OR using standard pip
pip install fastapi uvicorn pydantic python-multipart langgraph langchain-openai pillow pytesseract
```

#### 2. Frontend Dependencies
```bash
npm install
```

---

### Step 2: Set Environment Variables (Optional)

Create a `.env` file in the root directory if calling OpenAI models for real-time scientific research:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

---

### Step 3: Launch the Services

#### Terminal 1 — Start FastAPI Backend Server
```bash
uv run python server.py
# OR
python server.py
```
- Backend runs at: `http://localhost:8000`
- API documentation available at: `http://localhost:8000/docs`

#### Terminal 2 — Start Vite React Frontend
```bash
npm run dev
```
- Frontend app runs at: `http://localhost:3000`

---

## Features

1. **Full-Screen Atmospheric Video Hero**:
   - Seamless background video with cursor X scrubbing dead zone (+/-50px physics).
   - Staggered entrance animations and mix-blend-mode exclusion text overlays.
2. **Scattered Specimen Matrix**:
   - RAF scroll-driven card scale calculation (`0 → 1 → 0`) as product images scroll through the viewport.
3. **Interactive 5-Agent AI Dashboard**:
   - Visualized LangGraph execution pipeline (*OCR → Ingredient → Research → Safety → Report*).
   - Upload label images or select demo specimens.
   - Dermatological safety score gauge (0–100), INCI ingredient table, and report downloads in `.md` and `.json`.

---

## License

MIT License
