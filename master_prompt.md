# PRMPT & IngredientSight AI — Complete End-to-End Frontend Master Prompt

This document contains the complete, production-grade master specification and prompt for generating the **PRMPT Fashion/Archive Landing Page** and the **IngredientSight AI Dashboard** with identical monochrome color palettes, typography, responsive scrubbing physics, RAF scroll-driven animations, and 5-agent LangGraph integration.

---

## SECTION 1: MASTER PROMPT SPECIFICATION

```markdown
Build a full-screen, scroll-driven fashion/archive landing page and an integrated AI Dashboard for a brand called "prmpt" / "IngredientSight AI". The web application must maintain a strict, ultra-premium monochrome aesthetic (Apple / OpenAI / Linear / Anthropic inspired) with glassmorphism, mix-blend-mode exclusion text overlays, and per-frame RAF scroll mechanics.

---

### Design System & Global Styles

- **Typography**: "Inter Tight" (Google Fonts, weights 400, 500, 600, 700) loaded via `<link>`.
- **Color Palette**: Ultra-sleek monochrome palette (#000000 black, #FFFFFF white, #121212 dark zinc, subtle border accents #27272a, and status accents).
- **Blend Modes**: All overlaid UI elements (logo, navigation, caption, product information, custom cursor) use `mix-blend-mode: exclusion` to remain perfectly crisp against both light background videos and dark panels.
- **Scroll Mechanics**: Standard browser scrollbar hidden (`::-webkit-scrollbar { display: none }`); all animations powered by smooth RAF scroll tracking.

---

### Component Specifications

#### 1. Custom Mix-Blend Cursor (Desktop Only)
- Active on viewports ≥ 1024px without touch inputs.
- `fixed`, `pointer-events-none`, `z-index: 50` centered on pointer via `mousemove` direct DOM updates (`transform: translate(-50%, -50%)`).
- `mix-blend-mode: exclusion`.
- Contains a 48x48 SVG circle (stroke 2.5) with an inner Japanese/decorative glyph path.

#### 2. Hero Section & Atmospheric Video Layer
- **Root Spacer Container**: `id="scroll-spacer"`, dynamic height (`vh + maxScroll + 2*vh`).
- **Video Background Layer** (`id="main-canvas"`): Muted, looping background video (`AI_analyzes_cosmetic_ingredients_202608042106.mp4`) with a 40–60% opacity dark gradient overlay.
- **Media Scrubbing Logic**:
  - *Desktop*: Scrubbed via cursor X position with a dead zone of `Math.max(30, width * 0.05)` pixels around center. Active video side switches smoothly without abrupt `currentTime = 0` resets.
  - *Mobile*: Auto-play looping with seamless fallback.
- **Overlaid UI Elements**:
  - *Logo (Top Left)*: SVG wordmark "prmpt" with circled "R" mark (`mix-blend-mode: exclusion`).
  - *Caption (Left Side)*: Responsive width caption in 12px Inter Tight 500, white.
  - *Header Nav (Top Right)*: "ABOUT", Hamburger icon (`M0 14H40` & `M0 26H40`), "[ DASHBOARD ]", and "[ CART ]".
  - *Product Badge (Bottom Right)*: `id="outro-info"`, circle badge with live randomizing symbol (`['8', '$', '^^', '%', '/']`), collection label "ARCHIVE COLLECTION PROMPT", and price "$97,33".
  - *View CTA Button (Bottom Right)*: `id="outro-buy"`, pill shape (`border-radius: 1335px`), white background with text "view" (`mix-blend-mode: exclusion`), scaling from 0 to 1 on scroll.

#### 3. Black Panel Gallery Section
- Fixed black container (`z-index: 10`) starting at `translateY(100vh)` sliding to `translateY(0)` during the first viewport height of scroll.
- **Responsive Grid**: 2 columns (< 640px), 3 columns (640-1024px), 4 columns (≥ 1024px).
- **Layout Algorithm**: `buildLayout(count, cols)` placing 10 analyzed specimen images in a scattered matrix (aspect ratio 2/3).
- **Per-Frame RAF Card Scaling**:
  - `Enter = Math.min(1, (vh - top) / (vh * 0.6))`
  - `Exit = Math.min(1, bottom / (vh * 0.4))`
  - `Final Scale = Math.min(enter, exit)`

#### 4. IngredientSight AI Working Dashboard
- Accessed seamlessly via the "view" button or navigation header.
- **5-Agent LangGraph Pipeline Visualizer**:
  1. *OCR Agent*: Text extraction from label images.
  2. *Ingredient Agent*: INCI normalization & botanical chemical mapping.
  3. *Research Agent*: PubMed / ECHA toxicity lookup.
  4. *Safety Agent*: EWG risk score calculation (0-100 gauge) & dermatological advice.
  5. *Report Agent*: Markdown & JSON report compilation.
- **Interactive Label Upload & Demo Selection**: Select pre-analyzed samples or drop custom label images.
- **Export Options**: Download reports as `.md` or `.json`.
```

---

## SECTION 2: VERIFIED FILE MAP & PATHS

| Component | Path | Description |
| :--- | :--- | :--- |
| **Package Config** | [package.json](file:///d:/Lang/package.json) | React 19, Vite 6, Tailwind CSS v4, GSAP, Motion |
| **Vite Config** | [vite.config.ts](file:///d:/Lang/vite.config.ts) | Vite + React + Tailwind plugins + API proxy |
| **Styling** | [index.css](file:///d:/Lang/src/index.css) | Inter Tight font setup, bp-card styling |
| **Custom Cursor** | [CustomCursor.tsx](file:///d:/Lang/src/components/CustomCursor.tsx) | Direct DOM cursor with mix-blend exclusion |
| **Hero Section** | [HeroSection.tsx](file:///d:/Lang/src/components/HeroSection.tsx) | Atmospheric video layer & mix-blend UI |
| **Black Gallery** | [BlackPanelGallery.tsx](file:///d:/Lang/src/components/BlackPanelGallery.tsx) | RAF scroll-driven matrix with card scale |
| **AI Dashboard** | [Dashboard.tsx](file:///d:/Lang/src/components/Dashboard.tsx) | 5-agent LangGraph workflow dashboard |
| **FastAPI Backend** | [server.py](file:///d:/Lang/server.py) | Python FastAPI service calling LangGraph |
