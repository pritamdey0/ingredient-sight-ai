import os
import requests
from urllib.parse import quote_plus
import re
import html
from pydantic import BaseModel, Field
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

class ExposureContext(BaseModel):
    sensitive_skin_suitability: str = Field(
        description="Suitability for sensitive skin. Must be one of: 'Suitable', 'Caution / Avoid', or 'Unknown'."
    )
    children_suitability: str = Field(
        description="Suitability for children. Must be one of: 'Suitable', 'Caution / Avoid', or 'Unknown'."
    )
    pregnancy_suitability: str = Field(
        description="Suitability for pregnant users. Must be one of: 'No specific pregnancy concerns identified', 'Consult healthcare provider if concerned', or 'Caution / Avoid'."
    )
    rinse_off_suitability: str = Field(
        description="Suitability for rinse-off products. Must be one of: 'Suitable', 'Caution / Avoid', or 'Unknown'."
    )
    leave_on_suitability: str = Field(
        description="Suitability for leave-on products. Must be one of: 'Suitable', 'Caution / Avoid', or 'Unknown'."
    )
    spray_suitability: str = Field(
        description="Suitability for spray/inhalation products. Must be one of: 'Suitable', 'Caution / Avoid', or 'Unknown'."
    )

class IngredientResearch(BaseModel):
    name: str = Field(description="The name of the ingredient")
    purpose: str = Field(description="Primary purpose or function of this ingredient (e.g., surfactant, preservative, humectant, emulsifier)")
    side_effects: str = Field(description="Known side effects, safety concerns, allergies, or toxicity risks associated with this ingredient")
    evidence_based_safety_assessment: str = Field(
        description=(
            "A clear verdict on whether this ingredient is considered safe for human cosmetic use based ONLY on the web search results provided. "
            "Must be one of: 'Considered Safe Under Current Cosmetic Use', 'Generally Safe with Conditions', 'Use with Caution', 'Not Recommended', or 'Insufficient Web Data'. "
            "Do NOT invent a verdict — only use the information found in the provided search context."
        )
    )
    evidence_sources: List[str] = Field(
        description=(
            "A list of real URLs or source names found in the provided web search context that support the safety assessment verdict. "
            "ONLY include URLs or sources that actually appeared in the search results. Do NOT fabricate or hallucinate URLs. "
            "If no sources were found in the search context, return an empty list."
        )
    )
    evidence: str = Field(description="Summary of scientific evidence, publications, or clinical trials regarding its safety profile, based on the provided search context")
    confidence_score: str = Field(
        description="Confidence in safety assessment rating, based on source quality, agreement, and completeness. Must be one of: 'High', 'Medium', 'Low'."
    )
    exposure_context: ExposureContext = Field(
        description="Detailed suitability context for different user groups and cosmetic formulations based on the search context."
    )

class BatchResearchReport(BaseModel):
    reports: List[IngredientResearch] = Field(
        description="A list containing the safety and research profiles for each of the requested ingredients."
    )

def search_tavily(query: str, max_results: int = 3) -> dict:
    """
    Performs a search on Tavily.
    Returns a dict with 'snippets' (text) and 'urls' (source links found).
    """
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        print("Warning: TAVILY_API_KEY not found in environment.")
        return {"snippets": "", "urls": []}
    
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "basic",
        "include_answer": False,
        "include_images": False,
        "max_results": max_results
    }
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            res_json = response.json()
            results = res_json.get("results", [])
            snippets = []
            urls = []
            for r in results:
                snippet = r.get("content", "")
                url_val = r.get("url", "")
                if snippet:
                    snippets.append(snippet)
                if url_val:
                    urls.append(url_val)
            return {
                "snippets": "\n".join(snippets),
                "urls": urls
            }
        else:
            print(f"Warning: Tavily API returned status code {response.status_code}: {response.text}")
            return {"snippets": "", "urls": []}
    except Exception as e:
        print(f"Warning: Tavily search failed for query '{query}': {e}")
        return {"snippets": "", "urls": []}

from urllib.parse import urlparse

