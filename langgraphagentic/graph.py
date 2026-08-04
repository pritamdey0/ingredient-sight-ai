"""
IngredientSight AI - LangGraph Pipeline

This module defines the complete LangGraph StateGraph that orchestrates
all 5 agents as nodes with typed state transitions:

  OCR → Ingredient → Research → Safety → Report

Usage:
    from langgraphagentic.graph import build_graph
    
    graph = build_graph()
    result = graph.invoke({"image_path": "path/to/product_label.jpg"})
"""
import os
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, START, END

from langgraphagentic.ocr_agent import ocr_node
from langgraphagentic.ingredient_agent import ingredient_node
from langgraphagentic.research_agent import research_node
from langgraphagentic.safety_agent import safety_node
from langgraphagentic.report_agent import report_node


# ──────────────────────────────────────────────
# 1. Define the Typed State Schema
# ──────────────────────────────────────────────

class PipelineState(TypedDict, total=False):
    """Typed state that flows through the entire LangGraph pipeline."""
    # Input
    image_path: str

    # Step 1 – OCR Agent output
    ocr_text: str

    # Step 2 – Ingredient Agent output
    ingredients: List[str]

    # Step 3 – Research Agent output
    research_results: Dict[str, Any]

    # Step 4 – Safety Agent output
    safety_analysis: Dict[str, Any]

    # Step 5 – Report Agent outputs
    markdown_report: str
    json_report: Dict[str, Any]
    report_md_path: str
    report_json_path: str


# ──────────────────────────────────────────────
# 2. Build the StateGraph
# ──────────────────────────────────────────────

def build_graph() -> StateGraph:
    """
    Constructs and compiles the IngredientSight AI LangGraph pipeline.

    Graph topology (linear):
        START → ocr → ingredient → research → safety → report → END

    Returns:
        A compiled LangGraph StateGraph ready to be invoked.
    """
    # Create the graph with our typed state
    graph = StateGraph(PipelineState)

    # ── Register each agent as a node ──
    graph.add_node("ocr", ocr_node)
    graph.add_node("ingredient", ingredient_node)
    graph.add_node("research", research_node)
    graph.add_node("safety", safety_node)
    graph.add_node("report", report_node)

    # ── Wire the edges (linear pipeline) ──
    graph.add_edge(START, "ocr")
    graph.add_edge("ocr", "ingredient")
    graph.add_edge("ingredient", "research")
    graph.add_edge("research", "safety")
    graph.add_edge("safety", "report")
    graph.add_edge("report", END)

    # ── Compile and return ──
    compiled = graph.compile()
    return compiled


# ──────────────────────────────────────────────
# 3. Convenience: Run from CLI
# ──────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    if len(sys.argv) < 2:
        print("Usage: python -m langgraphagentic.graph <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    if not os.path.exists(image_path):
        print(f"Error: File not found at '{image_path}'")
        sys.exit(1)

    print("Building IngredientSight AI LangGraph...")
    app = build_graph()

    print(f"Running pipeline on: {image_path}\n")
    result = app.invoke({"image_path": image_path})

    # Print final summary
    analysis = result.get("safety_analysis", {})
    print("\n======================================================")
    print("           INGREDIENTSIGHT AI - FINAL RESULTS          ")
    print("======================================================")
    print(f"Raw OCR Output:\n{result.get('ocr_text')}\n")
    print(f"Ingredients: {result.get('ingredients')}\n")
    print(f"Overall Safety Score: {analysis.get('overall_score', 'N/A')}\n")
    print("Safety Summary:")
    print(analysis.get('summary', 'N/A'))
    print("\nWarnings:")
    for warn in analysis.get('warnings', []):
        print(f"  [WARNING] {warn}")
    print("\nRecommendations:")
    for rec in analysis.get('recommendations', []):
        print(f"  [RECOMMENDATION] {rec}")
    print("\n------------------------------------------------------")
    print("Reports Saved:")
    print(f"  Markdown: {result.get('report_md_path', 'N/A')}")
    print(f"  JSON:     {result.get('report_json_path', 'N/A')}")
    print("======================================================")
