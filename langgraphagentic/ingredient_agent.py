import os
from pydantic import BaseModel, Field
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

class IngredientList(BaseModel):
    ingredients: List[str] = Field(
        description="Clean, corrected, and normalized chemical/common ingredient names. Each element should be a single ingredient."
    )

_structured_llm_instance = None

def get_ingredient_llm():
    """
    Initializes (or reuses) the Google Generative AI LLM with structured output.
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
    
    _structured_llm_instance = llm.with_structured_output(IngredientList)
    return _structured_llm_instance

def ingredient_node(state: dict) -> dict:
    """
    Ingredient Node using LangChain and ChatGoogleGenerativeAI.
    
    Takes state["ocr_text"], corrects spelling mistakes, normalizes names,
    and returns a structured list of ingredient strings in state["ingredients"].
    """
    ocr_text = state.get("ocr_text", "").strip()
    if not ocr_text:
        state["ingredients"] = []
        return state
        
    structured_llm = get_ingredient_llm()
    
    # Setup prompt
    system_prompt = (
        "You are an expert cosmetic and food chemist. Your job is to process raw OCR text "
        "extracted from a product label, clean it, correct spelling mistakes/OCR inaccuracies, "
        "and extract individual ingredients as a structured list.\n\n"
        "Rules:\n"
        "1. Correct obvious spelling errors (e.g. 'Sodlum Laureth Sulfale' -> 'Sodium Laureth Sulfate').\n"
        "2. Normalize ingredient names (e.g. 'Water (Aqua)' -> 'Water', 'Glycerine' -> 'Glycerin').\n"
        "3. Remove branding/marketing adjectives (e.g. 'Organic Lavender Extract' -> 'Lavender Extract').\n"
        "4. Separate concatenated ingredients and output them as individual items in the list.\n"
        "5. Output only valid ingredient names. Ignore warnings, weights, instructions, or footnotes."
    )
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "Here is the raw OCR text:\n\n{ocr_text}\n\nExtract and clean the ingredients list.")
    ])
    
    chain = prompt_template | structured_llm
    
    try:
        result = chain.invoke({"ocr_text": ocr_text})
        state["ingredients"] = result.ingredients
    except Exception as e:
        print(f"[WARN] Gemini call failed in Ingredient Agent: {e}. Trying Groq fallback...")
        groq_api_key = os.environ.get("GROQ_API_KEY")
        if not groq_api_key:
            raise RuntimeError(f"Gemini call failed and no GROQ_API_KEY configured for fallback. Original error: {e}")
        try:
            from langchain_groq import ChatGroq
            groq_llm = ChatGroq(
                model="llama-3.3-70b-versatile",
                groq_api_key=groq_api_key,
                temperature=0.0
            ).with_structured_output(IngredientList)
            
            groq_chain = prompt_template | groq_llm
            result = groq_chain.invoke({"ocr_text": ocr_text})
            state["ingredients"] = result.ingredients
            print("[INFO] Ingredient Agent successfully recovered using Groq (llama-3.3-70b-versatile)!")
        except Exception as groq_err:
            raise RuntimeError(f"Both Gemini and Groq fallback failed in Ingredient Agent. Gemini error: {e}. Groq error: {groq_err}")
        
    return state