def rank_and_filter_sources(urls: List[str]) -> List[str]:
    """
    Ranks and filters a list of source URLs.
    Scores domains:
      - 5: fda.gov, ncbi.nlm.nih.gov (PubMed), nih.gov, cir-safety.org (CIR)
      - 4: canada.ca (Health Canada), ec.europa.eu (SCCS), europa.eu
      - 3: cosmeticsinfo.org
      - 2: specialchem.com
      - 1: random blogs / news
      - 0: quora.com, facebook.com, twitter.com, instagram.com, grokipedia, reddit.com, pinterest.com
    Filters out 0-score sources.
    If 4-5 score sources exist, keeps ONLY score >= 4 sources.
    """
    scored_urls = []
    has_high_tier = False
    
    for url in urls:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Determine score
        score = 1  # Default score for web sources
        
        if any(d in domain for d in ["fda.gov", "ncbi.nlm.nih.gov", "nih.gov", "cir-safety.org"]):
            score = 5
        elif any(d in domain for d in ["canada.ca", "ec.europa.eu", "europa.eu"]):
            score = 4
        elif "cosmeticsinfo.org" in domain:
            score = 3
        elif "specialchem.com" in domain:
            score = 2
        elif any(d in domain for d in ["quora.com", "facebook.com", "twitter.com", "instagram.com", "grokipedia", "reddit.com", "pinterest.com"]):
            score = 0
            
        if score >= 4:
            has_high_tier = True
            
        if score > 0:
            scored_urls.append((url, score))
            
    # If high tier exists, keep only score >= 4
    if has_high_tier:
        filtered = [u for u, s in scored_urls if s >= 4]
    else:
        filtered = [u for u, s in scored_urls]
        
    return filtered

def get_batch_research_llm():
    """
    Initializes the ChatGoogleGenerativeAI client with batch structured output binding.
    """
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Neither GOOGLE_API_KEY nor GEMINI_API_KEY was found in the environment/dotenv file.")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0.0
    )

    return llm.with_structured_output(BatchResearchReport)


