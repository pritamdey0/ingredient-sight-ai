<div align="center">

<br/>

```
 ██╗███╗  ██╗ ██████╗ ██████╗ ███████╗██████╗ ██╗███████╗███╗  ██╗████████╗    ███████╗██╗ ██████╗ ██╗  ██╗████████╗
 ██║████╗ ██║██╔════╝ ██╔══██╗██╔════╝██╔══██╗██║██╔════╝████╗ ██║╚══██╔══╝    ██╔════╝██║██╔════╝ ██║  ██║╚══██╔══╝
 ██║██╔██╗██║██║  ███╗██████╔╝█████╗  ██║  ██║██║█████╗  ██╔██╗██║   ██║       ███████╗██║██║  ███╗███████║   ██║   
 ██║██║╚████║██║   ██║██╔══██╗██╔══╝  ██║  ██║██║██╔══╝  ██║╚████║   ██║       ╚════██║██║██║   ██║██╔══██║   ██║   
 ██║██║ ╚███║╚██████╔╝██║  ██║███████╗██████╔╝██║███████╗██║ ╚███║   ██║       ███████║██║╚██████╔╝██║  ██║   ██║   
 ╚═╝╚═╝  ╚══╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═════╝ ╚═╝╚══════╝╚═╝  ╚══╝   ╚═╝       ╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝
```

### ✦ AI-Powered Cosmetic & Skincare Ingredient Intelligence ✦

