import os
from pydantic import BaseModel, Field
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

class SafetyAnalysis(BaseModel):
    overall_score: str = Field(
        description="Overall safety score rating (e.g. Safe / Low Risk, Caution / Medium Risk, Danger / High Risk)"
    )
    summary: str = Field(
        description="A clear and comprehensive summary explaining the overall safety profile of the ingredients."
    )
    warnings: List[str] = Field(
        description="Specific safety alerts or warnings regarding particular ingredients (e.g. potential allergens, toxic elements, restricted usages)."
    )
    recommendations: List[str] = Field(
        description="Actionable consumer recommendations (e.g., 'Do a patch test before use', 'Avoid contact with eyes', 'Not recommended for sensitive skin')."
    )

_structured_llm_instance = None

def get_safety_llm():
    """
    Initializes (or reuses) the ChatGoogleGenerativeAI client with structured output.
    Module-level singleton to avoid re-creating the client on every graph run.
    """
    global _structured_llm_instance
    if _structured_llm_instance is not None:
        return _structured_llm_instance

    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Neither GOOGLE_API_KEY nor GEMINI_API_KEY was found in the environment/dotenv file.")
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0.0
    )

    _structured_llm_instance = llm.with_structured_output(SafetyAnalysis)
    return _structured_llm_instance

def safety_node(state: dict) -> dict:
    """
    Safety Agent Node.
    
    Reads state["research_results"], analyzes all ingredient risks,
    synthesizes an overall safety evaluation, and stores it in state["safety_analysis"].
    """
    research_results = state.get("research_results", {})
    if not research_results:
        state["safety_analysis"] = {
            "overall_score": "Unknown",
            "summary": "No research data was available to evaluate safety.",
            "warnings": [],
            "recommendations": []
        }
        return state
        
    structured_llm = get_safety_llm()
    
    # Format the ingredients and their safety data for the prompt
    formatted_context = ""
    for ing, report in research_results.items():
        formatted_context += f"INGREDIENT: {ing}\n"
        formatted_context += f"- Purpose: {report.get('purpose', 'N/A')}\n"
        formatted_context += f"- Side Effects: {report.get('side_effects', 'N/A')}\n"
        formatted_context += f"- Human Safety Status: {report.get('human_safety_status', 'N/A')}\n"
        safety_sources = report.get('safety_sources', [])
        formatted_context += f"- Safety Sources: {', '.join(safety_sources) if safety_sources else 'None found'}\n"
        formatted_context += f"- Scientific Evidence: {report.get('evidence', 'N/A')}\n\n"
        
    system_prompt = (
        "You are an expert toxicologist, consumer safety advocate, and regulatory specialist. "
        "Your task is to analyze the research summaries of all ingredients in a product, "
        "evaluate their combined safety risks, determine an overall safety score (Safe / Low Risk, "
        "Caution / Medium Risk, Danger / High Risk), identify specific warning alerts, "
        "and provide actionable recommendations for consumers.\n\n"
        "STRICT TOXICOLOGICAL EVALUATION GUIDELINES:\n"
        "1. Distinguish between INHERENT HAZARD and ACTUAL RISK. An ingredient may possess an inherent hazard (e.g., Titanium Dioxide is an inhalation hazard when in powder/spray form) but pose virtually zero risk in a rinse-off liquid product (like a shampoo) or a cream. Assess the risk based on realistic cosmetic application routes.\n"
        "2. Incorporate exposure route (rinse-off vs leave-on, spray vs cream) and permitted cosmetic concentration thresholds into your reasoning.\n"
        "3. Apply the fallback rule: 'No evidence of safety does not equal high risk'. If an ingredient's safety verification shows 'Insufficient Web Data' or has missing evidence, do NOT automatically classify the product or the ingredient as High Risk or Caution. Instead, default to 'Unknown' or 'Needs More Evidence' unless there is clear scientific documentation of a risk.\n"
        "4. Avoid overstating risks for common mild irritants (e.g., Sodium Laureth Sulfate is an irritant primarily at high concentrations or for sensitive skin, not a major toxicity hazard in normal rinse-off use). Keep assessments scientifically balanced."
    )
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", (
            "Here are the chemical research profiles for each ingredient in this product:\n\n"
            "{formatted_context}\n"
            "Generate the overall safety analysis report."
        ))
    ])
    
    chain = prompt_template | structured_llm
    
    try:
        analysis = chain.invoke({"formatted_context": formatted_context})
        state["safety_analysis"] = analysis.model_dump()
    except Exception as e:
        raise RuntimeError(f"Safety Agent synthesis failed: {e}")
        
    return state