def research_node(state: dict) -> dict:
    """
    Research Node using LangChain and Gemini.

    Searches the web via Tavily for each ingredient's safety status,
    then uses a single batched LLM call to synthesise structured safety profiles.
    """
    ingredients = state.get("ingredients", [])
    if not ingredients:
        state["research_results"] = {}
        return state

    print(f"Researching safety profiles for {len(ingredients)} ingredients in batch using Tavily...")

    research_results = {}
    ingredients_to_search = []
    
    # 1. Hardcode Water / Aqua
    for ing in ingredients:
        ing_lower = ing.strip().lower()
        if ing_lower in ["water", "aqua", "water (aqua)", "aqua (water)", "purified water", "deionized water"]:
            research_results[ing] = {
                "name": ing,
                "purpose": "Cosmetic solvent and vehicle for active ingredients.",
                "side_effects": "No known side effects or toxicity risks under standard cosmetic use. Completely safe for skin application.",
                "evidence_based_safety_assessment": "Considered Safe Under Current Cosmetic Use",
                "evidence_sources": [
                    "https://www.cir-safety.org",
                    "https://www.fda.gov/cosmetics",
                    "https://ncbi.nlm.nih.gov/pubmed"
                ],
                "human_safety_status": "Considered Safe Under Current Cosmetic Use",
                "safety_sources": [
                    "https://www.cir-safety.org",
                    "https://www.fda.gov/cosmetics",
                    "https://ncbi.nlm.nih.gov/pubmed"
                ],
                "evidence": "Water (Aqua) is the most widely used ingredient in cosmetics. It is a well-established solvent that has been recognized as safe by all major scientific panels including the Cosmetic Ingredient Review (CIR) Expert Panel, the US Food and Drug Administration (FDA), and the EU Scientific Committee on Consumer Safety (SCCS).",
                "confidence_score": "High",
                "exposure_context": {
                    "sensitive_skin_suitability": "Suitable",
                    "children_suitability": "Suitable",
                    "pregnancy_suitability": "No specific pregnancy concerns identified",
                    "rinse_off_suitability": "Suitable",
                    "leave_on_suitability": "Suitable",
                    "spray_suitability": "Suitable"
                }
            }
        else:
            ingredients_to_search.append(ing)

    if not ingredients_to_search:
        state["research_results"] = research_results
        return state

    # 2. Gather search results (snippets + real URLs) for remaining ingredients
    combined_search_context = ""
    for ing in ingredients_to_search:
        search_query = f"{ing} cosmetic ingredient safe for humans safety review"
        result = search_tavily(search_query, max_results=3)

        # Run the URL filter and ranker
        filtered_urls = rank_and_filter_sources(result.get("urls", []))

        combined_search_context += f"Ingredient: {ing}\n"
        if result["snippets"]:
            combined_search_context += f"Web Search Snippets:\n{result['snippets']}\n"
        else:
            combined_search_context += "Web Search Snippets: No results found.\n"

        if filtered_urls:
            combined_search_context += "Source URLs found in search:\n"
            for u in filtered_urls:
                combined_search_context += f"  - {u}\n"
        else:
            combined_search_context += "Source URLs: None found.\n"

        combined_search_context += "-" * 40 + "\n"

    structured_llm = get_batch_research_llm()

    system_prompt = (
        "You are an expert toxicologist and cosmetic safety scientist.\n"
        "Your task is to synthesise authoritative safety profiles for a list of cosmetic/chemical ingredients.\n\n"
        "STRICT RULES — READ CAREFULLY:\n"
        "1. Use ONLY the provided web search snippets and source URLs as your evidence base.\n"
        "2. For 'evidence_based_safety_assessment', choose ONLY one of: "
        "'Considered Safe Under Current Cosmetic Use', 'Generally Safe with Conditions', 'Use with Caution', 'Not Recommended', 'Insufficient Web Data'.\n"
        "   Base this verdict strictly on what the search results say.\n"
        "3. For 'evidence_sources', list ONLY the URLs that appeared in the 'Source URLs found in search' section "
        "for that ingredient. DO NOT invent, guess, or construct any URLs. If no URLs were provided, return an empty list.\n"
        "4. For 'evidence', summarise what the search snippets say. Do not add information not present in the snippets.\n"
        "5. For 'purpose' and 'side_effects', you may use your general toxicological knowledge if the snippets are insufficient.\n"
        "6. Always return a profile for EVERY requested ingredient.\n"
        "7. For empty search context (or when no valid evidence URLs exist), you MUST set 'confidence_score' to 'Low' and the 'evidence' summary MUST start with: 'No specific cosmetic safety studies were retrieved from web search. This assessment is based on general chemical database knowledge.' and keep the description brief."
    )

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", (
            "List of ingredients to evaluate: {ingredients_list}\n\n"
            "Web Search Context (snippets and source URLs per ingredient):\n{combined_search_context}\n\n"
            "Generate a structured safety report for each ingredient. "
            "Remember: only cite source URLs that were explicitly listed in the search context above."
        ))
    ])

    chain = prompt_template | structured_llm

    try:
        batch_report = chain.invoke({
            "ingredients_list": ", ".join(ingredients_to_search),
            "combined_search_context": combined_search_context
        })

        # Formaldehyde donors set
        formaldehyde_donors = [
            "dmdm hydantoin", "imidazolidinyl urea", "diazolidinyl urea",
            "quaternium-15", "sodium hydroxymethylglycinate", "bronopol"
        ]

        # Map reports back to ingredient names
        for report in batch_report.reports:
            matched_name = report.name
            for ing in ingredients_to_search:
                if ing.lower() in report.name.lower() or report.name.lower() in ing.lower():
                    matched_name = ing
                    break
            
            report_dict = report.model_dump()
            
            # Formaldehyde donor check override
            for donor in formaldehyde_donors:
                if donor in report_dict["name"].lower() or donor in matched_name.lower():
                    report_dict["evidence_based_safety_assessment"] = "Generally Safe with Conditions"
                    
            # Handle empty search results fallback programmatically
            if not report_dict.get("evidence_sources") or len(report_dict.get("evidence_sources")) == 0:
                report_dict["confidence_score"] = "Low"
                orig_evidence = report_dict.get("evidence", "")
                prefix = "No specific cosmetic safety studies were retrieved from web search. This assessment is based on general chemical database knowledge."
                if not orig_evidence.startswith(prefix):
                    report_dict["evidence"] = f"{prefix} {orig_evidence}".strip()

            # Maintain backward compatibility with old keys
            report_dict["human_safety_status"] = report_dict["evidence_based_safety_assessment"]
            report_dict["safety_sources"] = report_dict["evidence_sources"]
            
            research_results[matched_name] = report_dict

        # Ensure every ingredient has a fallback entry
        for ing in ingredients:
            if ing not in research_results:
                research_results[ing] = {
                    "name": ing,
                    "purpose": "Unknown (not processed)",
                    "side_effects": "Unable to retrieve details",
                    "evidence_based_safety_assessment": "Insufficient Web Data",
                    "evidence_sources": [],
                    "human_safety_status": "Insufficient Web Data",
                    "safety_sources": [],
                    "evidence": "No specific cosmetic safety studies were retrieved from web search. This assessment is based on general chemical database knowledge.",
                    "confidence_score": "Low",
                    "exposure_context": {
                        "sensitive_skin_suitability": "Unknown",
                        "children_suitability": "Unknown",
                        "pregnancy_suitability": "Consult healthcare provider if concerned",
                        "rinse_off_suitability": "Unknown",
                        "leave_on_suitability": "Unknown",
                        "spray_suitability": "Unknown"
                    }
                }

        state["research_results"] = research_results
    except Exception as e:
        raise RuntimeError(f"Research Agent batch synthesis failed: {e}")

    return state