<br/>

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic%20Pipeline-FF6B35?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![License: MIT](https://img.shields.io/badge/License-MIT-F7DC6F?style=for-the-badge)](./LICENSE)

<br/>

> **Upload a product label → 5 AI Agents analyze it → Get a full dermatological safety report.**  
> A full-stack AI application combining a scroll-driven editorial landing page with a live multi-agent analysis dashboard.

<br/>

---

</div>

## 🧬 What is IngredientSight AI?

**IngredientSight AI** is a full-stack intelligent system that decodes the ingredient labels of cosmetic, food, and skincare products using a **5-stage autonomous AI pipeline** built with [LangGraph](https://langchain-ai.github.io/langgraph/). Simply photograph your product label, upload it to the dashboard, and receive a comprehensive, research-backed safety report — complete with a dermatological risk score, per-ingredient profiles, health warnings, and downloadable reports.

The project lives inside a stunning editorial landing page called **PRMPT Archive**, featuring scroll-driven cinematics, atmospheric full-screen video, and scattered specimen cards — designed to feel like a high-fashion AI lab.

<br/>

---

## ✨ Feature Highlights

| 🧠 5-Agent AI Pipeline | 🎨 Premium Frontend |
|---|---|
| **OCR Agent** — Extracts raw text from label images via Gemini Vision | **Full-Screen Video Hero** with cursor-driven X-axis scrubbing (±50px dead zone physics) |
| **Ingredient Agent** — Parses and normalizes INCI ingredient lists | **Scattered Specimen Matrix** — RAF scroll-driven card scale animation (`0 → 1 → 0`) |
| **Research Agent** — Pulls clinical evidence via Tavily web search | **GSAP 3 + Framer Motion** staggered entrance animations |
| **Safety Agent** — Scores ingredients, flags allergens & irritants | **`mix-blend-mode: exclusion`** typography overlays for editorial feel |
| **Report Agent** — Generates `.md` + `.json` safety reports | **Realtime Pipeline Visualizer** showing each agent's live execution state |

<br/>

---

## 🏗️ Architecture

```
                ┌─────────────────────────────────────┐
                │         React 19  Frontend           │
                │   Vite 6 · TypeScript · Tailwind v4  │
                │    GSAP 3 · Framer Motion · Lucide    │
                └────────────────┬────────────────────-┘
                                 │  REST API (HTTP)
                ┌────────────────▼────────────────────-┐
                │       FastAPI Backend  (Python)        │
                │    POST /api/analyze · GET /api/health │
                └────────────────┬────────────────────-┘
                                 │
                ┌────────────────▼────────────────────-┐
                │      LangGraph  StateGraph Pipeline    │
                │                                       │
                │  ┌──────────────────────────────┐    │
                │  │           START              │    │
                │  └──────────────┬───────────────┘    │
                │                 │                     │
                │  ┌──────────────▼───────────────┐    │
                │  │  🔍  OCR Agent               │    │
                │  │      Google Gemini Vision     │    │
                │  └──────────────┬───────────────┘    │
                │            ocr_text                   │
                │  ┌──────────────▼───────────────┐    │
                │  │  🧪  Ingredient Agent         │    │
                │  │      INCI List Parser         │    │
                │  └──────────────┬───────────────┘    │
                │            ingredients[ ]             │
                │  ┌──────────────▼───────────────┐    │
                │  │  🔬  Research Agent           │    │
                │  │      Tavily Web Search        │    │
                │  └──────────────┬───────────────┘    │
                │            research_results{}         │
                │  ┌──────────────▼───────────────┐    │
                │  │  🛡️  Safety Agent             │    │
                │  │      Risk Scoring Engine      │    │
                │  └──────────────┬───────────────┘    │
                │         safety_score · risk_label     │
                │  ┌──────────────▼───────────────┐    │
                │  │  📋  Report Agent             │    │
                │  │      .md + .json Generator    │    │
                │  └──────────────┬───────────────┘    │
                │                 │                     │
                │  ┌──────────────▼───────────────┐    │
                │  │            END               │    │
                │  └──────────────────────────────┘    │
                └───────────────────────────────────────┘
```

<br/>

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend Framework** | React 19 + TypeScript | Component-based reactive UI |
| **Build Tool** | Vite 6 | Lightning-fast dev server & HMR |
| **Styling** | Tailwind CSS v4 | Utility-first design system |
| **Animation** | GSAP 3 + Framer Motion | Scroll physics & micro-interactions |
| **Icons** | Lucide React | Crisp, consistent SVG icon library |
| **Backend Framework** | FastAPI | High-performance async REST API |
| **AI Orchestration** | LangGraph (StateGraph) | Multi-agent pipeline with typed state |
| **Vision AI** | Google Gemini Vision | OCR from product label images |
| **Web Research** | Tavily Search API | Real-time ingredient evidence gathering |
| **Python Runtime** | Python 3.11+ with `uv` | Fast, reliable dependency management |

<br/>

---

## 🚀 Getting Started

### Prerequisites

| Requirement | Minimum Version | Download |
|-------------|----------------|----------|
| **Node.js** | v18 or v24+ | [nodejs.org](https://nodejs.org/) |
| **Python** | v3.11+ | [python.org](https://www.python.org/) |
| **uv** *(recommended)* | latest | `pip install uv` |

<br/>

### Step 1 — Clone the Repository

```bash
git clone https://github.com/pritamdey0/IngredientSight-AI.git
cd IngredientSight-AI
```

<br/>

### Step 2 — Configure Environment Variables

Copy the example env file and fill in your API keys:

```bash
# Linux / macOS
cp .env.example .env

# Windows
copy .env.example .env
```

Open `.env` and set your keys:

```env
# ── Required ──────────────────────────────────────────────────────────
# Google Gemini API key — powers OCR, Ingredient & Safety agents
# Get yours free at: https://aistudio.google.com/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# ── Recommended ───────────────────────────────────────────────────────
# Tavily Search API — enables real-time web research per ingredient
# Get yours at: https://app.tavily.com
TAVILY_API_KEY=your_tavily_api_key_here

# ── Optional (reserved for future agents) ─────────────────────────────
GROQ_API_KEY=
OPENAI_API_KEY=
```

> ⚠️ **Never commit your `.env` file.** It is already listed in `.gitignore`.

<br/>

### Step 3 — Install Dependencies

**Backend (Python):**
```bash
# Using uv (recommended — significantly faster than pip)
uv pip install fastapi uvicorn pydantic python-multipart \
               langgraph langchain-google-genai pillow pytesseract \
               python-dotenv tavily-python

# OR using pip with the requirements file
pip install -r requirements.txt
```

**Frontend (Node.js):**
```bash
npm install
```

<br/>

### Step 4 — Launch the Application

Open **two terminal windows** and run each command simultaneously:

**Terminal 1 — Backend (FastAPI + LangGraph)**
```bash
uv run python server.py
# OR
python server.py
```

| Service | URL |
|---------|-----|
| 🚀 API Server | `http://localhost:8000` |
| 📖 Interactive API Docs (Swagger) | `http://localhost:8000/docs` |
| ❤️ Health Check | `http://localhost:8000/api/health` |

<br/>

**Terminal 2 — Frontend (Vite Dev Server)**
```bash
npm run dev
```

| Service | URL |
|---------|-----|
| 🌐 Frontend App | `http://localhost:3000` |

<br/>

---

## 🔬 How the Pipeline Works

Once you upload a product label image, the following 5-step sequence executes automatically:

```
Step 1 — 🔍  OCR Agent
              Sends the image to Google Gemini Vision API
              → Returns raw extracted text from the ingredient panel

Step 2 — 🧪  Ingredient Agent
              Parses the OCR output
              → Normalizes and identifies each INCI ingredient name

Step 3 — 🔬  Research Agent
              Queries Tavily Search for each key ingredient
              → Gathers clinical studies, safety data & usage guidelines

Step 4 — 🛡️  Safety Agent
              Evaluates each ingredient against safety references
              → Computes a dermatological safety score (0–100)
              → Flags allergens, irritants & comedogenic compounds

Step 5 — 📋  Report Agent
              Synthesizes all findings into a structured report
              → Saves as .md (human-readable) and .json (machine-readable)
              → Returns safety_score and risk_label to the dashboard
```

<br/>

---

## 📁 Project Structure

```
IngredientSight-AI/
│
├── 📂 langgraphagentic/          # Core 5-agent AI pipeline (Python)
│   ├── graph.py                  # LangGraph StateGraph definition & wiring
│   ├── ocr_agent.py              # Agent 1: Gemini Vision OCR
│   ├── ingredient_agent.py       # Agent 2: INCI ingredient parser
│   ├── research_agent.py         # Agent 3: Tavily web research
│   ├── safety_agent.py           # Agent 4: Safety scoring engine
│   └── report_agent.py           # Agent 5: Markdown + JSON report generator
│
├── 📂 src/                       # React + TypeScript frontend
│   ├── components/               # UI components (hero, dashboard, cards…)
│   ├── App.tsx                   # Root application component
│   ├── main.tsx                  # Vite entry point
│   └── index.css                 # Global styles & CSS variables
│
├── 📂 uploads/                   # Uploaded label images (runtime, gitignored)
├── 📂 reports/                   # Generated AI reports (runtime, gitignored)
├── 📂 public/                    # Static frontend assets
│
├── server.py                     # FastAPI application & REST endpoints
├── main.py                       # CLI entry point
├── .env.example                  # Environment variable template
├── .gitignore                    # Gitignore rules (includes .env, uploads, reports)
├── vite.config.ts                # Vite build configuration
├── tsconfig.json                 # TypeScript compiler config
├── package.json                  # Node.js dependencies & scripts
├── pyproject.toml                # Python project metadata
└── requirements.txt              # Python dependencies list
```

<br/>

---

## 🌐 API Reference

### `POST /api/analyze`

Runs the full 5-agent LangGraph pipeline on an uploaded product label image.

**Request (multipart/form-data):**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | `UploadFile` | ✅ Yes | Product label image (PNG, JPG, WebP, GIF, BMP) |
| `product_name` | `string` | No | Optional display name for the product |

**Example Response:**
```json
{
  "success": true,
  "product_name": "CeraVe Moisturizing Cream",
  "safety_score": 87,
  "risk_label": "Low Risk",
  "ocr_text": "INGREDIENTS: Aqua, Glycerin, Cetearyl Alcohol ...",
  "ingredients": ["Aqua", "Glycerin", "Cetearyl Alcohol", "..."],
  "research_results": {
    "Glycerin": { "safety": "well-tolerated humectant", "sources": ["..."] }
  },
  "safety_analysis": {
    "overall_score": 87,
    "warnings": [],
    "recommendations": ["Suitable for sensitive skin"]
  },
  "markdown_report": "# IngredientSight Safety Report\n...",
  "json_report": { "product": "...", "score": 87 },
  "report_md_path": "/reports/report_abc123.md",
  "report_json_path": "/reports/report_abc123.json"
}
```

<br/>

### `GET /api/health`

Returns the current health and configuration status of the backend pipeline.

```json
{
  "status": "ok",
  "service": "IngredientSight AI LangGraph Pipeline",
  "gemini_configured": true,
  "tavily_configured": true,
  "upload_dir": "/path/to/uploads",
  "reports_dir": "/path/to/reports",
  "port": 8000,
  "host": "0.0.0.0"
}
```

<br/>

---

## 🔑 API Keys Reference

| Variable | Required | Provider | Used By |
|----------|----------|----------|---------|
| `GEMINI_API_KEY` | ✅ Required | [Google AI Studio](https://aistudio.google.com/apikey) | OCR, Ingredient & Safety agents |
| `TAVILY_API_KEY` | ⚡ Recommended | [Tavily](https://app.tavily.com) | Research agent (real-time web search) |
| `GROQ_API_KEY` | 🔮 Future | [Groq Console](https://console.groq.com) | Reserved for future fast-inference agents |
| `OPENAI_API_KEY` | 🔮 Optional | [OpenAI](https://platform.openai.com) | Optional LLM alternative |

> Without `TAVILY_API_KEY`, the Research Agent gracefully falls back to LLM-only knowledge. All core features remain fully operational.

<br/>

---

## 🛡️ Security Notes

- Uploaded files are validated against **image magic bytes** (not just file extensions) — spoofed file types are rejected before OCR
- The `.env` file is **gitignored** — your API keys are never committed to version control
- If any key was ever accidentally committed, rotate it at the provider immediately and generate a fresh one
- CORS is wide-open for local development; restrict `allow_origins` before any production deployment

<br/>

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. **Fork** the repository
2. Create your feature branch: `git checkout -b feat/your-feature-name`
3. Commit your changes using [Conventional Commits](https://www.conventionalcommits.org/):
   ```bash
   git commit -m "feat: add amazing new feature"
   ```
4. Push to your branch: `git push origin feat/your-feature-name`
5. Open a **Pull Request** and describe your changes

<br/>

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](./LICENSE) file for full details.

<br/>

---

<div align="center">

**Built with ❤️ using LangGraph · FastAPI · React 19 · Google Gemini**

*IngredientSight AI — Know exactly what's in your products.*

<br/>

[![GitHub Stars](https://img.shields.io/github/stars/pritamdey0/IngredientSight-AI?style=social)](https://github.com/pritamdey0/IngredientSight-AI)
[![GitHub Forks](https://img.shields.io/github/forks/pritamdey0/IngredientSight-AI?style=social)](https://github.com/pritamdey0/IngredientSight-AI/fork)

</div>
