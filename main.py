"""
IngredientSight AI - CLI Entry Point

Uses the LangGraph StateGraph pipeline to process product label images
through all 5 agent nodes:
  OCR → Ingredient → Research → Safety → Report
"""
import sys
import os

# Set standard output encoding to UTF-8 to prevent Windows terminal encoding issues
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from langgraphagentic.graph import build_graph


def main():
    print("=" * 56)
    print("        IngredientSight AI - LangGraph Pipeline")
    print("=" * 56)
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = input("\nEnter the path to your product label image: ").strip()
        
    if not image_path:
        print("Error: No image path provided.")
        sys.exit(1)
        
    if not os.path.exists(image_path):
        print(f"Error: File not found at '{image_path}'")
        sys.exit(1)
        
    # Build and compile the LangGraph
    print("\nBuilding LangGraph pipeline...")
    app = build_graph()
    print("Graph compiled: START → ocr → ingredient → research → safety → report → END\n")
    
    # Invoke the graph with initial state
    print("Running pipeline...\n")
    try:
        result = app.invoke({"image_path": image_path})
    except Exception as e:
        print(f"\nPipeline failed: {e}")
        sys.exit(1)
    
    # Display results
    analysis = result.get("safety_analysis", {})
    
    print("\n" + "=" * 56)
    print("           INGREDIENTSIGHT AI - FINAL RESULTS")
    print("=" * 56)
    print(f"\nRaw OCR Output:\n{result.get('ocr_text', 'N/A')}\n")
    print(f"Normalized Ingredients: {result.get('ingredients', [])}\n")
    print(f"Overall Safety Score: {analysis.get('overall_score', 'N/A')}\n")
    print("Safety Summary:")
    print(analysis.get('summary', 'N/A'))
    print("\nWarnings:")
    for warn in analysis.get('warnings', []):
        print(f"  [!] {warn}")
    print("\nConsumer Recommendations:")
    for rec in analysis.get('recommendations', []):
        print(f"  [>] {rec}")
    print("\n" + "-" * 56)
    print("Reports Saved:")
    print(f"  Markdown: {result.get('report_md_path', 'N/A')}")
    print(f"  JSON:     {result.get('report_json_path', 'N/A')}")
    print("=" * 56)


if __name__ == "__main__":
    main()
