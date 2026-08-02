For IngredientSight AI
 INITIAL Architecture REFRENCE
                LangGraph

                     │

        Supervisor (Workflow)

                     │

     ┌───────────────┼────────────────┐

     ▼               ▼                ▼

 OCR Agent     Ingredient Agent   Research Agent

                     │

                     ▼

            Safety Agent

                     │

                     ▼

            Report Agent

Core Idea

User uploads

Cosmetic
Food
Shampoo
Face Wash

↓

AI analyzes ingredients

↓

Provides explainable safety report.

That's it.

Simple.

Useful.

Professional.

Only 5 Agents

Instead of this

12 Agents

Let's do

5 Agents
1️⃣ Supervisor Agent

The brain.

Responsible for orchestration.

It decides

OCR

↓

Ingredient Extraction

↓

Research

↓

Safety Analysis

↓

Report
2️⃣ OCR + Ingredient Agent

Instead of two agents

Make one.

Responsibilities

OCR
Clean text
Extract ingredients
Normalize ingredient names

Output

Water

Glycerin

Niacinamide

Fragrance
3️⃣ Research Agent

This is the best part.

It will

Search PostgreSQL
Search ChromaDB
Retrieve FDA/WHO/PubMed documents

Return

Purpose

Risk

Evidence

Regulations

One agent.

Simple.

4️⃣ Safety Analysis Agent

This agent thinks.

Input

Ingredient

+

Research

Output

Risk

Warnings

Recommendations

Overall Score

Instead of separate

Toxicity
Allergy
Regulation

Just one intelligent Safety Agent.

5️⃣ Report Agent

Generate

Dashboard
PDF
JSON

Done.

My final architecture for IngredientSight AI
Component	Use create_agent()?	Reason
OCR Node	❌ No	Deterministic. Always runs.
Ingredient Node	❌ No	Deterministic text cleaning.
Research Agent	✅ Maybe	If it needs to choose among multiple information sources.
Safety Agent	❌ Usually no	A simple prompt + LLM chain is enough.
Report Agent	❌ No	Prompt + LLM generates the report.
Supervisor	❌ No	LangGraph handles orchestration.

1️⃣ OCR Agent
Job

Extract text from an image.

Input:

Product Image

Output:

Water
Glycerin
Fragrance
Citric Acid
Technology
Gemini Vision (via google-genai)




2️⃣ Ingredient Agent

This is different.

Suppose OCR gives:

Sodlum Laureth Sulfale

We want:

Sodium Laureth Sulfate

Now we need reasoning.

Gemini understands:

"This is probably Sodium Laureth Sulfate."

Here LangChain becomes useful.

Example

Prompt

↓

Gemini

↓

Clean Ingredient List

So

OCR Text

↓

LangChain

↓

Gemini

↓

Structured Ingredients


3️⃣ Research Agent

Input

Sodium Laureth Sulfate

Now we ask

Tell me

Purpose

Side Effects

FDA Status

WHO Information


↓

RAG

↓

Research Papers

↓

FDA

↓

PubMed

So

Ingredient

↓

LangChain

↓

Gemini

↓

Research

*Research Agent

↓

RAG

↓

FDA

↓

WHO

↓

PubMed

↓

Gemini

↓

Research Report

Everything else stays the same.*

4️⃣ Safety Agent

Input

Research Results

Example

Ingredient A

Low Risk

Ingredient B

High Risk

Now LLM thinks

Overall

Medium Risk

Again

LangChain

↓

Gemini

↓

Decision

5️⃣ Report Agent

Input

Safety Result

Gemini creates

Beautiful Report

↓

Markdown

↓

PDF

Again

LangChain.

6️⃣ Supervisor

This is completely different.

Supervisor doesn't know chemistry.

Supervisor doesn't know OCR.

Supervisor doesn't know Gemini.

It only knows

Who runs next?

Like

OCR finished?

↓

Yes

↓

Ingredient Agent

↓

Research Agent

↓

Safety Agent

↓

Report Agent

This is LangGraph.

Example

builder.add_node("ocr", ocr_node)

builder.add_node("ingredient", ingredient_node)

builder.add_node("research", research_node)

builder.add_edge("ocr","ingredient")

builder.add_edge("ingredient","research")


FINAL ARCHITECTURE
                    User
                      │
                      ▼
                 OCR Agent
            (Gemini Vision API)
                      │
                      ▼
             Ingredient Agent
          (LangChain + Gemini)
                      │
                      ▼
              Research Agent
                 (LangChain)
                      │
                      ▼
             Retriever (RAG)
                      │
     ┌────────────────┼────────────────┐
     ▼                ▼                ▼
   FDA Docs      PubMed Papers      WHO Docs
     │                │                │
     └────────────────┼────────────────┘
                      ▼
                 Gemini LLM
                      ▼
             Research Summary
                      │
                      ▼
             Safety Agent
          (LangChain + Gemini)
                      │
                      ▼
             Report Agent
          (LangChain + Gemini)
                      │
                      ▼
           Dashboard + PDF Report
